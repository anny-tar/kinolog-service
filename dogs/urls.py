from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),

    path('dogs/', views.dog_list, name='dog_list'),
    path('dogs/add/', views.dog_add, name='dog_add'),
    path('dogs/<int:pk>/', views.dog_detail, name='dog_detail'),
    path('dogs/<int:pk>/edit/', views.dog_edit, name='dog_edit'),

    path('trainings/', views.training_list, name='training_list'),
    path('trainings/add/', views.training_add, name='training_add'),

    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.event_add, name='event_add'),

    path('vet/', views.vet_list, name='vet_list'),
    path('vet/add/', views.vet_add, name='vet_add'),

    path('employees/', views.employee_list, name='employee_list'),

    path('reports/', views.report_list, name='report_list'),
    path('reports/generate/', views.report_generate, name='report_generate'),
]