from django.db import migrations
from django.utils.text import slugify
import uuid

def populate_articles(apps, schema_editor):
    ArticleCategory = apps.get_model('api', 'ArticleCategory')
    Article = apps.get_model('api', 'Article')
    User = apps.get_model('api', 'User')

    # Ensure we have at least one user for author
    author = User.objects.filter(is_superuser=True).first()
    if not author:
        # Try any user
        author = User.objects.first()
    
    # If still no user, we can leave author null or create one (but creating one in migration might be tricky if auth is complex)
    # Let's assume there's a user or leave it null.

    categories_data = ["Бізнес", "Найм", "Самозайнятість", "Освіта", "Кар'єра"]
    category_map = {}

    for cat_name in categories_data:
        cat, created = ArticleCategory.objects.get_or_create(
            name=cat_name,
            defaults={'slug': slugify(cat_name, allow_unicode=True)}
        )
        category_map[cat_name] = cat

    articles_data = [
        {
            "title": "Як розпочати власний бізнес в Україні",
            "summary": "Покроковий гайд для початківців про реєстрацію ФОП, вибір системи оподаткування та перші кроки в підприємництві.",
            "image": "https://images.unsplash.com/photo-1664575602554-2087b04935a5?w=400",
            "category": "Бізнес",
            "views": 1250,
        },
        {
            "title": "Топ-10 помилок при наймі працівників",
            "summary": "Розбираємо найпоширеніші помилки роботодавців та як їх уникнути при пошуку та наймі нових співробітників.",
            "image": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=400",
            "category": "Найм",
            "views": 890,
        },
        {
            "title": "Фріланс vs Офіс: що обрати?",
            "summary": "Порівняння переваг та недоліків віддаленої роботи та офісної зайнятості для різних типів спеціалістів.",
            "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
            "category": "Самозайнятість",
            "views": 2100,
        },
        {
            "title": "Безкоштовні курси програмування 2024",
            "summary": "Огляд найкращих безкоштовних онлайн-курсів для вивчення програмування з нуля.",
            "image": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400",
            "category": "Освіта",
            "views": 3400,
        },
        {
            "title": "Як побудувати кар'єру в IT без досвіду",
            "summary": "Реальні історії та поради від людей, які успішно перейшли в IT-сферу з інших професій.",
            "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400",
            "category": "Кар'єра",
            "views": 4500,
        },
        {
            "title": "Маркетинг для малого бізнесу",
            "summary": "Ефективні маркетингові стратегії з мінімальним бюджетом для невеликих компаній.",
            "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400",
            "category": "Бізнес",
            "views": 780,
        },
        {
            "title": "Як провести ефективну співбесіду",
            "summary": "Техніки та питання для оцінки кандидатів на різні позиції.",
            "image": "https://images.unsplash.com/photo-1565688534245-05d6b5be184a?w=400",
            "category": "Найм",
            "views": 560,
        },
        {
            "title": "Податки для самозайнятих: повний гайд",
            "summary": "Все про оподаткування ФОП: групи, ставки, звітність та оптимізація.",
            "image": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400",
            "category": "Самозайнятість",
            "views": 1800,
        },
    ]

    for item in articles_data:
        # Generate improvised content
        content = f"{item['summary']}\n\n"
        content += f"Детальний розгляд теми '{item['title']}'.\n\n"
        content += "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n\n"
        content += "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\n"
        content += "Висновки:\nЦе дуже важлива тема для розвитку вашої кар'єри або бізнесу. Сподіваємося, ця стаття була корисною."

        # Check if article already exists to avoid duplicates if migration runs multiple times (though RunPython usually runs once)
        if not Article.objects.filter(title=item['title']).exists():
            Article.objects.create(
                author=author,
                category=category_map.get(item['category']),
                title=item['title'],
                slug=slugify(item['title'], allow_unicode=True),
                content=content,
                cover_image_url=item['image'],
                is_published=True,
                views_count=item['views']
            )

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_userassessment_benefits_awareness_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_articles),
    ]
