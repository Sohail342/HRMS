from urllib.parse import urlparse
from pathlib import Path
import cloudinary
import os
from dotenv import load_dotenv
load_dotenv()
from django.urls import reverse_lazy
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG") == 'True'

ALLOWED_HOSTS = ["127.0.0.1",'.vercel.app', os.getenv("ALLOW_HOST")]



LOGIN_URL = reverse_lazy('account:login')
LOGIN_REDIRECT_URL = reverse_lazy('HRMS:home')


# Application definition

INSTALLED_APPS = [
    'unfold',
    'hide_admin.apps.HideAdminConfig',

    # default apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    
    # Third party apps
    'tailwind',
    'django_browser_reload',
    'import_export',
    "widget_tweaks",
    'cloudinary',
    
    # project apps
    'HRIS_App',
    'reporting',
    'account',
    'transfer_employees',
    'group_head',
    'employee_user',
    'employee_attendance',
    'employee_search',
]


MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

if os.getenv("DATABASE_NAME"):
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

MIDDLEWARE += [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    'django.middleware.cache.FetchFromCacheMiddleware', 
]

ROOT_URLCONF = 'HRMS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'HRMS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


# Get DATABASE_URL from environment
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Parse the DATABASE_URL
if DATABASE_NAME:

    # FOR VERCEL DATABASE (Testing)
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DATABASE_NAME"),
        'USER': os.getenv("DATABASE_USER"),
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        'HOST': os.getenv("DATABASE_HOST"),
        'OPTIONS': {'sslmode': 'require'},
    }
}
else:
    # Fallback for Production DATABASE (VPS)
    DATABASES = {
    'default': {
        'ENGINE': os.getenv("PRO_DATABASE_ENGINE"),
        'NAME': os.getenv("PRO_DATABASE_NAME"),
        'USER': os.getenv("PRO_DATABASE_USER"),
        'PASSWORD': os.getenv("PRO_DATABASE_PASSWORD"),
        'HOST': os.getenv("PRO_DATABASE_HOST"),
        'PORT': os.getenv("PRO_DATABASE_PORT"),
    }
}



# Custom Employee Model
AUTH_USER_MODEL = 'HRIS_App.Employee'


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


if os.getenv("DATABASE_NAME"):
    
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
  
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Increase the maximum number of fields
DATA_UPLOAD_MAX_NUMBER_FIELDS = 9000 


# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret"),
    secure=True  
)


# Unfold Admin Configuration
UNFOLD = {
    "SITE_TITLE": "HRMS - HR Management System",
    "SITE_HEADER": "HRMS",
    "SITE_SUBHEADER": "HR Management System",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("HRIS_App/images/icon-light.svg"),  # light mode
        "dark": lambda request: static("HRIS_App/images/icon-dark.svg"),  # dark mode
    },
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": _("My site"),
            "link": "https://example.com",
        },
        {
            "icon": "diamond",
            "title": _("My site"),
            "link": reverse_lazy("admin:index"),
        },
    ],
    "SITE_LOGO": {
        "light": lambda request: static("HRIS_App/images/logo-light.svg"),  # light mode
        "dark": lambda request: static("HRIS_App/images/logo-dark.svg"),  # dark mode
    },
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("HRIS_App/images/favicon.png"),
        },
    ],
    "STYLES": [
        lambda request: static("HRIS_App/css/style.css"),
        lambda request: static("HRIS_App/css/import-export-buttons.css"),
        lambda request: static("HRIS_App/css/import-export-pages.css"),
    ],
    "SCRIPTS": [
        lambda request: static("HRIS_App/JS/script.js"),
        lambda request: static("HRIS_App/JS/import-form-enhancer.js"),
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "BORDER_RADIUS": "6px",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Dashboard"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
        ],
        "navigation": [
            {
                "title": _("Dashboard"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("HR Management System"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Employees"),
                        "icon": "people",
                        "link": reverse_lazy("admin:HRIS_App_employee_changelist"),
                    },
                    {
                        "title": _("Group"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:HRIS_App_group_changelist"),
                    },
                    {
                        "title": _("Division"),
                        "icon": "apartment",
                        "link": reverse_lazy("admin:HRIS_App_division_changelist"),
                    },
                    {
                        "title": _("Wing"),
                        "icon": "account_tree",
                        "link": reverse_lazy("admin:HRIS_App_wing_changelist"),
                    },
                    {
                        "title": _("Region"),
                        "icon": "public",
                        "link": reverse_lazy("admin:HRIS_App_region_changelist"),
                    },
                    {
                        "title": _("Branch"),
                        "icon": "fork_right",
                        "link": reverse_lazy("admin:HRIS_App_branch_changelist"),
                    },
                    {
                        "title": _("Designation"),
                        "icon": "badge",
                        "link": reverse_lazy("admin:HRIS_App_designation_changelist"),
                    },
                    {
                        "title": _("Cadre"),
                        "icon": "group_work",
                        "link": reverse_lazy("admin:HRIS_App_cadre_changelist"),
                    },
                    {
                        "title": _("EmployeeType"),
                        "icon": "work_outline",
                        "link": reverse_lazy("admin:HRIS_App_employeetype_changelist"),
                    },
                    {
                        "title": _("EmployeeGrade"),
                        "icon": "star_half",
                        "link": reverse_lazy("admin:HRIS_App_employeegrade_changelist"),
                    },
                    {
                        "title": _("Qualification"),
                        "icon": "school",
                        "link": reverse_lazy("admin:HRIS_App_qualification_changelist"),
                    },
                ],
            },
            {
                "title": _("Employee Management"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("RICP Details"),
                        "icon": "insights",
                        "link": reverse_lazy("admin:employee_user_ricpdata_changelist"),
                    },
                    {
                        "title": _("RICP KPI's"),
                        "icon": "trending_up",
                        "link": reverse_lazy("admin:employee_user_ricpkpi_changelist"),
                    },
                    {
                        "title": _("Leave Application"),
                        "icon": "event_note",
                        "link": reverse_lazy("admin:employee_attendance_leaveapplication_changelist"),
                    },
                    {
                        "title": _("Non-Involvement Certificate"),
                        "icon": "verified_user",
                        "link": reverse_lazy("admin:employee_attendance_noninvolvementcertificate_changelist"),
                    },
                    {
                        "title": _("Educational Documents"),
                        "icon": "school",
                        "link": reverse_lazy("admin:employee_attendance_educationaldocument_changelist"),
                    },
                    {
                        "title": _("Contract Renewal"),
                        "icon": "autorenew",
                        "link": reverse_lazy("admin:employee_attendance_contractrenewal_changelist"),
                    },
                    {
                        "title": _("Stationary Request"),
                        "icon": "edit_note",
                        "link": reverse_lazy("admin:employee_attendance_stationaryrequest_changelist"),
                    },
                    {
                        "title": _("Transfer Inquiry"),
                        "icon": "swap_horiz",
                        "link": reverse_lazy("admin:transfer_employees_inquiry_changelist"),
                    },
                ],
            },
            {
                "title": _("Letter Templates"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Purpose of Letter"),
                        "icon": "local_hospital",
                        "link": reverse_lazy("admin:reporting_purpose_changelist"),
                    },
                    {
                        "title": _("Hospital Names"),
                        "icon": "local_hospital",
                        "link": reverse_lazy("admin:reporting_hospitalname_changelist"),
                    },
                    {
                        "title": _("Saved Templates"),
                        "icon": "save",
                        "link": reverse_lazy("admin:reporting_lettertemplates_changelist"),
                    },
                    {
                        "title": _("Permanent Saved Letter Templates"),
                        "icon": "drafts",
                        "link": reverse_lazy("admin:reporting_permenantlettertemplates_changelist"),
                    },
                    {
                        "title": _("Signature on Letter"),
                        "icon": "draw",
                        "link": reverse_lazy("admin:reporting_signature_changelist"),
                    },
                ],
            },
        ],

    },
}



