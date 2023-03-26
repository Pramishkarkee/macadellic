from django.shortcuts import redirect
from apps.auth import get_user_stripe_id_auth0
from django.conf import settings
import stripe

def auth_decorator_func(func):
    def wrapper_func(request, *args, **kwargs):
        if "auth0" in request.session:
            token = request.session['auth0']
            stripe_id = get_user_stripe_id_auth0(token['userinfo']['sub'])
            try:
                if stripe_id.get("status") == "failed":
                    return redirect('subscription/')
            except:
                pass
            if stripe_id:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                subscription = stripe.Subscription.list(
                    customer=stripe_id,
                    status='active',
                    limit=1
                )
                if subscription:
                    return func(request, *args, **kwargs)
            else:
                return redirect("subscription/")
            return func(request, *args, **kwargs)
        else:
            return redirect("login/")


    return wrapper_func