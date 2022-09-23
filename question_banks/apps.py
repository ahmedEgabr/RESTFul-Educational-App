from django.apps import AppConfig


class QuestionBanksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'question_banks'

    def ready(self):
        from . import signals
