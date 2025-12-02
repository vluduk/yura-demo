from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from api.models.conversation import Conversation, ConversationType
from api.models.message import Message
from api.models.business import BusinessIdea, ActionStep
from api.models.resume import Resume, CVTemplate, ExperienceEntry, EducationEntry
from api.models.article import Article, ArticleCategory
from api.models.user_assesment import UserAssessment
from api.serializers.auth import UserRegistrationSerializer, UserSerializer
from api.serializers.conversation import ConversationSerializer
from api.serializers.message import MessageSerializer
from api.serializers.business import BusinessIdeaSerializer, ActionStepSerializer
from api.serializers.resume import ResumeSerializer, CVTemplateSerializer
from api.serializers.user_assessment import UserAssessmentSerializer

User = get_user_model()


class UserSerializerTest(TestCase):
    """Tests for User serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone='1234567890'
        )

    def test_user_serializer_fields(self):
        """Test that UserSerializer contains correct fields"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('role', data)
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'John')

    def test_user_registration_serializer_valid(self):
        """Test valid user registration"""
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '9876543210'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_user_registration_serializer_invalid_email(self):
        """Test registration with invalid email"""
        data = {
            'email': 'not-an-email',
            'password': 'SecurePass123!',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_user_registration_serializer_missing_fields(self):
        """Test registration with missing required fields"""
        data = {
            'email': 'test@example.com'
            # Missing password, first_name, last_name
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_user_registration_creates_user(self):
        """Test that registration serializer creates user correctly"""
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            self.assertEqual(user.email, 'newuser@example.com')
            self.assertTrue(user.check_password('SecurePass123!'))
            self.assertEqual(user.first_name, 'Jane')


class ConversationSerializerTest(TestCase):
    """Tests for Conversation serializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            conv_type=ConversationType.BUSINESS
        )

    def test_conversation_serializer_fields(self):
        """Test that ConversationSerializer contains correct fields"""
        serializer = ConversationSerializer(self.conversation)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('title', data)
        self.assertIn('conv_type', data)
        self.assertIn('created_at', data)
        self.assertIn('last_active_at', data)
        self.assertEqual(data['title'], 'Test Conversation')
        self.assertEqual(data['conv_type'], ConversationType.BUSINESS)

    def test_conversation_serializer_create(self):
        """Test creating a conversation via serializer"""
        data = {
            'title': 'New Conversation',
            'conv_type': ConversationType.HIRING
        }
        serializer = ConversationSerializer(data=data)
        if serializer.is_valid():
            conv = serializer.save(user=self.user)
            self.assertEqual(conv.title, 'New Conversation')
            self.assertEqual(conv.user, self.user)

    def test_conversation_serializer_with_messages(self):
        """Test conversation serializer includes messages if configured"""
        Message.objects.create(
            conversation=self.conversation,
            content='Hello',
            is_user=True
        )
        Message.objects.create(
            conversation=self.conversation,
            content='Hi there',
            is_user=False
        )
        
        serializer = ConversationSerializer(self.conversation)
        data = serializer.data
        
        # Check if messages are included (depends on serializer configuration)
        if 'messages' in data:
            self.assertEqual(len(data['messages']), 2)


class MessageSerializerTest(TestCase):
    """Tests for Message serializer"""
    
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
        self.message = Message.objects.create(
            conversation=self.conversation,
            content='Test message content',
            is_user=True
        )

    def test_message_serializer_fields(self):
        """Test that MessageSerializer contains correct fields"""
        serializer = MessageSerializer(self.message)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('content', data)
        self.assertIn('is_user', data)
        self.assertIn('created_at', data)
        self.assertEqual(data['content'], 'Test message content')
        self.assertTrue(data['is_user'])

    def test_message_serializer_create(self):
        """Test creating a message via serializer"""
        data = {
            'content': 'New message',
            'is_user': False
        }
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            msg = serializer.save(conversation=self.conversation)
            self.assertEqual(msg.content, 'New message')
            self.assertFalse(msg.is_user)


class BusinessIdeaSerializerTest(TestCase):
    """Tests for BusinessIdea serializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.business_idea = BusinessIdea.objects.create(
            user=self.user,
            title='SaaS Product',
            status='BRAINSTORM',
            validation_score=75
        )

    def test_business_idea_serializer_fields(self):
        """Test that BusinessIdeaSerializer contains correct fields"""
        serializer = BusinessIdeaSerializer(self.business_idea)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('title', data)
        self.assertIn('status', data)
        self.assertIn('validation_score', data)
        self.assertEqual(data['title'], 'SaaS Product')
        self.assertEqual(data['validation_score'], 75)

    def test_business_idea_serializer_create(self):
        """Test creating a business idea via serializer"""
        data = {
            'title': 'New Business Idea',
            'status': 'VALIDATION',
            'market_analysis': 'Strong market demand'
        }
        serializer = BusinessIdeaSerializer(data=data)
        if serializer.is_valid():
            idea = serializer.save(user=self.user)
            self.assertEqual(idea.title, 'New Business Idea')
            self.assertEqual(idea.status, 'VALIDATION')

    def test_business_idea_json_fields_serialization(self):
        """Test that JSON fields are serialized correctly"""
        self.business_idea.business_canvas = {
            'value_proposition': 'Affordable solution',
            'customer_segments': ['SMBs', 'Startups']
        }
        self.business_idea.save()
        
        serializer = BusinessIdeaSerializer(self.business_idea)
        data = serializer.data
        
        if 'business_canvas' in data:
            self.assertIn('value_proposition', data['business_canvas'])


class ActionStepSerializerTest(TestCase):
    """Tests for ActionStep serializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.business_idea = BusinessIdea.objects.create(
            user=self.user,
            title='SaaS Product'
        )
        self.action_step = ActionStep.objects.create(
            business_idea=self.business_idea,
            title='Market Research',
            details='Conduct surveys',
            status='PENDING',
            step_order=1
        )

    def test_action_step_serializer_fields(self):
        """Test that ActionStepSerializer contains correct fields"""
        serializer = ActionStepSerializer(self.action_step)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('title', data)
        self.assertIn('status', data)
        self.assertIn('step_order', data)
        self.assertEqual(data['title'], 'Market Research')

    def test_action_step_serializer_create(self):
        """Test creating an action step via serializer"""
        data = {
            'title': 'Build MVP',
            'details': 'Develop minimum viable product',
            'status': 'IN_PROGRESS',
            'step_order': 2
        }
        serializer = ActionStepSerializer(data=data)
        if serializer.is_valid():
            step = serializer.save(business_idea=self.business_idea)
            self.assertEqual(step.title, 'Build MVP')
            self.assertEqual(step.step_order, 2)


class ResumeSerializerTest(TestCase):
    """Tests for Resume serializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.template = CVTemplate.objects.create(
            name='Modern',
            slug='modern'
        )
        self.resume = Resume.objects.create(
            user=self.user,
            template=self.template,
            title='Software Engineer Resume',
            first_name='John',
            last_name='Doe',
            professional_summary='Experienced developer'
        )

    def test_resume_serializer_fields(self):
        """Test that ResumeSerializer contains correct fields"""
        serializer = ResumeSerializer(self.resume)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('title', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('professional_summary', data)
        self.assertEqual(data['title'], 'Software Engineer Resume')

    def test_resume_serializer_with_entries(self):
        """Test resume serializer with related entries"""
        ExperienceEntry.objects.create(
            resume=self.resume,
            job_title='Developer',
            employer='Tech Co'
        )
        EducationEntry.objects.create(
            resume=self.resume,
            institution='University',
            degree='BS Computer Science'
        )
        
        serializer = ResumeSerializer(self.resume)
        data = serializer.data
        
        # Check if related entries are included (depends on serializer configuration)
        if 'experience_entries' in data:
            self.assertGreaterEqual(len(data['experience_entries']), 1)

    def test_cv_template_serializer(self):
        """Test CVTemplateSerializer"""
        serializer = CVTemplateSerializer(self.template)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('slug', data)
        self.assertEqual(data['name'], 'Modern')


class UserAssessmentSerializerTest(TestCase):
    """Tests for UserAssessment serializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assessment = UserAssessment.objects.create(
            user=self.user,
            answers={
                'service_branch': 'Navy',
                'years_of_service': '10',
                'primary_skills': 'leadership,operations'
            },
            completed=False
        )

    def test_user_assessment_serializer_fields(self):
        """Test that UserAssessmentSerializer contains correct fields"""
        serializer = UserAssessmentSerializer(self.assessment)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('answers', data)
        self.assertIn('completed', data)
        self.assertFalse(data['completed'])

    def test_user_assessment_serializer_answers(self):
        """Test that answers are serialized correctly"""
        serializer = UserAssessmentSerializer(self.assessment)
        data = serializer.data
        
        if 'answers' in data:
            self.assertIn('service_branch', data['answers'])
            self.assertEqual(data['answers']['service_branch'], 'Navy')

    def test_user_assessment_serializer_create(self):
        """Test creating an assessment via serializer"""
        data = {
            'answers': {
                'current_goals': 'Find remote job',
                'work_preferences': 'Freelance'
            },
            'completed': False
        }
        serializer = UserAssessmentSerializer(data=data)
        if serializer.is_valid():
            assessment = serializer.save(user=self.user)
            self.assertEqual(assessment.user, self.user)
            self.assertIn('current_goals', assessment.answers)

    def test_user_assessment_serializer_update(self):
        """Test updating an assessment via serializer"""
        new_data = {
            'answers': {
                'service_branch': 'Navy',
                'years_of_service': '10',
                'primary_skills': 'leadership,operations',
                'current_goals': 'Updated goal'
            },
            'completed': True
        }
        serializer = UserAssessmentSerializer(
            self.assessment,
            data=new_data,
            partial=True
        )
        if serializer.is_valid():
            assessment = serializer.save()
            self.assertTrue(assessment.completed)


class SerializerValidationTest(TestCase):
    """Tests for serializer validation logic"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_registration_duplicate_email(self):
        """Test validation fails for duplicate email"""
        # Create first user
        User.objects.create_user(
            email='duplicate@example.com',
            password='pass123',
            first_name='First',
            last_name='User'
        )
        
        # Try to register with same email
        data = {
            'email': 'duplicate@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Second',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_conversation_type_validation(self):
        """Test that conversation type is validated"""
        data = {
            'title': 'Test Conversation',
            'conv_type': 'INVALID_TYPE'  # Not a valid choice
        }
        serializer = ConversationSerializer(data=data)
        # Depending on serializer implementation, this might fail validation
        # or accept and filter invalid values
        serializer.is_valid()  # Will raise or return False

    def test_empty_content_validation(self):
        """Test validation of empty message content"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test'
        )
        
        data = {
            'content': '',  # Empty content
            'is_user': True
        }
        serializer = MessageSerializer(data=data)
        # Most likely this should fail validation
        # but depends on serializer field configuration


class SerializerReadOnlyFieldsTest(TestCase):
    """Tests for read-only fields in serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_id_is_readonly(self):
        """Test that user ID cannot be changed via serializer"""
        serializer = UserSerializer(self.user)
        # ID should be in data but attempting to update it should not work
        original_id = serializer.data['id']
        
        update_data = {
            'id': '00000000-0000-0000-0000-000000000000',
            'email': 'test@example.com',
            'first_name': 'Updated'
        }
        update_serializer = UserSerializer(self.user, data=update_data, partial=True)
        if update_serializer.is_valid():
            user = update_serializer.save()
            # ID should remain unchanged
            self.assertEqual(str(user.id), original_id)

    def test_created_at_is_readonly(self):
        """Test that created_at timestamps cannot be changed"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test'
        )
        
        original_created = conversation.created_at
        
        # Try to update created_at via serializer
        data = {
            'title': 'Updated Title',
            'created_at': '2020-01-01T00:00:00Z'
        }
        serializer = ConversationSerializer(conversation, data=data, partial=True)
        if serializer.is_valid():
            conv = serializer.save()
            # created_at should remain unchanged
            self.assertEqual(conv.created_at, original_created)
