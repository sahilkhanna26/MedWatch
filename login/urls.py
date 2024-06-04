from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views


app_name = "login"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('custom_redirect/', views.custom_redirect, name='custom_redirect'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('login:index')), name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='account_login'),
    path("report/", views.report, name="report"),
    path("report/submitted/", views.ReportDone.as_view(), name="report_done"),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('report/<int:report_id>/resolve/', views.resolve_report, name='resolve_report'),
    path('report/<int:report_id>/delete/', views.delete_report, name='delete_report'),
]