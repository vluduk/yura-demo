from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0014_remove_cvtemplate"),
    ]

    operations = [
        migrations.AddField(
            model_name="resume",
            name="template_id",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="resume",
            name="profession",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
