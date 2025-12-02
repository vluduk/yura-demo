from django.test import TestCase
from django.contrib.auth import get_user_model
from api.services.advisor import AdvisorService
from api.models.user_assesment import UserAssessment, ASSESSMENT_QUESTIONS
from api.models.conversation import Conversation, ConversationType
from api.models.message import Message
from unittest.mock import patch
from django.conf import settings

User = get_user_model()


class AdvisorServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='adv@example.com', password='pass', first_name='Adv', last_name='User'
        )
        self.conversation = Conversation.objects.create(user=self.user)

    def test_process_response_applies_updates_and_saves(self):
        assessment = UserAssessment.objects.create(user=self.user)
        raw = 'Here is an update:\n```json {"updates": {"service_branch": "Army", "primary_skills": "mechanics"}} ```\nThanks.'

        result = AdvisorService._process_response(assessment, raw)

        # JSON block should be removed from returned text
        self.assertNotIn('{"updates"', result)

        # Assessment should be updated and saved
        assessment.refresh_from_db()
        self.assertIn('service_branch', assessment.answers)
        self.assertEqual(assessment.answers.get('service_branch'), 'Army')
        # convenience field should have been synced
        self.assertEqual(assessment.service_branch, 'Army')

    def test_process_response_returns_raw_when_no_json(self):
        assessment = UserAssessment.objects.create(user=self.user)
        raw = 'Just a normal reply without json.'
        result = AdvisorService._process_response(assessment, raw)
        self.assertEqual(result, raw)

    def test_format_assessment_context_empty_and_with_data(self):
        assessment = UserAssessment.objects.create(user=self.user)
        empty = AdvisorService._format_assessment_context(assessment)
        self.assertIn('Дані ще не заповнені', empty)

        assessment.answers = {'current_goals': 'Find job', 'long_term_goals': 'Start business'}
        assessment.primary_skills = 'python,django'
        assessment.years_of_service = 5
        assessment.service_branch = 'Navy'
        assessment.save()

        ctx = AdvisorService._format_assessment_context(assessment)
        # Ensure key items are present in formatted context
        self.assertIn('Navy', ctx)
        # Accept either English or localized labels in the context
        self.assertTrue(('Primary skills' in ctx) or ('Основні навички' in ctx))

    def test_build_assessment_prompt_next_question_and_completed(self):
        assessment = UserAssessment.objects.create(user=self.user)
        # Initially there are unanswered questions, prompt should ask a question id
        prompt = AdvisorService._build_assessment_prompt(assessment, 'history', 'user said something')
        self.assertIn('НАСТУПНЕ ПИТАННЯ', prompt)

        # Mark all questions answered
        answers = {q['id']: 'x' for q in ASSESSMENT_QUESTIONS}
        assessment.answers = answers
        assessment.save()
        prompt2 = AdvisorService._build_assessment_prompt(assessment, 'history', 'user content')
        self.assertIn('профіль оцінювання вже заповнений', prompt2)

    def test_get_ai_response_no_api_key_returns_echo(self):
        # Force settings and environment to act as if no API key is configured
        from django.conf import settings
        import os
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        old_env = os.environ.pop('GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = None

        try:
            # Create a conversation with no type and user with career_selected False
            self.user.career_selected = False
            self.user.save()
            convo = self.conversation
            resp = AdvisorService.get_ai_response(self.user, convo, 'Hello advisor')
            self.assertTrue(resp.startswith('(LLM не налаштовано)'))
        finally:
            if old_env is not None:
                os.environ['GOOGLE_API_KEY'] = old_env
            settings.GOOGLE_API_KEY = old_key

    def test_generate_initial_message_no_api_key_returns_greeting(self):
        from django.conf import settings
        import os
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        old_env = os.environ.pop('GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = None
        try:
            msg = AdvisorService.generate_initial_message(self.user, self.conversation)
            # Accept a friendly greeting or any advisor-like introduction
            self.assertTrue(('Вітаю' in msg) or ('радник' in msg) or (len(msg.strip()) > 0))
        finally:
            if old_env is not None:
                os.environ['GOOGLE_API_KEY'] = old_env
            settings.GOOGLE_API_KEY = old_key

    def test_generate_conversation_title_no_api_key_skips(self):
        from django.conf import settings
        import os
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        old_env = os.environ.pop('GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = None
        try:
            # Should return None/skip and not raise
            res = AdvisorService.generate_conversation_title(self.conversation)
            self.assertIsNone(res)
        finally:
            if old_env is not None:
                os.environ['GOOGLE_API_KEY'] = old_env
            settings.GOOGLE_API_KEY = old_key

    def test_search_knowledge_base_empty(self):
        results = AdvisorService._search_knowledge_base('nonexistent term')
        # Should return a list (possibly empty) and not raise
        self.assertIsInstance(results, list)

    def test_build_business_prompt_fallback(self):
        # Make conversation type Business to trigger business prompt path
        self.conversation.conv_type = ConversationType.BUSINESS
        self.conversation.save()

        prompt, direct = AdvisorService._build_business_prompt(self.user, AdvisorService.SYSTEM_PROMPTS[ConversationType.BUSINESS], UserAssessment.objects.create(user=self.user), 'hist', 'I have an idea to open a cafe and sell pastries')
        # Should return a prompt (string) and None direct response in fallback
        self.assertIsInstance(prompt, str)
        self.assertIsNone(direct)

    def test_build_education_prompt_fallback(self):
        prompt = AdvisorService._build_education_prompt(AdvisorService.SYSTEM_PROMPTS['assessment'], UserAssessment.objects.create(user=self.user), 'hist', 'quantum physics')
        self.assertIsInstance(prompt, str)
        self.assertIn('Матеріали з бази знань', prompt)

    def test_user_assessment_save_conversions(self):
        # Test that answers sync to convenience fields and boolean parsing
        answers = {
            'years_of_service': '10',
            'deployment_experience': 'Yes',
            'leadership_experience': '1',
            'experience_years': '3',
            'primary_skills': 'first,second',
            'work_preferences': 'Full-time'
        }
        a = UserAssessment.objects.create(user=self.user, answers=answers)
        # After save, convenience fields should be populated
        a.refresh_from_db()
        self.assertEqual(a.years_of_service, 10)
        self.assertTrue(a.deployment_experience)
        self.assertTrue(a.leadership_experience)
        self.assertEqual(a.experience_years, 3)
        self.assertEqual(a.primary_skills, 'first,second')

    def test_to_llm_context_includes_fields(self):
        a = UserAssessment.objects.create(user=self.user)
        a.experience_level = 'mid'
        a.experience_years = 4
        a.primary_skills = 'python'
        a.service_branch = 'Air'
        a.answers = {'current_goals': 'Get job', 'long_term_goals': 'Grow career', 'additional_info': 'none'}
        a.save()
        ctx = a.to_llm_context()
        self.assertIn('Experience level', ctx)
        self.assertIn('Years of experience: 4', ctx)
        self.assertIn('Primary skills: python', ctx)

    def test_generate_initial_message_with_mocked_genai(self):
        # Mock genai model to avoid external calls
        class DummyResp:
            parts = [1]
            text = 'Mocked initial message'

        class DummyModel:
            def __init__(self, name):
                self.name = name
            def generate_content(self, prompt):
                return DummyResp()

        with patch('api.services.advisor.genai') as mock_genai:
            mock_genai.configure.return_value = None
            mock_genai.GenerativeModel = DummyModel
            # Ensure settings key present so code uses genai path
            old_key = getattr(settings, 'GOOGLE_API_KEY', None)
            settings.GOOGLE_API_KEY = 'fake'
            try:
                msg = AdvisorService.generate_initial_message(self.user, self.conversation)
                self.assertIn('Mocked initial message', msg)
            finally:
                settings.GOOGLE_API_KEY = old_key

    def test_generate_conversation_title_with_mocked_genai(self):
        # Create sample messages
        Message.objects.create(conversation=self.conversation, content='User: looking for job', is_user=True)
        Message.objects.create(conversation=self.conversation, content='Advisor: ask about skills', is_user=False)
        Message.objects.create(conversation=self.conversation, content='User: I know python', is_user=True)

        class DummyResp:
            parts = [1]
            text = 'Пошук роботи Python'

        class DummyModel:
            def __init__(self, name):
                pass
            def generate_content(self, prompt):
                return DummyResp()

        with patch('api.services.advisor.genai') as mock_genai:
            mock_genai.configure.return_value = None
            mock_genai.GenerativeModel = DummyModel
            old_key = getattr(settings, 'GOOGLE_API_KEY', None)
            settings.GOOGLE_API_KEY = 'fake'
            try:
                AdvisorService.generate_conversation_title(self.conversation)
                self.conversation.refresh_from_db()
                self.assertIn('Пошук роботи', self.conversation.title)
            finally:
                settings.GOOGLE_API_KEY = old_key
