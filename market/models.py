from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

PROJECT_TYPES = [
    ('RE', 'Reforestation'),
    ('AF', 'Afforestation'),
    ('CS', 'Clean Cookstoves'),
    ('BG', 'Biogas'),
    ('AE', 'Agricultural/Soil'),
    ('OT', 'Other'),
]

class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=2, choices=PROJECT_TYPES)
    location = models.CharField(max_length=255, help_text='County, GPS or constituency')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class CreditListing(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='listings')
    available_credits = models.PositiveIntegerField(help_text='Estimated tons CO2')
    price_per_credit = models.DecimalField(max_digits=10, decimal_places=2, help_text='USD per ton')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.project.title} - {self.available_credits} tCO2 @ ${self.price_per_credit}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    listing = models.ForeignKey(CreditListing, on_delete=models.PROTECT)
    credits_bought = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(default=timezone.now)
    payment_reference = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Txn #{self.id} by {self.buyer.username} - {self.status}"
