# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
#
# Create your views here.
import http.client

from django.contrib.auth.forms import SetPasswordForm
from django.http import JsonResponse, HttpResponseRedirect,HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from .forms import LoginForm, SignUpForm
from apps.helpers import *
from apps import COMMON, helpers
# from django.settings import GITHUB_AUTH, TWITTER_AUTH

import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from stripe.error import SignatureVerificationError
import stripe
import requests
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from ..checkout.models import Product
from apps.auth_decorator import auth_decorator_func
from apps.auth import get_access_token,get_user_stripe_id_auth0,update_user_metadata


oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def auth0login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["auth0"] = token
    # print(request.build_absolute_uri(reverse("index")))
    return redirect("/")

def auth0logout(request):
    request.session.clear()
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("home")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )
def login_view(request):
    if "auth0" in request.session:
        return redirect("home/")
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":

        if form.is_valid():

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            # Credentials ok
            is_suspended = False
            if user:
                # Check Suspension state
                if user.status == COMMON.USER_SUSPENDED:
                    is_suspended = True
                    msg = 'Suspended account. Please contact support.'
                # All good
                else:

                    user.failed_logins = 0
                    user.save()
                    login(request, user)
                    return redirect("/")

            # Check user is registered
            user = username_exists(username)
            if not user:
                user = email_exists(username)
            # If user is suspended, don't check this case
            if not is_suspended:
                if user:

                    msg = 'Wrong password.'

                    # Update the fraud counter
                    user.failed_logins += 1

                    # Suspend the user (if needed)
                    if user.failed_logins > cfg_LOGIN_ATTEMPTS():
                        user.status = COMMON.USER_SUSPENDED
                        msg = 'Suspended account. Please contact support.'

                    # Update user
                    user.save()

                else:

                    msg = 'Username not registered.'

        else:
            msg = 'Error validating the form'
    else:
        msg = request.GET.get('message', None)

    return render(request, "accounts/login.html", {"form": form, "msg": msg,
                                                   # "github_login": GITHUB_AUTH,
                                                   "github_login":False,
                                                   "twitter_login": settings.TWITTER_AUTH,"auth0_login":True})


def register_user(request):
    msg = None
    success = False

    # new Registration
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():

            form.save()

            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")

            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

#
# def change_password(request, **kwargs):
#
#     form = SetPasswordForm(user=request.user, data=request.POST)
#     if form.is_valid():
#         user = form.save()
#         update_session_auth_hash(request, user)
#         message = 'Password successfully changed.'
#         status = 200
#     else:
#         message = form.errors
#         status = 400
#     return JsonResponse({
#         'message': message
#     }, status=status)
#
#
# def delete_account(request, **kwargs):
#     result, message = helpers.delete_user(request.user.username)
#     if not result:
#         return JsonResponse({
#             'errors': message
#         }, status=400)
#     logout(request)
#     return HttpResponseRedirect('home')
#
# def test(request):
#     return HttpResponse("jdjdj")

@auth_decorator_func
def index(request):
    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("auth0"),
            "pretty": json.dumps(request.session.get("auth0"), indent=4),
        },
    )

def home(request):
    return HttpResponse("htttp tesponse")


# @csrf_exempt
# def stripe_webhook(request):
#     if request.method=='POST':
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
#         payload = request.body
#         sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#         try:
#             event = json.loads(payload)
#         except:
#             print('⚠️  Webhook error while parsing basic request.')
#             return HttpResponse(status=404)
#         if endpoint_secret:
#             # Only verify the event if there is an endpoint secret defined
#             # Otherwise use the basic event deserialized with json
#             sig_header = request.headers.get('stripe-signature')
#             try:
#                 event = stripe.Webhook.construct_event(
#                     payload, sig_header, endpoint_secret
#                 )
#             except stripe.error.SignatureVerificationError as e:
#                 print('⚠️  Webhook signature verification failed.' + str(e))
#                 return HttpResponse(status=404)
#         if event and event['type'] == 'checkout.session.completed':
#             session = event['data']['object']
#             user_id = session['metadata']['user_id']
#             stripe_customer_id = session['customer']
#             update_user_metadata(user_id,stripe_customer_id)
#             x = send_mail(
#                 subject="Here is your product",
#                 message=f"Thanks for your purchase. The URL is: http//:localhost",
#                 recipient_list=["karkipramish18@gmail.com"],
#                 from_email="tutee.line@gmail.com",
#                 fail_silently=False,
#             )
#             print(x)
#         return HttpResponse(status=200)

def test_data(request):
    return render(request,"checkouts/subscription.html")