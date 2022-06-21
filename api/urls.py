from django.urls import path
from api import views
from api import tasks

urlpatterns = [
    path('company/', views.company),
    path('companies/', views.companies),
    path('update/', views.update),
]