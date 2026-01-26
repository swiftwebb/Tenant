# core/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If already connected, skip
        if sociallogin.is_existing:
            return
        
        email = sociallogin.account.extra_data.get("email")
        if not email:
            return
        
        try:
            # Check if a user with this email already exists
            user = User.objects.get(email=email)
            # Connect this social account to the existing user
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            # No user with that email, allauth will create a new one
            pass
