from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services_list, name='services'),
    path('faq/', views.faq, name='faq'),
    path('appointment/', views.appointment_view, name='appointment'),
    path('contact/', views.contact_view, name='contact'),
    path('cases/', views.cases_view, name='cases'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('cases/toggle-like/', views.toggle_like, name='toggle_like'),
    path('lawyers/<int:pk>/', views.lawyer_detail, name='lawyer_detail'),
        # Web Push endpoints
        path('webpush/vapid-public-key/', views.vapid_public_key, name='vapid_public_key'),
        path('webpush/save-subscription/', views.save_subscription, name='save_subscription'),
        path('webpush/delete-subscription/', views.delete_subscription, name='delete_subscription'),
        path('webpush/link-subscription/', views.link_subscription_to_user, name='link_subscription_to_user'),
    path('notifications/get/', views.get_notifications, name='get_notifications'),
    path('notifications/mark_read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/list/', views.notifications_list, name='notifications_list'),
    path('notifications/mark_all_read/', views.mark_all_read, name='notifications_mark_all_read'),
]
