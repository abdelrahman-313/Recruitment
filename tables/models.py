from django.db import models
from rest_framework import serializers


# Create your models here.
class Table(models.Model):
    name = models.CharField(max_length=255)

    def get_model(self):
        fields = Field.objects.filter(table=self)
        field_data = {
            "Meta": type("Meta", (), {"app_label": "tables"}),
            "__module__": "database.models",
        }
        for field in fields:
            if str(field.type).lower() == "string":
                field_data[field.name] = models.CharField(max_length=255)
            elif str(field.type).lower() == "boolen":
                field_data[field.name] = models.BooleanField()
            elif str(field.type).lower() == "number":
                field_data[field.name] = models.BigIntegerField()

        model = type(self.name, (models.Model,), field_data)
        return model

    def get_serializer(self):
        table_model = self.get_model()

        class DefaultSerializer(serializers.ModelSerializer):
            class Meta:
                model = table_model
                fields = "__all__"

        return DefaultSerializer


class Field(models.Model):
    table = models.ForeignKey(
        Table, on_delete=models.CASCADE, related_name="table_fields"
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=32)
