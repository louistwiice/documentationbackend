import environ


env = environ.Env(DEBUG=(bool, False))

# ===== Django settings
SECRET_KEY = env('SECRET_KEY', default="1234566svsfhgfsqdvjhsbdsjfjfnj")
DJANGO_SETTINGS_MODULE = env('DJANGO_SETTINGS_MODULE', default="config.settings.production")
ENVIRONMENT = DJANGO_SETTINGS_MODULE.split('.')[-1]
SERVER_IP = env("SERVER_IP", default='http://127.0.0.1:8000')
SWAGGER_BASE_URL = env("SWAGGER_BASE_URL", default='http://localhost')  # IP Address of Nginx would be great

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default='127.0.0.1,localhost').split(",")
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['http://127.0.0.1'])
CORS_ORIGIN_WHITELIST = env.list("DJANGO_CORS_ORIGIN_WHITELIST", default=[])

POSTGRES_USER = env('POSTGRES_USER', default="postgres")
POSTGRES_PASSWORD = env('POSTGRES_PASSWORD', default="postgres")
POSTGRES_DB = env('POSTGRES_DB', default="docs")
POSTGRES_HOST = env('POSTGRES_HOST', default="postgres")
POSTGRES_PORT = env.int('POSTGRES_PORT', default=5423)

USE_SQLITE = env.bool('USE_SQLITE', default=False)
DATABASE_SQLITE = env.db_url('DATABASE_SQLITE', default="sqlite:///db.sqlite3")

# ====== JWT settings
ACCESS_TOKEN_LIFETIME_MINUTES = env.int('ACCESS_TOKEN_LIFETIME_MINUTES', default=60*3)  # default 3h
REFRESH_TOKEN_LIFETIME_DAYS = env.int('REFRESH_TOKEN_LIFETIME_DAYS', default=2)  # default 1 Day
AUTH_HEADER_TYPES = env('AUTH_HEADER_TYPES', default='Bearer')
VERIFYING_KEY = env('VERIFYING_KEY', default='2356777sgqhghhjqjh)°)q1ér2567788')

# ===== Email settings
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.office365.com')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='git@wizall.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='Qar63072')

# ===== Log formatter
LOG_FORMATTER = env("LOG_FORMATTER", default='colored')

# ===== Swagger settings

