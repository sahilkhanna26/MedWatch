from django.contrib.auth.models import AbstractUser, User
from django.db import models
# from .models import Report

class CustomUser(AbstractUser):
    USER_ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('regular', 'Regular'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='regular')

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="customuser",
    )
class Report(models.Model):
    name_reported = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, default='New')
    resolved_notes = models.TextField(blank=True, null=True)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_reported


class ReportFile(models.Model):
    report = models.ForeignKey(Report, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='report_files/')




    def __str__(self):
        return self.name_reported
