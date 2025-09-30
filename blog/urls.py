from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('dev-check/', views.dev_check, name='dev_check'),
    path('page/', views.index_page, name='index_page'),
    # Detail page for editable lawyer cards (use PK to avoid slug conflicts)
    path('lawyer/<int:pk>/', views.lawyer_detail, name='lawyer_detail'),
    # Use str converter so Unicode slugs (e.g. Arabic) can be reversed and matched
    path('<str:slug>/', views.detail, name='detail'),
]
