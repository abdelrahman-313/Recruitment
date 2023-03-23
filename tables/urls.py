from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path("api/table", views.TableListApiView.as_view()),
    path("api/table/<int:table_id>/", views.TableDetailApiview.as_view()),
    path("api/table/<int:table_id>/row", views.RowListApiView.as_view()),
]
