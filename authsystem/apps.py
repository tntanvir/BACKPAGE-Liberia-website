from django.apps import AppConfig


class AuthsystemConfig(AppConfig):
    name = 'authsystem'

    def ready(self):
        import BackPage.signals
