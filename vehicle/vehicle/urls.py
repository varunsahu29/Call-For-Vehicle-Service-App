"""vehicle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from vehicles import views
from django.contrib.auth.views import LoginView,LogoutView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name=''),

    path('customerclick/', views.customerclick_view,name='customerclick'),
    path('mechanicclick/', views.mechanicclick_view,name='mechanicclick'),
    
    path('customersignup/', views.customer_signup_view,name='customersignup'),
    path('mechanicsignup/', views.mechanic_signup_view,name='mechanicsignup'),

    path('customerlogin/', LoginView.as_view(template_name='vehicles/customer/login.html'),name='customerlogin'),
    path('mechaniclogin/', LoginView.as_view(template_name='vehicles/mechanic/login.html'),name='mechaniclogin'),
    path('adminlogin/', LoginView.as_view(template_name='vehicles/adminlogin.html'),name='adminlogin'),

    path('customer-dashboard/', views.customer_dashboard_view,name='customer-dashboard'),
    path('afterlogin/', views.afterlogin_view,name='afterlogin'),
    path('logout', LogoutView.as_view(template_name='vehicles/index.html'),name='logout'),
    path('customer-profile/', views.customer_profile_view,name='customer-profile'),

    path('edit-customer-profile', views.edit_customer_profile_view,name='edit-customer-profile'),
    path('customer-request', views.customer_request_view,name='customer-request'),
    path('customer-view-request',views.customer_view_request,name='customer-view-request'),
    path('customer-delete-request/<int:pk>', views.customer_delete_request_view,name='customer-delete-request'),
    path('customer-add-request',views.customer_add_request,name='customer-add-request'),
    path('customer-approved-request',views.customer_approved_request,name='customer-approved-request'),
    path('customer-approved-request-invoice',views.customer_approved_request_invoice,name='customer-approved-request-invoice'),
    path('customer-feedback', views.customer_feedback_view,name='customer-feedback'),

    path('aboutus', views.aboutus_view,name='aboutus'),
    path('contactus', views.contactus_view,name='contactus'),

    path('mechanic-dashboard', views.mechanic_dashboard_view,name='mechanic-dashboard'),
    path('mechanic-profile', views.mechanic_profile_view,name='mechanic-profile'),
    path('edit-mechanic-profile', views.edit_mechanic_profile_view,name='edit-mechanic-profile'),
    path('mechanic-work-assigned', views.work_assigned_view,name='mechanic-work-assigned'),
    path('mechanic-update-status/<int:pk>', views.update_status_view,name='mechanic-update-status'),
    path('mechanic-salary', views.salary_view,name='mechanic-salary'),
    path('mechanic-feedback', views.mechanic_feedback_view,name='mechanic-feedback'),
]
