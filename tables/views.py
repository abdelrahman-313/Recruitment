from django.shortcuts import render
from django.db import models, connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import (
    TableCreationSerializer,
    RowCreationSerializer,
    RowDetailsSerializer,
)
from .models import Table
import json

# Create your views here.


class TableListApiView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TableCreationSerializer(data=request.data)
        if serializer.is_valid():
            table = type(
                request.data.get("table_name"),
                (models.Model,),
                serializer.get_fields_data(),
            )
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(table)
            serializer.save_table_details()

        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"details": "Table Created Successfully."})


class TableDetailApiview(APIView):
    def get_object(self, table_id):
        try:
            return Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return None

    def put(self, request, table_id, *args, **kwargs):
        """
        Updates the todo item with given todo_id if exists
        """
        table_instance = self.get_object(table_id)
        if not table_instance:
            return Response(
                {"res": "Object with todo id does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TableCreationSerializer(data=request.data)
        if serializer.is_valid():
            table = type(
                request.data.get("table_name"),
                (models.Model,),
                serializer.get_fields_data(),
            )
            with connection.schema_editor() as schema_editor:
                schema_editor.alter_db_table(
                    table,
                    "tables_" + table_instance.name,
                    "tables_" + request.data.get("table_name"),
                )
            serializer.update_table_details(table_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RowListApiView(APIView):
    def get_object(self, table_id):
        try:
            return Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return None

    def get(self, request, table_id, *args, **kwargs):
        table_instance = self.get_object(table_id)
        if not table_instance:
            return Response(
                {"res": "Object with table id does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        table_model = table_instance.get_model()
        rows = table_model.objects.all()
        default_serializer = table_instance.get_serializer()

        serializer = default_serializer(rows, many=True)

        return Response(serializer.data)

    def post(self, request, table_id, *args, **kwargs):
        table_instance = self.get_object(table_id)
        if not table_instance:
            return Response(
                {"res": "Object with table id does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RowCreationSerializer(data=request.data, table_id=table_id)
        if serializer.is_valid():
            table_model = table_instance.get_model()
            table_model.objects.create(**serializer.data.get("row"))

        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"details": "Row Created Successfully."})
