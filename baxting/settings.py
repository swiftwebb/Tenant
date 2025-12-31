
from pathlib import Path
import cloudinary
from dotenv import load_dotenv
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

project = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')  

# SECURITY WARNING: don't run with debug turned on in production!
if project==True:
    DEBUG = False
else:
    DEBUG = True




ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
]
# Application definition

SHARED_APPS = [
    'django_tenants',
    'b_manager',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic'
    'cloudinary_storage',
    'cloudinary',
    'django_ratelimit',
    'allauth',
    'allauth.account',
    'phonenumber_field',
    'django_twilio',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap4',
     'corsheaders', 
]
TENANT_APPS = (
    # your tenant-specific apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'allauth',
    'allauth.account',
    # 'ecommerce',
    # 'ecom',
    'ecom.apps.EcomConfig',
    'content.apps.ContentConfig',
    'phot.apps.PhotConfig',
    # 'landing.apps.LandingConfig',
    'blog.apps.BlogConfig',
    
    'company.apps.CompanyConfig',
    'restaurant.apps.RestaurantConfig',
)

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'b_manager.middleware.TenantStatusMiddleware',
    "b_manager.middleware.CloudinaryTenantMiddleware",  
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",

]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,  # disable Django’s default loaders
        'OPTIONS': {
            'loaders': [
                ('baxting.tenant_loader.TenantTemplateLoader',),
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',



                
                'b_manager.context_processors.tenant',
            ],
        },
    },
]

WSGI_APPLICATION = 'baxting.wsgi.application'


CORS_ALLOWED_ORIGINS = [
    "http://opestore.localhost:8000",        # local tenant site
    #"http://tenant1.example.com",   # production tenant
]








CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:AvdWQBjGM3WIgJRUVu55zUqFVfYopupq@redis-12888.c44.us-east-1-2.ec2.cloud.redislabs.com:12888/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}



# optional — tell django-ratelimit which cache to use
RATELIMIT_CACHE = 'default'

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD':os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True
TENANT_MODEL = "b_manager.Client" # app.Model

TENANT_DOMAIN_MODEL = "b_manager.Domain"
PUBLIC_SCHEMA_URLCONF = 'baxting.urls'
ROOT_URLCONF = 'baxting.urls'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
# STATICFILES_DIRS = [
#     BASE_DIR / 'static',  # for development
# ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

PAYSTACK_SECRET_KEY =os.getenv('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')


# SESSION_COOKIE_DOMAIN = ".baxting.com"
FLW_PUBLIC_KEY=os.getenv('FLW_PUBLIC_KEY')
FLW_SECRET_KEY=os.getenv('FLW_SECRET_KEY')


# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
AUTH_USER_MODEL = 'b_manager.User'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"
PAYSTACK_INITIALIZE_URL=os.getenv('PAYSTACK_INITIALIZE_URL')
BASE_URL=os.getenv('BASE_URL')

FLW_SECRET_KEY =os.getenv('FLW_SECRET_KEY')




cloudinary.config(
    cloud_name="default_name",
    api_key="default_key",
    api_secret="default_secret",
    secure=True
)




if project==True:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",  # for static files
        },
    }


    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME') 
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_FILE_OVERWRITE = False
    # AWS_LOCATION ='media'
else:
    pass



GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
PAYSTACK_BASE_URL = os.getenv('PAYSTACK_BASE_URL')



# settings.py

# settings.py

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'

# # --- These three lines are the crucial change ---
# EMAIL_PORT = 465 
# EMAIL_USE_TLS = False  # MUST be False for port 465
# EMAIL_USE_SSL = True   # MUST be True for port 465
# # -----------------------------------------------

# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  
# DEFAULT_FROM_EMAIL = 'no-reply@baxting.com'







EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'

# --- These three lines are the crucial change ---
EMAIL_PORT = 465 
EMAIL_USE_TLS = False  # MUST be False for port 465
EMAIL_USE_SSL = True   # MUST be True for port 465
# -----------------------------------------------

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  
DEFAULT_FROM_EMAIL = 'no-reply@baxting.com'

ACCOUNT_LOGIN_METHODS = {"email"}

ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "username*",
    "password1*",
    "password2*",
]

ACCOUNT_UNIQUE_EMAIL = True
