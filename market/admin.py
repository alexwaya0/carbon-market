from django.contrib import admin
from .models import Project, CreditListing, Transaction

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'project_type', 'location', 'created_at')
    search_fields = ('title', 'owner__username')

@admin.register(CreditListing)
class CreditListingAdmin(admin.ModelAdmin):
    list_display = ('project', 'available_credits', 'price_per_credit', 'available', 'created_at')
    list_filter = ('available',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'listing', 'credits_bought', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
