from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.PlacementLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.complete_profile_view, name='complete_profile'),
    path('apply/<int:company_id>/', views.apply_view, name='apply'),
    path('company/', views.company_dashboard_view, name='company_dashboard'),
    path('company/application/<int:application_id>/', views.company_update_application_view, name='company_update_application'),
]
