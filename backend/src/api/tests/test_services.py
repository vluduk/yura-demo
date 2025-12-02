from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock, Mock
from api.models.conversation import Conversation, ConversationType
from api.models.message import Message
from api.models.user_assesment import UserAssessment, ASSESSMENT_QUESTIONS
from api.services.advisor import AdvisorService

User = get_user_model()


class AdvisorServiceSearchKnowledgeBaseTest(TestCase):
    """Tests for knowledge base search functionality"""
    
    def test_search_knowledge_base_returns_list(self):
        """Test that search returns a list"""
        results = AdvisorService._search_knowledge_base('job search')
        self.assertIsInstance(results, list)

    def test_search_knowledge_base_empty_query(self):
        """Test search with empty query"""
        results = AdvisorService._search_knowledge_base('')
        self.assertIsInstance(results, list)

    def test_search_knowledge_base_no_results(self):
        """Test search with no matching results"""
        results = AdvisorService._search_knowledge_base('xyzabc123nonexistent')
        self.assertIsInstance(results, list)


class AdvisorServiceFormatAssessmentTest(TestCase):
    """Tests for assessment context formatting"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_format_empty_assessment(self):
        """Test formatting empty assessment"""
        assessment = UserAssessment.objects.create(user=self.user)
        context = AdvisorService._format_assessment_context(assessment)
        
        self.assertIsInstance(context, str)
        # Should indicate data not filled
        self.assertIn('Дані ще не заповнені', context)

    def test_format_partial_assessment(self):
        """Test formatting partially filled assessment"""
        assessment = UserAssessment.objects.create(
            user=self.user,
            answers={
                'service_branch': 'Air Force',
                'primary_skills': 'piloting,navigation'
            },
            service_branch='Air Force',
            primary_skills='piloting,navigation'
        )
        context = AdvisorService._format_assessment_context(assessment)
        
        self.assertIsInstance(context, str)
        self.assertIn('Air Force', context)

    def test_format_complete_assessment(self):
        """Test formatting complete assessment"""
        assessment = UserAssessment.objects.create(
            user=self.user,
            answers={
                'service_branch': 'Navy',
                'years_of_service': '8',
                'primary_skills': 'electronics,radar',
                'current_goals': 'Find tech job',
                'long_term_goals': 'Become tech lead'
            },
            service_branch='Navy',
            years_of_service=8,
            primary_skills='electronics,radar'
        )
        context = AdvisorService._format_assessment_context(assessment)
        
        self.assertIsInstance(context, str)
        self.assertIn('Navy', context)


class AdvisorServiceProcessResponseTest(TestCase):
    """Tests for LLM response processing"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assessment = UserAssessment.objects.create(user=self.user)

    def test_process_response_with_updates(self):
        """Test processing response with JSON updates"""
        raw_response = '''Here is my advice.
```json
{
  "updates": {
    "service_branch": "Marines",
    "primary_skills": "logistics,leadership"
  }
}
```
Good luck!'''
        
        result = AdvisorService._process_response(self.assessment, raw_response)
        
        # JSON should be stripped from response
        self.assertNotIn('```json', result)
        self.assertNotIn('"updates"', result)
        
        # Assessment should be updated
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.service_branch, 'Marines')

    def test_process_response_without_json(self):
        """Test processing response without any JSON"""
        raw_response = 'This is just plain text advice without any JSON updates.'
        
        result = AdvisorService._process_response(self.assessment, raw_response)
        
        # Should return original text unchanged
        self.assertEqual(result, raw_response)

    def test_process_response_invalid_json(self):
        """Test processing response with invalid JSON"""
        raw_response = '''Some text
```json
{invalid json here
```
More text'''
        
        result = AdvisorService._process_response(self.assessment, raw_response)
        
        # Should handle gracefully and return cleaned text
        self.assertIsInstance(result, str)

    def test_process_response_updates_multiple_fields(self):
        """Test that multiple fields can be updated"""
        raw_response = '''```json
{
  "updates": {
    "service_branch": "Navy",
    "years_of_service": "10",
    "rank": "Captain",
    "primary_skills": "strategy,leadership,operations"
  }
}
```'''
        
        AdvisorService._process_response(self.assessment, raw_response)
        
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.service_branch, 'Navy')
        self.assertIn('rank', self.assessment.answers)


class AdvisorServiceBuildPromptsTest(TestCase):
    """Tests for prompt building functions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assessment = UserAssessment.objects.create(user=self.user)

    def test_build_assessment_prompt_unanswered(self):
        """Test building prompt when questions remain"""
        prompt = AdvisorService._build_assessment_prompt(
            self.assessment,
            'conversation history',
            'user message'
        )
        
        self.assertIsInstance(prompt, str)
        # Should ask next question
        self.assertIn('НАСТУПНЕ ПИТАННЯ', prompt)

    def test_build_assessment_prompt_completed(self):
        """Test building prompt when all questions answered"""
        # Answer all questions
        answers = {q['id']: 'test answer' for q in ASSESSMENT_QUESTIONS}
        self.assessment.answers = answers
        self.assessment.save()
        
        prompt = AdvisorService._build_assessment_prompt(
            self.assessment,
            'history',
            'message'
        )
        
        self.assertIsInstance(prompt, str)
        # Should indicate completion
        self.assertIn('профіль оцінювання вже заповнений', prompt)

    def test_build_business_prompt(self):
        """Test building business conversation prompt"""
        system_prompt = AdvisorService.SYSTEM_PROMPTS.get(ConversationType.BUSINESS, '')
        
        prompt, direct = AdvisorService._build_business_prompt(
            self.user,
            system_prompt,
            self.assessment,
            'history',
            'I want to start a bakery'
        )
        
        self.assertIsInstance(prompt, str)
        # direct should be None in fallback mode
        self.assertIsNone(direct)

    def test_build_education_prompt(self):
        """Test building education conversation prompt"""
        system_prompt = AdvisorService.SYSTEM_PROMPTS.get('assessment', '')
        
        prompt = AdvisorService._build_education_prompt(
            system_prompt,
            self.assessment,
            'history',
            'I want to learn Python'
        )
        
        self.assertIsInstance(prompt, str)
        # Should include knowledge base materials
        self.assertIn('Матеріали з бази знань', prompt)


class AdvisorServiceGenerationTest(TestCase):
    """Tests for AI generation functions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )

    def test_generate_initial_message_no_api_key(self):
        """Test initial message generation without API key"""
        import os
        from django.conf import settings
        
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        old_env = os.environ.pop('GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = None
        
        try:
            msg = AdvisorService.generate_initial_message(self.user, self.conversation)
            # Should return a fallback message
            self.assertIsInstance(msg, str)
            self.assertGreater(len(msg), 0)
        finally:
            if old_env is not None:
                os.environ['GOOGLE_API_KEY'] = old_env
            settings.GOOGLE_API_KEY = old_key

    @patch('api.services.advisor.genai')
    def test_generate_initial_message_with_mock(self, mock_genai):
        """Test initial message generation with mocked API"""
        mock_response = Mock()
        mock_response.text = 'Welcome to the career advisor!'
        mock_response.parts = [1]
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure.return_value = None
        
        from django.conf import settings
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = 'test-key'
        
        try:
            msg = AdvisorService.generate_initial_message(self.user, self.conversation)
            self.assertIn('Welcome', msg)
        finally:
            settings.GOOGLE_API_KEY = old_key

    def test_generate_conversation_title_no_api_key(self):
        """Test conversation title generation without API key"""
        import os
        from django.conf import settings
        
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        old_env = os.environ.pop('GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = None
        
        try:
            result = AdvisorService.generate_conversation_title(self.conversation)
            # Should return None or skip
            self.assertIsNone(result)
        finally:
            if old_env is not None:
                os.environ['GOOGLE_API_KEY'] = old_env
            settings.GOOGLE_API_KEY = old_key

    @patch('api.services.advisor.genai')
    def test_generate_conversation_title_with_messages(self, mock_genai):
        """Test title generation with message history"""
        # Create some messages
        Message.objects.create(
            conversation=self.conversation,
            content='I need help finding a job',
            is_user=True
        )
        Message.objects.create(
            conversation=self.conversation,
            content='What skills do you have?',
            is_user=False
        )
        
        mock_response = Mock()
        mock_response.text = 'Пошук роботи та навички'
        mock_response.parts = [1]
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure.return_value = None
        
        from django.conf import settings
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = 'test-key'
        
        try:
            AdvisorService.generate_conversation_title(self.conversation)
            self.conversation.refresh_from_db()
            self.assertEqual(self.conversation.title, 'Пошук роботи та навички')
        finally:
            settings.GOOGLE_API_KEY = old_key

    def test_get_ai_response_no_api_key(self):
        """Test getting AI response without API key"""
        import os
        from django.conf import settings
        
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        old_env = os.environ.pop('GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = None
        
        try:
            response = AdvisorService.get_ai_response(
                self.user,
                self.conversation,
                'Hello advisor'
            )
            # Should return echo/fallback message
            self.assertIsInstance(response, str)
            self.assertTrue(response.startswith('(LLM не налаштовано)'))
        finally:
            if old_env is not None:
                os.environ['GOOGLE_API_KEY'] = old_env
            settings.GOOGLE_API_KEY = old_key


class AdvisorServiceConversationTypeTest(TestCase):
    """Tests for different conversation types"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_business_conversation_type(self):
        """Test business conversation handling"""
        conv = Conversation.objects.create(
            user=self.user,
            title='Business Idea',
            conv_type=ConversationType.BUSINESS
        )
        self.assertEqual(conv.conv_type, ConversationType.BUSINESS)

    def test_hiring_conversation_type(self):
        """Test hiring conversation handling"""
        conv = Conversation.objects.create(
            user=self.user,
            title='Job Search',
            conv_type=ConversationType.HIRING
        )
        self.assertEqual(conv.conv_type, ConversationType.HIRING)

    def test_education_conversation_type(self):
        """Test education conversation handling"""
        conv = Conversation.objects.create(
            user=self.user,
            title='Learning Path',
            conv_type=ConversationType.EDUCATION
        )
        self.assertEqual(conv.conv_type, ConversationType.EDUCATION)

    def test_career_path_conversation_type(self):
        """Test career path conversation handling"""
        conv = Conversation.objects.create(
            user=self.user,
            title='Career Direction',
            conv_type=ConversationType.CAREER_PATH
        )
        self.assertEqual(conv.conv_type, ConversationType.CAREER_PATH)


class AdvisorServiceSystemPromptsTest(TestCase):
    """Tests for system prompts configuration"""
    
    def test_system_prompts_exist(self):
        """Test that system prompts are defined"""
        self.assertIsInstance(AdvisorService.SYSTEM_PROMPTS, dict)
        self.assertGreater(len(AdvisorService.SYSTEM_PROMPTS), 0)

    def test_system_prompts_for_conversation_types(self):
        """Test that prompts exist for each conversation type"""
        # Should have prompts for main conversation types
        expected_types = [
            ConversationType.BUSINESS,
            ConversationType.HIRING,
            ConversationType.EDUCATION
        ]
        
        for conv_type in expected_types:
            # Should have a prompt for this type (or fallback)
            prompt = AdvisorService.SYSTEM_PROMPTS.get(
                conv_type,
                AdvisorService.SYSTEM_PROMPTS.get('assessment', '')
            )
            self.assertIsInstance(prompt, str)


class AdvisorServiceErrorHandlingTest(TestCase):
    """Tests for error handling in advisor service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test'
        )
        self.assessment = UserAssessment.objects.create(user=self.user)

    def test_process_response_handles_malformed_json(self):
        """Test that malformed JSON in response is handled gracefully"""
        raw = '```json\n{broken: json}\n```'
        
        # Should not raise exception
        result = AdvisorService._process_response(self.assessment, raw)
        self.assertIsInstance(result, str)

    def test_search_knowledge_base_handles_errors(self):
        """Test that knowledge base search handles errors gracefully"""
        # Even with unusual input, should not crash
        results = AdvisorService._search_knowledge_base(None)
        self.assertIsInstance(results, list)

    @patch('api.services.advisor.genai')
    def test_get_ai_response_handles_api_errors(self, mock_genai):
        """Test that API errors are handled gracefully"""
        mock_genai.GenerativeModel.side_effect = Exception('API Error')
        
        from django.conf import settings
        old_key = getattr(settings, 'GOOGLE_API_KEY', None)
        settings.GOOGLE_API_KEY = 'test-key'
        
        try:
            # Should not raise, but return error message
            response = AdvisorService.get_ai_response(
                self.user,
                self.conversation,
                'test message'
            )
            self.assertIsInstance(response, str)
        finally:
            settings.GOOGLE_API_KEY = old_key
