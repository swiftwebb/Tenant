from django import forms
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField as FormPhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.forms import Select, TextInput


from .models import *
from ecom.models import *
from content.models import *
from phot.models import *

from restaurant.models import *
from blog.models import *
from company.models import *
import requests
from django.conf import settings









class BlogForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'business_name', 'Tagline', 'business_description', 'logo',
            'street_address', 'apartment_address', 'city', 'state', 'zip',
            'phone_number', 'bank', 'account_no', 'account_name','tiktok',
            'facebook','instagram',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Enter your business name",
        'required': 'required', 
            }),
            'Tagline': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Your catchy business slogan",
            }),
            'business_description': forms.Textarea(attrs={
        'class':'form-textarea flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 min-h-[120px] placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Tell us more about your business..",
        'required': 'required', 
            }),

            'logo': forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'dropzone-file',
            'type': 'file',
            }),
            'street_address': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Street Address",
            }),
            'apartment_address': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Apartment Address (optional)",
            }),
            'city': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"City",
            }),
            'state': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"State",
            }),
            'zip': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Zip",
            }),
            'phone_number': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Phone Number",
        'required': 'required', 
            }),
            'bank': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Bank",
            }),
            'account_no': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Account number",
            }),
            'account_name': forms.TextInput(attrs={
        'class':'form-input mb-4 mt-3 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Account Name",
            }),
            'tiktok': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Tiktok",
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Instagram",
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Facebook",
            }),
        }





class CompanyForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'business_name', 'Tagline', 'business_description', 'logo',
            'street_address', 'apartment_address', 'city', 'state', 'zip',
            'phone_number', 'bank', 'account_no', 'account_name','linkedin',
            'facebook','instagram',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Enter your business name",
        'required': 'required', 
            }),
            'Tagline': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Your catchy business slogan",
            }),
            'business_description': forms.Textarea(attrs={
        'class':'form-textarea flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 min-h-[120px] placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Tell us more about your business..",
        'required': 'required', 
            }),

            'logo': forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'dropzone-file',
            'type': 'file',
            }),
            'street_address': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Street Address",
        'required': 'required', 
            }),
            'apartment_address': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"apartment Address (optional)",
            }),
            'city': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"City",
        'required': 'required', 
            }),
            'state': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"State",
        'required': 'required', 
            }),
            'zip': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Zip",
        'required': 'required', 
            }),
            'phone_number': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Phone Number",
        'required': 'required', 
            }),
            'bank': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Bank",
            }),
            'account_no': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Account number",
            }),
            'account_name': forms.TextInput(attrs={
        'class':'form-input mb-4 mt-3 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Account Name",
            }),

            'linkedin': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Linkedin",
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Instagram",
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Facebook",
            }),
        }

 







class StoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Fetch bank list dynamically from Paystack ---
        try:
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            response = requests.get("https://api.paystack.co/bank?country=nigeria", headers=headers)
            banks = response.json().get("data", [])
            bank_choices = [("", "Select your bank")]
            bank_choices += [(bank["code"], bank["name"]) for bank in banks]
        except Exception:
            bank_choices = [("", "Select your bank")]

        # --- Apply Tailwind styling to the dropdown ---
        self.fields["bank"].widget = forms.Select(
            choices=bank_choices,
            attrs={
                "class": (
                    "form-select mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg "
                    "text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 "
                    "border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark "
                    "h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal "
                    "appearance-none"
                ),
                "required": "required",
            },
        )

    class Meta:
        model = Client
        fields = [
            'business_name', 'Tagline', 'business_description', 'logo',
            'street_address', 'apartment_address', 'city', 'state', 'zip',
            'phone_number', 'bank', 'account_no', 'account_name','tiktok',
            'facebook','instagram','business_logistics',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Enter your business name",
                'required': 'required', 
            }),
            'Tagline': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Your catchy business slogan",
            }),
            'business_description': forms.Textarea(attrs={
                'class': 'form-textarea flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 min-h-[120px] '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Tell us more about your business..",
                'required': 'required', 
            }),
            'business_logistics': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "business logistics",
                'required': 'required', 
            }),
            'logo': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'dropzone-file',
                'type': 'file',
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Street Address",
            }),
            'apartment_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Apartment Address",
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "City",
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "State",
            }),
            'zip': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Zip",
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Phone Number",
                'required': 'required', 
            }),
            'account_no': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Account number",
                'required': 'required', 
            }),
            'account_name': forms.TextInput(attrs={
                'readonly': True,
                'class': 'form-input bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 cursor-not-allowed '
                         'rounded-lg w-full h-14 p-[15px] text-base font-normal leading-normal border border-gray-300 '
                         'dark:border-gray-600',
                        
            }),
            'tiktok': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Tiktok",
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Instagram",
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Facebook",
            }),
            
        }
    
    
    def clean_business_name(self):
        business_name = self.cleaned_data.get("business_name")

        if Client.objects.exclude(pk=self.instance.pk).filter(business_name__iexact=business_name).exists():
            raise forms.ValidationError("This business name already exists. Please choose another name.")

        return business_name

    def clean(self):
        cleaned_data = super().clean()
        account_name = cleaned_data.get("account_name")
        bank_code = cleaned_data.get("bank")

        if not account_name:
            raise forms.ValidationError("Invalid bank details. Please verify your account before submitting.")

        # Fetch bank name from Paystack list
        try:
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            response = requests.get("https://api.paystack.co/bank?country=nigeria", headers=headers)
            banks = response.json().get("data", [])
            bank_name = next((b["name"] for b in banks if b["code"] == bank_code), None)
            cleaned_data["bank_name"] = bank_name
        except Exception:
            cleaned_data["bank_name"] = None

        return cleaned_data




class RestForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'business_name', 'Tagline', 'business_description', 'logo',
            'street_address', 'apartment_address', 'city', 'state', 'zip',
            'phone_number', 'bank', 'account_no', 'account_name','tiktok',
            'facebook','instagram','business_working_hours',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Enter your business name",
        'required': 'required', 
            }),
            'Tagline': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Your catchy business slogan",
            }),
            'business_description': forms.Textarea(attrs={
        'class':'form-textarea flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 min-h-[120px] placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
        'placeholder':"Tell us more about your business..",
        'required': 'required', 
            }),

            'logo': forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'dropzone-file',
            'type': 'file',
            }),
            'street_address': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Street Address",
        'required': 'required', 
            }),
            'apartment_address': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Apartment Address",
            }),
            'city': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"City",
        'required': 'required', 
            }),
            'state': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"State",
        'required': 'required', 
            }),
            'zip': forms.TextInput(attrs={
        'class':'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Zip",
        'required': 'required', 
            }),
            'phone_number': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Phone Number",
        'required': 'required', 
            }),
            'bank': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Bank",
            }),
            'account_no': forms.TextInput(attrs={
        'class':'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Account number",
            }),
            'account_name': forms.TextInput(attrs={
        'class':'form-input mb-4 mt-3 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
        'placeholder':"Account Name",
        'required':'required',
            }),
            'tiktok': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Tiktok",
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Instagram",
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Facebook",
            }),
            'business_working_hours': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "business working hours",
                'required': 'required', 
            }),
        }

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     # ✅ This is where you make it required
        #     self.fields['business_name'].required = True








class FoodtForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Fetch bank list dynamically from Paystack ---
        try:
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            response = requests.get("https://api.paystack.co/bank?country=nigeria", headers=headers)
            banks = response.json().get("data", [])
            bank_choices = [("", "Select your bank")]
            bank_choices += [(bank["code"], bank["name"]) for bank in banks]
        except Exception:
            bank_choices = [("", "Select your bank")]

        # --- Apply Tailwind styling to the dropdown ---
        self.fields["bank"].widget = forms.Select(
            choices=bank_choices,
            attrs={
                "class": (
                    "form-select mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg "
                    "text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 "
                    "border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark "
                    "h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal "
                    "appearance-none"
                ),
                "required": "required",
            },
        )

    class Meta:
        model = Client
        fields = [
            'business_name', 'Tagline', 'business_description', 'logo',
            'street_address', 'apartment_address', 'city', 'state', 'zip',
            'phone_number', 'bank', 'account_no', 'account_name','tiktok',
            'facebook','instagram',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Enter your business name",
                'required': 'required', 
            }),
            'Tagline': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Your catchy business slogan",
            }),
            'business_description': forms.Textarea(attrs={
                'class': 'form-textarea flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 min-h-[120px] '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Tell us more about your business..",
                'required': 'required', 
            }),
            'logo': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'dropzone-file',
                'type': 'file',
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Street Address",
            }),
            'apartment_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Apartment Address",
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "City",
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "State",
            }),
            'zip': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Zip",
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Phone Number",
                'required': 'required', 
            }),
            'account_no': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Account number",
                'required': 'required', 
            }),
            'account_name': forms.TextInput(attrs={
                'readonly': True,
                'class': 'form-input bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 cursor-not-allowed '
                         'rounded-lg w-full h-14 p-[15px] text-base font-normal leading-normal border border-gray-300 '
                         'dark:border-gray-600',
                        
            }),
            'tiktok': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Tiktok",
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Instagram",
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Facebook",
            }),
        }
    def clean(self):
        cleaned_data = super().clean()
        account_name = cleaned_data.get("account_name")
        bank_code = cleaned_data.get("bank")

        if not account_name:
            raise forms.ValidationError("Invalid bank details. Please verify your account before submitting.")

        # Fetch bank name from Paystack list
        try:
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            response = requests.get("https://api.paystack.co/bank?country=nigeria", headers=headers)
            banks = response.json().get("data", [])
            bank_name = next((b["name"] for b in banks if b["code"] == bank_code), None)
            cleaned_data["bank_name"] = bank_name
        except Exception:
            cleaned_data["bank_name"] = None

        return cleaned_data










class FreeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Fetch bank list dynamically from Paystack ---
        try:
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            response = requests.get("https://api.paystack.co/bank?country=nigeria", headers=headers)
            banks = response.json().get("data", [])
            bank_choices = [("", "Select your bank")]
            bank_choices += [(bank["code"], bank["name"]) for bank in banks]
        except Exception:
            bank_choices = [("", "Select your bank")]

        # --- Apply Tailwind styling to the dropdown ---
        self.fields["bank"].widget = forms.Select(
            choices=bank_choices,
            attrs={
                "class": (
                    "form-select mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg "
                    "text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 "
                    "border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark "
                    "h-14 placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal "
                    "appearance-none"
                ),
                "required": "required",
            },
        )

    class Meta:
        model = Client
        fields = [
            'business_name', 'Tagline', 'business_description', 'logo',
            'street_address', 'apartment_address', 'city', 'state', 'zip',
            'phone_number', 'bank', 'account_no', 'account_name','business_picture','linkedin','tiktok',
            'facebook','instagram',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Enter your business name",
                'required': 'required', 
            }),
            'Tagline': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Your catchy business slogan",
            }),
            'business_description': forms.Textarea(attrs={
                'class': 'form-textarea flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 min-h-[120px] '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Tell us more about your business..",
                'required': 'required', 
            }),
            'logo': forms.FileInput(attrs={
    'class': 'hidden',
    'id': 'logo-upload',
    'type': 'file',
}),
'business_picture': forms.FileInput(attrs={
    'class': 'hidden',
    'id': 'business-picture-upload',
    'type': 'file',
}),
            'street_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Street Address",
            }),
            'apartment_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Apartment Address",
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "City",
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "State",
            }),
            'zip': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Zip",
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Phone Number",
                'required': 'required', 
            }),
            'account_no': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Account number",
                'required': 'required', 
            }),
            'account_name': forms.TextInput(attrs={
                'readonly': True,
                'class': 'form-input bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 cursor-not-allowed '
                         'rounded-lg w-full h-14 p-[15px] text-base font-normal leading-normal border border-gray-300 '
                         'dark:border-gray-600',
                        
            }),
            'tiktok': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Tiktok",
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Instagram",
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Facebook",
            }),
            'linkedin': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Linkedin",
            }),
        }
    def clean(self):
        cleaned_data = super().clean()
        account_name = cleaned_data.get("account_name")
        bank_code = cleaned_data.get("bank")

        if not account_name:
            raise forms.ValidationError("Invalid bank details. Please verify your account before submitting.")

        # Fetch bank name from Paystack list
        try:
            headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            response = requests.get("https://api.paystack.co/bank?country=nigeria", headers=headers)
            banks = response.json().get("data", [])
            bank_name = next((b["name"] for b in banks if b["code"] == bank_code), None)
            cleaned_data["bank_name"] = bank_name
        except Exception:
            cleaned_data["bank_name"] = None

        return cleaned_data





class PhotoForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = [
            'business_name', 'Tagline', 'business_description', 'logo',
            'street_address', 'apartment_address', 'city', 'state', 'zip',
            'phone_number', 'bank', 'account_no', 'account_name','business_picture','linkedin','tiktok',
            'facebook','instagram',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Enter your business name",
                'required': 'required', 
            }),
            'Tagline': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Your catchy business slogan",
            }),
            'business_description': forms.Textarea(attrs={
                'class': 'form-textarea flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 min-h-[120px] '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Tell us more about your business..",
                'required': 'required', 
            }),
            'logo': forms.FileInput(attrs={
    'class': 'hidden',
    'id': 'logo-upload',
    'type': 'file',
}),
'business_picture': forms.FileInput(attrs={
    'class': 'hidden',
    'id': 'business-picture-upload',
    'type': 'file',
}),
            'street_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Street Address",
            }),
            'apartment_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Apartment Address",
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "City",
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "State",
            }),
            'zip': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Zip",
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Phone Number",
                'required': 'required', 
            }),
            'tiktok': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Tiktok",
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Instagram",
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Facebook",
            }),
            'linkedin': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Linkedin",
            }),
        }

















class influForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = [
            'business_name', 'Tagline', 'business_description', 'logo',
            'street_address', 'apartment_address', 'city', 'state', 'zip',
            'phone_number', 'bank', 'account_no', 'account_name','business_picture','linkedin','tiktok',
            'facebook','instagram',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Enter your business name",
                'required': 'required', 
            }),
            'Tagline': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 h-14 '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Your catchy business slogan",
            }),
            'business_description': forms.Textarea(attrs={
                'class': 'form-textarea flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg '
                         'text-gray-900 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 min-h-[120px] '
                         'placeholder:text-gray-500 dark:placeholder:text-gray-400 p-4 text-base font-normal leading-normal',
                'placeholder': "Tell us more about your business..",
                'required': 'required', 
            }),
            'logo': forms.FileInput(attrs={
    'class': 'hidden',
    'id': 'logo-upload',
    'type': 'file',
}),
'business_picture': forms.FileInput(attrs={
    'class': 'hidden',
    'id': 'business-picture-upload',
    'type': 'file',
}),
            'street_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Street Address",
            }),
            'apartment_address': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Apartment Address",
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "City",
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "State",
            }),
            'zip': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Zip",
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Phone Number",
                'required': 'required', 
            }),
            'tiktok': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Tiktok",
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Instagram",
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Facebook",
            }),
            'linkedin': forms.TextInput(attrs={
                'class': 'form-input mb-4 flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg '
                         'text-primary-text dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 '
                         'border border-gray-300 dark:border-gray-600 bg-white dark:bg-background-dark h-14 '
                         'placeholder:text-secondary-text p-[15px] text-base font-normal leading-normal',
                'placeholder': "Linkedin",
            }),
        }


































from ecom.models import *
from ecom.models import Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'image',
            'size',
            'color',
            'quantity',
            'price',
            'discount_price',
            'category',
            'best_sellers',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        if tenant:
            from django_tenants.utils import schema_context
            with schema_context(tenant.schema_name):
                self.fields['category'].queryset = Category.objects.all()
        else:
            self.fields['category'].queryset = Category.objects.none()



# forms.py

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'amount']

    def __init__(self, *args, **kwargs):
        # Safely pop tenant if passed
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        # Optional: perform tenant-specific logic
        if self.tenant:
            # Example: filter related dropdowns or do tenant checks here
            pass






class CatForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        # Safely pop tenant if passed
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        # Optional: perform tenant-specific logic
        if self.tenant:
            # Example: filter related dropdowns or do tenant checks here
            pass





class DelStateForm(forms.ModelForm):
    class Meta:
        model = DeliveryState
        fields = ['name','fixed_price']

    def __init__(self, *args, **kwargs):
        # Safely pop tenant if passed
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        # Optional: perform tenant-specific logic
        if self.tenant:
            # Example: filter related dropdowns or do tenant checks here
            pass




class DelCityForm(forms.ModelForm):
    class Meta:
        model = DeliveryCity
        fields = ['name','delivery_fee']

    def __init__(self, *args, **kwargs):
        # Safely pop tenant if passed
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        # Optional: perform tenant-specific logic
        if self.tenant:
            # Example: filter related dropdowns or do tenant checks here
            pass


from ecom.models import DeliveryBase

class DelBaseForm(forms.ModelForm):
    class Meta:
        model = DeliveryBase
        fields = ['name','price']

    def __init__(self, *args, **kwargs):
        # Safely pop tenant if passed
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        # Optional: perform tenant-specific logic
        if self.tenant:
            # Example: filter related dropdowns or do tenant checks here
            pass






from content.models import *
from content.models import Categorysss
from content.models import Socails
class PostForm(forms.ModelForm):
    class Meta:
        model = Socails
        fields = [
            'name',
            'like',
            'comment',
            'views',
            'thumbnail',
            'link',
            'category',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        if tenant:
            from django_tenants.utils import schema_context
            with schema_context(tenant.schema_name):
                self.fields['category'].queryset = Categorysss.objects.all()
        else:
            self.fields['category'].queryset = Categorysss.objects.none()










class CampForm(forms.ModelForm):
    class Meta:
        model = Campagin
        fields = [
            'Title',
            'social',
            'problem',
            'overview',
            'solution',
            'result',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        if tenant:
            from django_tenants.utils import schema_context
            with schema_context(tenant.schema_name):
                self.fields['social'].queryset = Socails.objects.all()
        else:
            self.fields['social'].queryset = Socails.objects.none()



class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'name',
            'description',
            'amount',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

class HomeconForm(forms.ModelForm):
    class Meta:
        model = Home
        fields = [
            'title',
            'description',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)


class AboutconForm(forms.ModelForm):
    class Meta:
        model = About
        fields = [
            'title',
            'description',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)



from phot.models import *
class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = [
            'title',
            'description',
            'image',
            'featured',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

class SerphotForm(forms.ModelForm):
    class Meta:
        model = Service_Photo
        fields = [
            'name',
            'description',
            'amount',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)



class ABouphotForm(forms.ModelForm):
    class Meta:
        model = Myself
        fields = [
            'name',
            'image_tool',
            'my_story',
            'expertise',
            'image_demo',

            'image',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)




from ecom.models import Sale, Product
class SaletForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'reference',
            'product',
            'quantity_sold',
            'total',

        ]


    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        if tenant:
            from django_tenants.utils import schema_context
            with schema_context(tenant.schema_name):
                self.fields['product'].queryset = Product.objects.all()
        else:
            self.fields['product'].queryset = Product.objects.none()

    def save(self, commit=True):
        sale = super().save(commit)

        # Reduce product stock
        for p in sale.product.all():
            p.quantity -= self.cleaned_data['quantity_sold']
            if p.quantity < 0:
                p.quantity = 0
            p.save()

        return sale











from company.models import *



class HocompanyForm(forms.ModelForm):
    class Meta:
        model = Ideal
        fields = [
            'overview',
            'description',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)


class SerompanyForm(forms.ModelForm):
    class Meta:
        model = Serv
        fields = [
            'title',
            'overview',
            'premium',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)


class LeadompanyForm(forms.ModelForm):
    class Meta:
        model = Leaders
        fields = [
            'title',
            'name',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)



class AdompanyForm(forms.ModelForm):
    class Meta:
        model = Abut
        fields = [
            'image',
            'description',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)



from blog.models import *



class BlyForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = [
            'title',
            'overview',
            'description',
            'thumbnail',
            'cataegory',
            'featured',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)






class BAbuForm(forms.ModelForm):
    class Meta:
        model = Abbb
        fields = [
            'my_story',
            'our_mission',
            'why',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)


from restaurant.models import *
class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = [
            'name',
            'category',
            'description',
            'price',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)


        if tenant:
            from django_tenants.utils import schema_context
            with schema_context(tenant.schema_name):
                self.fields['category'].queryset = Catgg.objects.all()
        else:
            self.fields['category'].queryset = Catgg.objects.none()





class RcatForm(forms.ModelForm):
    class Meta:
        model = Catgg
        fields = [
            'name',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)


class HrForm(forms.ModelForm):
    class Meta:
        model = Hom
        fields = [
            'image',
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

