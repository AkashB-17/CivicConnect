from django.db import migrations

def create_initial_data(apps, schema_editor):
    Category = apps.get_model('grievances', 'Category')
    Status = apps.get_model('grievances', 'Status')

    # Create categories
    categories = [
        ('Road Issues', 'Problems related to roads and transportation', 'Public Works'),
        ('Water Supply', 'Issues with water supply and quality', 'Water Department'),
        ('Waste Management', 'Garbage collection and waste disposal issues', 'Sanitation Department'),
        ('Electricity', 'Power supply and electrical infrastructure problems', 'Electricity Department'),
        ('Public Safety', 'Safety and security concerns', 'Police Department'),
    ]

    for name, description, department in categories:
        Category.objects.create(
            name=name,
            description=description,
            department=department
        )

    # Create statuses
    statuses = [
        ('submitted', 'Grievance has been submitted'),
        ('in_review', 'Grievance is under review'),
        ('in_progress', 'Work on the grievance has started'),
        ('resolved', 'Grievance has been resolved'),
        ('rejected', 'Grievance has been rejected'),
    ]

    for name, description in statuses:
        Status.objects.create(
            name=name,
            description=description
        )

def reverse_initial_data(apps, schema_editor):
    Category = apps.get_model('grievances', 'Category')
    Status = apps.get_model('grievances', 'Status')
    
    Category.objects.all().delete()
    Status.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('grievances', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, reverse_initial_data),
    ] 