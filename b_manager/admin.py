from django.contrib import admin
from .models import *


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'can_use_custom_domain')
    list_filter = ('can_use_custom_domain',)




@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'plan', 'trial_ends_on', 'paid_until', 'is_active')
    list_filter = ('is_active', 'plan', 'template_type')
    search_fields = ('name', 'schema_name', 'email')




@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')

admin.site.register(PaystackEventLog)


admin.site.register(WebsiteTemplate)
admin.site.register(Job)
admin.site.register(TenantAPIKey)
admin.site.register(Review)
admin.site.register(WebsiteVisit)
admin.site.register(Tutorial)