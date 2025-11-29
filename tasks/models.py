from django.db import models

class Task(models.Model):
    """
    Task model reflecting the requirements:
    - title: CharField
    - due_date: DateField
    - importance: IntegerField
    - estimated_hours: IntegerField
    - dependencies: JSONField (list of titles or ids)
    """
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    importance = models.IntegerField(default=1)
    estimated_hours = models.IntegerField(default=1)
    dependencies = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
