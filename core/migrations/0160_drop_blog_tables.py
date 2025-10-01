from django.db import migrations


BLOG_TABLES = [
    'blog_blogpost',
    'blog_blogpost_translation',
    'blog_comment',
    'blog_notificationlog',
    'blog_lawyercard',
    'blog_category',
    'blog_tag',
    # Many-to-many table (if present)
    'blog_blogpost_tags',
]


def drop_blog_tables(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        for t in BLOG_TABLES:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS \"{t}\" CASCADE;")
            except Exception:
                # Ignore failures — table may not exist or DB may not allow CASCADE
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_case_likes'),
    ]

    operations = [
        migrations.RunPython(drop_blog_tables, reverse_code=migrations.RunPython.noop),
    ]
