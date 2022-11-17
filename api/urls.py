from django.urls import path
from api import views
from api import tasks

urlpatterns = [
    path('company/<str:company>', views.company),
    path('companies/', views.companies),
    path('update/', views.update),
    path('update_companies/', views.update_companies),
    path('scan_market/', views.perform_market_scan),
    path('get_csrf_token/', views.get_csrf_token),
]