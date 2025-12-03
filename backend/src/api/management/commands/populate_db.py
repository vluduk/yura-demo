from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models.article import Article, ArticleCategory, ArticleTag
from api.models.business import BusinessIdea, ActionStep
from api.models.knowledge import KnowledgeCategory, KnowledgeDocument
from api.models.resume import Resume, ExperienceEntry, EducationEntry, LanguageEntry
from api.models.user_assesment import UserAssessment
from django.utils import timezone
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Wiping data...')
        self.wipe_data()
        
        self.stdout.write('Creating admin user...')
        admin_user = self.create_admin_user()
        
        self.stdout.write('Creating user assessment...')
        self.create_user_assessment(admin_user)
        
        self.stdout.write('Creating articles...')
        self.create_articles(admin_user)
        
        self.stdout.write('Creating business ideas...')
        self.create_business_ideas(admin_user)
        
        self.stdout.write('Creating knowledge base...')
        self.create_knowledge(admin_user)
        
        self.stdout.write('Creating resumes...')
        self.create_resumes(admin_user)
        
        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))

    def wipe_data(self):
        # Delete in order to respect foreign keys if necessary, though CASCADE usually handles it
        UserAssessment.objects.all().delete()
        Article.objects.all().delete()
        ArticleCategory.objects.all().delete()
        ArticleTag.objects.all().delete()
        BusinessIdea.objects.all().delete()
        KnowledgeDocument.objects.all().delete()
        KnowledgeCategory.objects.all().delete()
        Resume.objects.all().delete()
        # We do NOT delete Users here, except maybe we could, but the instruction said "except user"
        # implying we shouldn't mess with the user table too much, but we need an admin.

    def create_admin_user(self):
        email = 'admin@example.com'
        password = 'adminpassword123'
        user, created = User.objects.get_or_create(email=email)
        user.set_password(password)
        user.first_name = 'Admin'
        user.last_name = 'User'
        user.role = 'ADMIN'
        user.is_staff = True
        user.is_superuser = True
        user.save()
        if created:
            self.stdout.write(f'Created admin user: {email}')
        else:
            self.stdout.write(f'Updated admin user: {email}')
        return user

    def create_user_assessment(self, user):
        answers = {
            "service_branch": "Army",
            "service_role": "Infantry Platoon Commander",
            "rank": "Lieutenant",
            "years_of_service": 5,
            "discharge_date": "2023",
            "deployment_experience": "Yes",
            "leadership_experience": "Yes",
            "primary_skills": "Leadership, Team Management, Logistics, Crisis Management",
            "civilian_certifications": "None",
            "education_level": "Bachelors",
            "disabilities_or_limits": "None",
            "security_clearance": "Yes",
            "current_goals": "Transition to Project Management in IT",
            "long_term_goals": "Start my own logistics company",
            "work_preferences": "Full-time employment",
            "financial_needs": "Immediate steady income",
            "locality": "Kyiv",
            "available_time": "20-40 hours",
            "benefits_awareness": "Somewhat",
            "support_needs": "Legal assistance for veteran status",
            "additional_info": "Interested in tech sector"
        }
        
        UserAssessment.objects.create(
            user=user,
            answers=answers,
            experience_level="Mid-level",
            primary_skills="Leadership, Management, Logistics",
            work_preferences="Corporate",
            suggested_path="Project Management"
        )

    def create_articles(self, user):
        categories = [
            ("Бізнес", "business"),
            ("Найм", "hiring"),
            ("Самозайнятість", "self-employment"),
            ("Освіта", "education"),
            ("Кар'єра", "career")
        ]
        
        cat_objects = []
        for name, slug in categories:
            cat, _ = ArticleCategory.objects.get_or_create(name=name, slug=slug)
            cat_objects.append(cat)

        tags = ["IT", "Marketing", "Management", "Finance", "Legal", "Veterans", "Startups"]
        tag_objects = []
        for t in tags:
            tag, _ = ArticleTag.objects.get_or_create(name=t, slug=t.lower())
            tag_objects.append(tag)

        articles_data = [
            {
                "title": "Як ветерану знайти роботу в IT",
                "content": "Детальний гайд про перехід з військової служби в IT сферу. Курси, менторство, підготовка резюме...",
                "category": "Кар'єра",
                "tags": ["IT", "Veterans", "Management"]
            },
            {
                "title": "Відкриття власної кав'ярні: бізнес-план",
                "content": "Покрокова інструкція як відкрити кав'ярню. Вибір локації, обладнання, постачальників...",
                "category": "Бізнес",
                "tags": ["Startups", "Finance"]
            },
            {
                "title": "Юридичні аспекти самозайнятості",
                "content": "Як зареєструвати ФОП, вибрати групу оподаткування та вести звітність...",
                "category": "Самозайнятість",
                "tags": ["Legal", "Finance"]
            },
            {
                "title": "Безкоштовні освітні програми для ветеранів",
                "content": "Огляд доступних курсів та програм перекваліфікації, що фінансуються державою та фондами...",
                "category": "Освіта",
                "tags": ["Education", "Veterans"]
            },
             {
                "title": "Ефективне управління командою",
                "content": "Застосування військового досвіду лідерства в цивільному менеджменті...",
                "category": "Найм",
                "tags": ["Management", "Leadership"]
            }
        ]

        for data in articles_data:
            cat = next(c for c in cat_objects if c.name == data["category"])
            article = Article.objects.create(
                author=user,
                category=cat,
                title=data["title"],
                slug=data["title"].lower().replace(" ", "-").replace("'", "").replace(":", ""),
                content=data["content"] * 5, # Make it a bit longer
                is_published=True,
                is_promoted=random.choice([True, False]),
                views_count=random.randint(100, 5000)
            )
            
            # Add tags
            article_tags = [t for t in tag_objects if t.name in data["tags"]]
            article.tags.set(article_tags)

    def create_business_ideas(self, user):
        ideas = [
            {
                "title": "Drone Repair Service",
                "status": "VALIDATION",
                "score": 85,
                "market": "High demand due to agricultural and hobbyist usage growth."
            },
            {
                "title": "Veteran Security Consultancy",
                "status": "BRAINSTORM",
                "score": 60,
                "market": "Corporate security needs are rising."
            }
        ]

        for idea in ideas:
            bi = BusinessIdea.objects.create(
                user=user,
                title=idea["title"],
                status=idea["status"],
                validation_score=idea["score"],
                market_analysis=idea["market"],
                final_verdict="Promising idea with good market fit." if idea["score"] > 70 else "Needs more research."
            )
            
            ActionStep.objects.create(
                business_idea=bi,
                title="Conduct Competitor Analysis",
                status="COMPLETED",
                step_order=1
            )
            ActionStep.objects.create(
                business_idea=bi,
                title="Register Legal Entity",
                status="PENDING",
                step_order=2
            )

    def create_knowledge(self, user):
        categories = ["Legal", "Financial", "Medical", "Education"]
        cat_objects = []
        for name in categories:
            cat, _ = KnowledgeCategory.objects.get_or_create(name=name)
            cat_objects.append(cat)

        docs = [
            ("Guide to Veteran Benefits", "Legal", "Full text of the law on veteran benefits..."),
            ("Tax Breaks for Veteran Businesses", "Financial", "Details on tax exemptions..."),
            ("Rehabilitation Centers Map", "Medical", "List of centers..."),
        ]

        for title, cat_name, content in docs:
            cat = next(c for c in cat_objects if c.name == cat_name)
            KnowledgeDocument.objects.create(
                uploader=user,
                category=cat,
                title=title,
                raw_text_content=content,
                source_url="https://example.com/doc"
            )

    def create_resumes(self, user):
        resume = Resume.objects.create(
            user=user,
            title="Project Manager Resume",
            first_name=user.first_name,
            last_name=user.last_name,
            professional_summary="Experienced leader with 5 years of military service...",
            is_primary=True
        )

        ExperienceEntry.objects.create(
            resume=resume,
            job_title="Platoon Commander",
            employer="Armed Forces of Ukraine",
            city="Various",
            start_date=timezone.now().date() - timedelta(days=365*5),
            end_date=timezone.now().date() - timedelta(days=365*2),
            is_current=False
        )
        
        EducationEntry.objects.create(
            resume=resume,
            institution="Military Academy",
            degree="Bachelor of Military Science",
            field_of_study="Command & Control",
            start_date=timezone.now().date() - timedelta(days=365*9),
            end_date=timezone.now().date() - timedelta(days=365*5)
        )
        
        LanguageEntry.objects.create(
            resume=resume,
            language="Ukrainian",
            proficiency="Native"
        )
        LanguageEntry.objects.create(
            resume=resume,
            language="English",
            proficiency="B2"
        )
