from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-change-me-later-for-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # Разрешаем все хосты для разработки

# Application definition
INSTALLED_APPS = [  
    'jazzmin',# <--- ВАЖНО: Jazzmin должен быть ПЕРВЫМ!
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- МОИ ПРИЛОЖЕНИЯ (MODULES) ---
    'core',       # Главная страница и общие функции
    'users',      # Пользователи, роли (Студент/Учитель)
    'courses',    # Уроки, видео, тесты
    'analytics',  # ML и статистика
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qadam.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Указываем папку templates в корне
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.unread_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'qadam.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qadam_db',
        'USER': 'postgres',
        'PASSWORD': 'aldi2138D', # Тот самый, что вводил в pgAdmin
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Password validation
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
LANGUAGE_CODE = 'ru-ru'  # Ставим русский язык
TIME_ZONE = 'Asia/Almaty' # Твой часовой пояс
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Добавляем вот эту строку (это папка, куда сервер соберет все файлы):
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [BASE_DIR / 'static']  # Папка static в корне

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- ВАЖНАЯ НАСТРОЙКА: ПОЛЬЗОВАТЕЛЬ ---
AUTH_USER_MODEL = 'users.CustomUser'

# --- НАСТРОЙКИ ПОЧТЫ (SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'aldiargabitov53@gmail.com'
EMAIL_HOST_PASSWORD = 'ewij ieqd fzck mpod' 

AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',  # Наш новый способ
    'django.contrib.auth.backends.ModelBackend', # Стандартный
]

# Медиа файлы (для картинок курсов и видео)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- ПЕРЕАДРЕСАЦИЯ ---
LOGIN_REDIRECT_URL = '/'  
LOGOUT_REDIRECT_URL = '/'


# ==========================================
# НАСТРОЙКИ JAZZMIN (КРАСИВАЯ АДМИНКА)
# ==========================================
JAZZMIN_SETTINGS = {
    # Заголовки
    "site_title": "QADAM Admin",
    "site_header": "QADAM",
    "site_brand": "QADAM Education",
    "welcome_sign": "Добро пожаловать в панель управления QADAM",
    "copyright": "Qadam Project Ltd",
    "changeform_format": "horizontal_tabs",
    
    # Аватарка и поиск
    "search_model": "users.CustomUser",
    "user_avatar": "avatar",

    # 🔥 ПРЯЧЕМ ЛИШНИЕ ТАБЛИЦЫ ИЗ БОКОВОГО МЕНЮ 🔥
    "hide_models": ["courses.Question", "courses.Choice"],

    # Меню
    "topmenu_links": [
        {"name": "Главная", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Открыть сайт", "url": "/", "new_window": True},
    ],

    # Иконки (FontAwesome)
    "icons": {
        "auth": "fas fa-users-cog",
        "users.CustomUser": "fas fa-user",
        "courses.Course": "fas fa-graduation-cap",
        "courses.Lesson": "fas fa-book-open",
        "courses.LessonProgress": "fas fa-chart-line",
    },
    
    # Порядок приложений в меню
    "order_with_respect_to": ["users", "courses", "analytics", "auth"],
}

# --- ИСПРАВЛЕННЫЙ ЦВЕТОВОЙ КОНФИГ (Текст будет виден!) ---
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",  # Белая шапка, темный текст
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-primary",     # Светлый сайдбар, темный текст
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "theme": "spacelab",                    # Контрастная тема
    "dark_mode_theme": None,                # Отключаем темную тему в админке
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}