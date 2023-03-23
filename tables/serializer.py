from rest_framework import serializers
from django.db import models
from .models import Table, Field


class TableCreationSerializer(serializers.Serializer):
    table_name = serializers.CharField()
    fields = serializers.JSONField()

    def validate_table_name(self, value):
        from django.db import connection

        # tables_full_names = connection.introspection.table_names()
        # tables_names = [str(table).split("_")[1] for table in tables_full_names]

        # if value in tables_names:
        if Table.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"{value} already exists!")

        return value

    def validate_fields(self, obj):
        for key, value in obj.items():
            if str(value).lower() == "string" or str(value).lower() == "str":
                obj[key] = "string"
            elif str(value).lower() == "boolen" or str(value).lower() == "bool":
                obj[key] = "boolen"
            elif str(value).lower() == "number" or str(value).lower() == "num":
                obj[key] = "number"
            else:
                raise serializers.ValidationError(
                    f"field type ({value}) was not support thanks to enter vaild from given (string, boolen, number)"
                )
        return obj

    def get_fields_data(self):
        obj = self.data.get("fields")
        field_data = {
            "Meta": type("Meta", (), {"app_label": "tables"}),
            "__module__": "database.models",
        }

        for key, value in obj.items():
            if str(value).lower() == "string":
                field_data[key] = models.CharField(max_length=255)
            elif str(value).lower() == "boolen":
                field_data[key] = models.BooleanField()
            elif str(value).lower() == "number":
                field_data[key] = models.BigIntegerField()

        return field_data

    def save_table_details(self):
        table_name = self.data.get("table_name")
        fields = self.data.get("fields")

        table = Table.objects.create(name=table_name)
        for field_name, field_type in fields.items():
            Field.objects.create(table=table, name=field_name, type=field_type)

    def update_table_details(self, table_instance):
        table_name = self.data.get("table_name")
        if table_name:
            table_instance.name = table_name
            table_instance.save()
        fields = self.data.get("fields")
        if fields:
            for field_name, field_type in fields.items():
                Field.objects.create(
                    table=table_instance, name=field_name, type=field_type
                )


class RowCreationSerializer(serializers.Serializer):
    def __init__(self, instance=None, data=..., table_id=None, **kwargs):
        self.table_id = table_id
        super().__init__(instance, data, **kwargs)

    row = serializers.JSONField()

    def validate_row(self, value):
        table = Table.objects.get(id=self.table_id)
        for field_name, field_value in value.items():
            try:
                field = Field.objects.get(name=field_name, table=table)
            except Field.DoesNotExist:
                raise serializers.ValidationError(
                    f"field: {field_name} does not  exists!"
                )

            if (
                (field.type == "string" and isinstance(field_value, str))
                or (field.type == "number" and isinstance(field_value, int))
                or (field.type == "boolean" and isinstance(field_value, bool))
            ):
                return value
            else:
                raise serializers.ValidationError(
                    f"field: {field_name} accept only {field.type}"
                )


class RowDetailsSerializer(serializers.Serializer):
    rows = serializers.ListField()
