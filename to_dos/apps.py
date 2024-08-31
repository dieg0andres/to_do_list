from django.apps import AppConfig


class ToDosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'to_dos'

    def ready(self):
        import to_dos.signals


