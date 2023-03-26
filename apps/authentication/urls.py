# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include
# from .views import login_view, register_user, change_password, delete_account,test
from . import views
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    # path("logout/", LogoutView.as_view(), name="logout"),
    # path("change_password/", change_password),
    # path("delete_account/", delete_account),
    # path('social_login/', include('allauth.urls')),
    path("home/", views.index, name="index"),
    path("auth0/login/", views.auth0login, name="auth0_login"),
    path("logout/", views.auth0logout, name="logout"),
    path("callback/", views.callback, name="callback"),
    # path("email/",views.email_send_test,name="email")
    path("test/",views.test_data, name="test_data" )
]


