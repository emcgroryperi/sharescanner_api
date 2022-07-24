from django.urls import path
from api import views
from api import tasks

urlpatterns = [
    path('company/<str:company>', views.company),
    path('companies/', views.companies),
    path('update/', views.update),
    path('update_companies/', views.update_companies),
    path('ema_crossovers/', views.get_ema_crossovers),
]