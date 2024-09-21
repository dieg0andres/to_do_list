import stripe
from django.views.generic import TemplateView
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User


stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
YOUR_DOMAIN = settings.YOUR_DOMAIN



class SuccessView(TemplateView):

    template_name = 'stripe/success.html'

    def get_context_data(self, **kwargs):

        context = super(SuccessView, self).get_context_data(**kwargs)

        session_id = self.request.GET.get('session_id')
        
        if session_id:
            session = stripe.checkout.Session.retrieve(session_id)

            context.update({
                'metadata': session.metadata,
                'home_tag_unique_str': session.metadata.home_tag_unique_str,
            })

            return context
        
    


class CancelView(TemplateView):
    template_name = 'stripe/cancel.html'

    def get_context_data(self, **kwargs):
        context = super(CancelView, self).get_context_data(**kwargs)

        context.update({
            'home_tag_unique_str': self.request.session.get('home_tag_unique_str'),
        })

        return context
        


class SupportView(TemplateView):

    template_name = 'stripe/support.html'

    def get_context_data(self, **kwargs):

        context = super(SupportView, self).get_context_data(**kwargs)

        home_tag_unique_str = self.request.user.tags.get(name='Home').unique_str

        context.update({
            'home_tag_unique_str': home_tag_unique_str,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        })

        return context
    

class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):

        button_type = request.POST.get('button_type')
        home_tag_unique_str = request.user.profile.selected_tag_unique_str

        if button_type == 'support':
            amount = int(request.POST.get('amount', 100))
            product_name = 'Support'

        elif button_type == 'upgrade':
            amount = 500
            product_name = 'Upgrade'

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data' : {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'product_id': 'some important information goes here',
                'product_name': product_name,
                'amount': amount,
                'user_id': request.user.id,
                'home_tag_unique_str': home_tag_unique_str,
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )

        request.session['home_tag_unique_str'] = home_tag_unique_str
        
        return redirect(checkout_session.url, code=303)
    

def fulfill_checkout(session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    product_name = session.metadata.product_name
    amount = session.metadata.amount
    user_id = session.metadata.user_id
    user = User.objects.get(id=user_id)

    if session.payment_status == 'paid':
        print('Payment successful, made it here')
        print(session)

        if product_name == 'Support':
            user.profile.supported = True
            user.profile.amount_supported = amount
            user.profile.save()

        elif product_name == 'Upgrade':
            user.profile.upgraded = True
            user.profile.save()




@csrf_exempt
def stripe_webhook_view(request):

    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return HttpResponse(status=400)
    
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    if event.type == 'checkout.session.completed':
        session = event.data.object
        fulfill_checkout(session.id)
    
    return HttpResponse(status=200)
    
    