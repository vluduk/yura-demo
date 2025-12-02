from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from api.models.conversation import Conversation, ConversationType
from api.models.message import Message
from api.models.business import BusinessIdea, ActionStep
from api.models.resume import (
    CVTemplate, Resume, ExperienceEntry, EducationEntry,
    ExtraActivityEntry, SocialLink, SkillEntry, LanguageEntry
)
from api.models.article import Article, ArticleCategory
from api.models.knowledge import KnowledgeDocument, KnowledgeCategory
from api.models.user_assesment import UserAssessment, ASSESSMENT_QUESTIONS

User = get_user_model()


class UserModelTest(TestCase):
    """Tests for the custom User model"""
    
    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.role, 'USER')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        self.assertEqual(admin.email, 'admin@example.com')
        self.assertEqual(admin.role, 'ADMIN')
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_active)

    def test_create_user_without_email_raises_error(self):
        """Test that creating a user without email raises ValueError"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                password='testpass123'
            )

    def test_user_string_representation(self):
        """Test the __str__ method of User"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(str(user), 'test@example.com')

    def test_user_career_selected_default(self):
        """Test that career_selected defaults to False"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertFalse(user.career_selected)

    def test_user_optional_fields(self):
        """Test optional fields are handled correctly"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            avatar_url='https://example.com/avatar.jpg'
        )
        self.assertEqual(user.phone, '1234567890')
        self.assertEqual(user.avatar_url, 'https://example.com/avatar.jpg')


class ConversationModelTest(TestCase):
    """Tests for the Conversation model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_create_conversation(self):
        """Test creating a conversation"""
        conv = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
        self.assertEqual(conv.user, self.user)
        self.assertEqual(conv.title, 'Test Conversation')
        self.assertIsNotNone(conv.created_at)
        self.assertIsNotNone(conv.last_active_at)

    def test_conversation_with_type(self):
        """Test creating a conversation with a type"""
        conv = Conversation.objects.create(
            user=self.user,
            title='Business Chat',
            conv_type=ConversationType.BUSINESS
        )
        self.assertEqual(conv.conv_type, ConversationType.BUSINESS)

    def test_conversation_string_representation(self):
        """Test __str__ method with and without title"""
        conv_with_title = Conversation.objects.create(
            user=self.user,
            title='My Conversation'
        )
        self.assertEqual(str(conv_with_title), 'My Conversation')
        
        conv_without_title = Conversation.objects.create(user=self.user)
        self.assertEqual(str(conv_without_title), str(conv_without_title.id))

    def test_conversation_summary_data_default(self):
        """Test that summary_data defaults to empty dict"""
        conv = Conversation.objects.create(user=self.user)
        self.assertEqual(conv.summary_data, {})

    def test_conversation_cascade_delete(self):
        """Test that deleting a user deletes their conversations"""
        conv = Conversation.objects.create(user=self.user)
        user_id = self.user.id
        self.user.delete()
        self.assertFalse(Conversation.objects.filter(user_id=user_id).exists())


class MessageModelTest(TestCase):
    """Tests for the Message model"""
    
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

    def test_create_user_message(self):
        """Test creating a user message"""
        msg = Message.objects.create(
            conversation=self.conversation,
            content='Hello, this is a test message',
            is_user=True
        )
        self.assertEqual(msg.conversation, self.conversation)
        self.assertEqual(msg.content, 'Hello, this is a test message')
        self.assertTrue(msg.is_user)
        self.assertIsNotNone(msg.created_at)

    def test_create_ai_message(self):
        """Test creating an AI message"""
        msg = Message.objects.create(
            conversation=self.conversation,
            content='AI response',
            is_user=False
        )
        self.assertFalse(msg.is_user)

    def test_message_context_used_default(self):
        """Test that context_used defaults to empty dict"""
        msg = Message.objects.create(
            conversation=self.conversation,
            content='Test'
        )
        self.assertEqual(msg.context_used, {})

    def test_message_cascade_delete(self):
        """Test that deleting a conversation deletes its messages"""
        msg = Message.objects.create(
            conversation=self.conversation,
            content='Test'
        )
        conv_id = self.conversation.id
        self.conversation.delete()
        self.assertFalse(Message.objects.filter(conversation_id=conv_id).exists())


class BusinessIdeaModelTest(TestCase):
    """Tests for the BusinessIdea model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_create_business_idea(self):
        """Test creating a business idea"""
        idea = BusinessIdea.objects.create(
            user=self.user,
            title='Tech Startup Idea',
            status='BRAINSTORM'
        )
        self.assertEqual(idea.user, self.user)
        self.assertEqual(idea.title, 'Tech Startup Idea')
        self.assertEqual(idea.status, 'BRAINSTORM')
        self.assertEqual(idea.validation_score, 0)

    def test_business_idea_json_fields(self):
        """Test JSON fields default to empty dicts"""
        idea = BusinessIdea.objects.create(
            user=self.user,
            title='Test Idea'
        )
        self.assertEqual(idea.business_canvas, {})
        self.assertEqual(idea.market_research, {})
        self.assertEqual(idea.summary_card_data, {})

    def test_business_idea_analysis_fields(self):
        """Test setting analysis fields"""
        idea = BusinessIdea.objects.create(
            user=self.user,
            title='Test Idea',
            market_analysis='Strong market opportunity',
            financial_analysis='Requires $50k investment',
            skills_match='Good match with user skills',
            risk_assessment='Medium risk',
            final_verdict='Proceed with validation'
        )
        self.assertEqual(idea.market_analysis, 'Strong market opportunity')
        self.assertEqual(idea.financial_analysis, 'Requires $50k investment')


class ActionStepModelTest(TestCase):
    """Tests for the ActionStep model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.business_idea = BusinessIdea.objects.create(
            user=self.user,
            title='Tech Startup'
        )

    def test_create_action_step(self):
        """Test creating an action step"""
        step = ActionStep.objects.create(
            business_idea=self.business_idea,
            title='Market Research',
            details='Conduct surveys and interviews',
            status='PENDING',
            step_order=1
        )
        self.assertEqual(step.business_idea, self.business_idea)
        self.assertEqual(step.title, 'Market Research')
        self.assertEqual(step.status, 'PENDING')
        self.assertEqual(step.step_order, 1)

    def test_action_step_with_deadline(self):
        """Test action step with a deadline"""
        deadline = date.today() + timedelta(days=30)
        step = ActionStep.objects.create(
            business_idea=self.business_idea,
            title='Launch MVP',
            deadline=deadline
        )
        self.assertEqual(step.deadline, deadline)

    def test_action_step_cascade_delete(self):
        """Test that deleting a business idea deletes its action steps"""
        step = ActionStep.objects.create(
            business_idea=self.business_idea,
            title='Step 1'
        )
        idea_id = self.business_idea.id
        self.business_idea.delete()
        self.assertFalse(ActionStep.objects.filter(business_idea_id=idea_id).exists())


class ResumeModelTest(TestCase):
    """Tests for the Resume and related models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.template = CVTemplate.objects.create(
            name='Modern Template',
            slug='modern-template'
        )

    def test_create_cv_template(self):
        """Test creating a CV template"""
        template = CVTemplate.objects.create(
            name='Professional',
            slug='professional',
            is_active=True
        )
        self.assertEqual(template.name, 'Professional')
        self.assertTrue(template.is_active)
        self.assertEqual(str(template), 'Professional')

    def test_create_resume(self):
        """Test creating a resume"""
        resume = Resume.objects.create(
            user=self.user,
            template=self.template,
            title='Software Engineer Resume',
            first_name='John',
            last_name='Doe',
            professional_summary='Experienced software engineer'
        )
        self.assertEqual(resume.user, self.user)
        self.assertEqual(resume.template, self.template)
        self.assertEqual(resume.title, 'Software Engineer Resume')
        self.assertFalse(resume.is_primary)

    def test_resume_json_fields_default(self):
        """Test JSON fields default correctly"""
        resume = Resume.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(resume.contact_details, {})
        self.assertEqual(resume.layout_order, [])

    def test_experience_entry(self):
        """Test creating an experience entry"""
        resume = Resume.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe'
        )
        experience = ExperienceEntry.objects.create(
            resume=resume,
            job_title='Software Engineer',
            employer='Tech Corp',
            city='San Francisco',
            start_date=date(2020, 1, 1),
            is_current=True,
            description='Developed web applications',
            display_order=1
        )
        self.assertEqual(experience.job_title, 'Software Engineer')
        self.assertTrue(experience.is_current)
        self.assertIsNone(experience.end_date)

    def test_education_entry(self):
        """Test creating an education entry"""
        resume = Resume.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe'
        )
        education = EducationEntry.objects.create(
            resume=resume,
            institution='University of Example',
            degree='Bachelor of Science',
            field_of_study='Computer Science',
            start_date=date(2016, 9, 1),
            end_date=date(2020, 5, 30),
            display_order=1
        )
        self.assertEqual(education.institution, 'University of Example')
        self.assertEqual(education.degree, 'Bachelor of Science')

    def test_skill_entry(self):
        """Test creating a skill entry"""
        resume = Resume.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe'
        )
        skill = SkillEntry.objects.create(
            resume=resume,
            name='Python',
            level='Advanced',
            display_order=1
        )
        self.assertEqual(skill.name, 'Python')
        self.assertEqual(skill.level, 'Advanced')

    def test_language_entry(self):
        """Test creating a language entry"""
        resume = Resume.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe'
        )
        language = LanguageEntry.objects.create(
            resume=resume,
            language='English',
            proficiency='Native'
        )
        self.assertEqual(language.language, 'English')

    def test_social_link(self):
        """Test creating a social link"""
        resume = Resume.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe'
        )
        link = SocialLink.objects.create(
            resume=resume,
            platform='LinkedIn',
            url='https://linkedin.com/in/johndoe'
        )
        self.assertEqual(link.platform, 'LinkedIn')


class ArticleModelTest(TestCase):
    """Tests for the Article model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.category = ArticleCategory.objects.create(
            name='Technology',
            slug='technology'
        )

    def test_create_article_category(self):
        """Test creating an article category"""
        category = ArticleCategory.objects.create(
            name='Career',
            slug='career'
        )
        self.assertEqual(category.name, 'Career')
        self.assertEqual(str(category), 'Career')

    def test_create_article(self):
        """Test creating an article"""
        article = Article.objects.create(
            author=self.user,
            category=self.category,
            title='How to Transition to Tech',
            slug='how-to-transition-to-tech',
            content='Article content here...',
            is_published=True
        )
        self.assertEqual(article.title, 'How to Transition to Tech')
        self.assertTrue(article.is_published)
        self.assertFalse(article.is_promoted)
        self.assertEqual(article.views_count, 0)

    def test_article_views_increment(self):
        """Test incrementing article views"""
        article = Article.objects.create(
            author=self.user,
            category=self.category,
            title='Test Article',
            slug='test-article',
            content='Content',
            is_published=True
        )
        article.views_count += 1
        article.save()
        article.refresh_from_db()
        self.assertEqual(article.views_count, 1)


class KnowledgeModelTest(TestCase):
    """Tests for the Knowledge models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.category = KnowledgeCategory.objects.create(
            name='Career Guides'
        )

    def test_create_knowledge_category(self):
        """Test creating a knowledge category"""
        category = KnowledgeCategory.objects.create(
            name='Technical Skills'
        )
        self.assertEqual(str(category), 'Technical Skills')

    def test_create_knowledge_document(self):
        """Test creating a knowledge document"""
        doc = KnowledgeDocument.objects.create(
            uploader=self.user,
            category=self.category,
            title='Resume Writing Guide',
            raw_text_content='This is a guide on how to write resumes...',
            source_url='https://example.com/guide'
        )
        self.assertEqual(doc.title, 'Resume Writing Guide')
        self.assertEqual(doc.uploader, self.user)
        self.assertEqual(str(doc), 'Resume Writing Guide')


class UserAssessmentModelTest(TestCase):
    """Tests for the UserAssessment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_create_user_assessment(self):
        """Test creating a user assessment"""
        assessment = UserAssessment.objects.create(
            user=self.user,
            completed=False
        )
        self.assertEqual(assessment.user, self.user)
        self.assertFalse(assessment.completed)
        self.assertEqual(assessment.answers, {})

    def test_assessment_answers_sync_to_convenience_fields(self):
        """Test that answers sync to convenience fields on save"""
        assessment = UserAssessment.objects.create(
            user=self.user,
            answers={
                'service_branch': 'Army',
                'years_of_service': '5',
                'deployment_experience': 'Yes',
                'leadership_experience': '1',
                'primary_skills': 'python,django'
            }
        )
        assessment.refresh_from_db()
        self.assertEqual(assessment.service_branch, 'Army')
        self.assertEqual(assessment.years_of_service, 5)
        self.assertTrue(assessment.deployment_experience)
        self.assertTrue(assessment.leadership_experience)
        self.assertEqual(assessment.primary_skills, 'python,django')

    def test_assessment_boolean_parsing(self):
        """Test various boolean answer formats"""
        # Test 'Yes'
        assessment1 = UserAssessment.objects.create(
            user=self.user,
            answers={'deployment_experience': 'Yes'}
        )
        self.assertTrue(assessment1.deployment_experience)
        
        # Test 'true'
        assessment1.answers = {'deployment_experience': 'true'}
        assessment1.save()
        assessment1.refresh_from_db()
        self.assertTrue(assessment1.deployment_experience)

    def test_to_llm_context(self):
        """Test the to_llm_context method"""
        assessment = UserAssessment.objects.create(
            user=self.user,
            experience_level='mid',
            experience_years=5,
            primary_skills='python,django,react',
            service_branch='Navy',
            answers={
                'current_goals': 'Find remote job',
                'long_term_goals': 'Start consulting business'
            }
        )
        context = assessment.to_llm_context()
        self.assertIn('Experience level: mid', context)
        self.assertIn('Years of experience: 5', context)
        self.assertIn('Primary skills: python,django,react', context)
        self.assertIn('Service branch: Navy', context)
        self.assertIn('Short-term goals: Find remote job', context)
        self.assertIn('Long-term goals: Start consulting business', context)

    def test_assessment_questions_constant(self):
        """Test that ASSESSMENT_QUESTIONS is properly defined"""
        self.assertIsInstance(ASSESSMENT_QUESTIONS, list)
        self.assertGreater(len(ASSESSMENT_QUESTIONS), 0)
        # Check each question has required fields
        for question in ASSESSMENT_QUESTIONS:
            self.assertIn('id', question)
            self.assertIn('question', question)
            self.assertIn('type', question)
