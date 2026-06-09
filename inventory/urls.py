from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/add/', views.equipment_create, name='equipment_create'),
    path('equipment/<slug:slug>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/<slug:slug>/edit/', views.equipment_update, name='equipment_update'),
    path('equipment/<slug:slug>/delete/', views.equipment_delete, name='equipment_delete'),

    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
]
