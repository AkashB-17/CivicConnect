# Email Configuration
# For development/testing, use the console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production with Gmail
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-actual-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'  # Note: changed from EMAIL_HOST_USER_PASSWORD
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER 