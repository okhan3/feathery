from django.urls import path

from ai import views

urlpatterns = [
    path('', views.index, name='index'),
    path('extracted_info', views.extracted_info, name='extracted_info'),
]