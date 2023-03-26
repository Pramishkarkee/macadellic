from django.http.response import HttpResponseNotFound, JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse, reverse_lazy
from .models import *
from django.views.generic import ListView, CreateView, DetailView, TemplateView
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from apps.auth import update_user_metadata
from django.core.mail import send_mail
# Create your views here.


def subscription_plane(request):
    return render(request,"checkouts/subscription.html")

@csrf_exempt
def subscription_checkout(request,id):
    price,name = subscription_price(id)
    print(settings.STRIPE_SECRET_KEY)
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        product = stripe.Product.create(name=name)
        price = stripe.Price.create(
            unit_amount=price,
            currency="INR",
            recurring={"interval": "day"},
            product=product.id,
        )
        checkout_session = stripe.checkout.Session.create(
            customer_email="karkipramish@gmail.com",
            payment_method_types=['card'],
            line_items=[{
                'price': price['id'],
                # For metered billing, do not pass quantity
                'quantity': 1
            }],
            metadata={
                'user_id': request.session['auth0']['userinfo']['sub'].replace('auth0|', '')
            },
            mode='subscription',
            success_url=request.build_absolute_uri(
                reverse('success')
            ) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse('failed')),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return HttpResponse("failed")

def subscription_price(id):
    if id=="1":
        return 300*100,"Starter"
    elif id=="2":
        return 600*100,"Professional"
    elif id=="3":
        return 900*100,"Business"
    else:
        return 1200*100,"Enterprise"


@csrf_exempt
def stripe_webhook(request):
    if request.method=='POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        try:
            event = json.loads(payload)
        except:
            print('⚠️  Webhook error while parsing basic request.')
            return HttpResponse(status=404)
        if endpoint_secret:
            # Only verify the event if there is an endpoint secret defined
            # Otherwise use the basic event deserialized with json
            sig_header = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            except stripe.error.SignatureVerificationError as e:
                print('⚠️  Webhook signature verification failed.' + str(e))
                return HttpResponse(status=404)
        if event and event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata']['user_id']
            stripe_customer_id = session['customer']
            updated_auth=update_user_metadata(user_id,stripe_customer_id)
            x = send_mail(
                subject="Here is your product",
                message=f"Thanks for your purchase. The URL is: http//:localhost",
                recipient_list=["karkipramish18@gmail.com"],
                from_email="tutee.line@gmail.com",
                fail_silently=False,
            )
        return HttpResponse(status=200)


class PaymentSuccessView(TemplateView):
    template_name = "checkouts/payment_success.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if session_id is None:
            return HttpResponseNotFound()

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)

        # order = get_object_or_404(OrderDetail, stripe_payment_intent=session.payment_intent)
        # order.has_paid = True
        # order.save()
        return render(request, self.template_name)

class PaymentFailedView(TemplateView):
    template_name = "checkouts/payment_failed.html"
