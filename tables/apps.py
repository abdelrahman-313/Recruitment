from django.apps import AppConfig


class TablesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tables"

    def ready(self):
        original_register_model = self.apps.register_model

        def register_model(app_label, model):
            if not hasattr(model, "_generated_table_model"):
                original_register_model(app_label, model)
            else:
                self.apps.do_pending_operations(model)
                self.apps.clear_cache()

        self.apps.register_model = register_model
