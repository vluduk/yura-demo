from django.db import migrations, models
import uuid
from django.utils.text import slugify


def create_tags_and_assign(apps, schema_editor):
    Article = apps.get_model('api', 'Article')
    ArticleTag = apps.get_model('api', 'ArticleTag')

    # Mapping of article title -> list of tags
    tags_map = {
        "Як розпочати власний бізнес в Україні": ["ФОП", "реєстрація", "податки"],
        "Топ-10 помилок при наймі працівників": ["HR", "рекрутинг", "співбесіда"],
        "Фріланс vs Офіс: що обрати?": ["фріланс", "віддалена робота", "кар'єра"],
        "Безкоштовні курси програмування 2024": ["програмування", "курси", "IT"],
        "Як побудувати кар'єру в IT без досвіду": ["IT", "зміна професії", "junior"],
        "Маркетинг для малого бізнесу": ["маркетинг", "SMM", "реклама"],
        "Як провести ефективну співбесіду": ["співбесіда", "HR", "оцінка"],
        "Податки для самозайнятих: повний гайд": ["податки", "ФОП", "звітність"],
    }

    created_tags = {}

    for title, tags in tags_map.items():
        for tag_name in tags:
            slug = slugify(tag_name, allow_unicode=True)
            if tag_name not in created_tags:
                tag_obj, _ = ArticleTag.objects.get_or_create(name=tag_name, defaults={'slug': slug})
                created_tags[tag_name] = tag_obj

    # Assign tags to matching articles
    for article in Article.objects.all():
        if article.title in tags_map:
            tag_names = tags_map[article.title]
            for tn in tag_names:
                tag_obj = created_tags.get(tn)
                if tag_obj:
                    article.tags.add(tag_obj)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_populate_articles'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleTag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
            options={'db_table': 'article_tags'},
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='articles', to='api.ArticleTag'),
        ),
        migrations.RunPython(create_tags_and_assign),
    ]
