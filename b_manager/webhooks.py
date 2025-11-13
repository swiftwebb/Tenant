# import json
# from django.http import JsonResponse, HttpResponse
# from datetime import date, timedelta
# from .models import Client, SubscriptionPlan
# from django.views.decorators.csrf import csrf_exempt





# @csrf_exempt
# def paystack_webhook(request):
#     """Process Paystack webhooks. Configure this URL in Paystack dashboard to point to
# https://website.baxting.com/customers/webhooks/paystack/ (or your domain).


# We expect metadata with tenant and plan_name inside the Paystack charge data.
# """
#     try:
#         payload = json.loads(request.body)
#     except Exception:
#         return HttpResponse(status=400)


#     event = payload.get('event')
#     data = payload.get('data') or {}


#     # Paystack event for successful charge
#     if event == 'charge.success':
#         metadata = data.get('metadata') or {}
#     # metadata might be JSON-string depending on how it was sent
#         if isinstance(metadata, str):
#             try:
#                 metadata = json.loads(metadata)
#             except Exception:
#                 metadata = {}


#         tenant_name = metadata.get('tenant')
#         plan_name = metadata.get('plan_name')


#         if not tenant_name or not plan_name:
#             return JsonResponse({'ok': False, 'reason': 'missing metadata'}, status=400)


#         try:
#             client = Client.objects.get(schema_name=tenant_name)
#             plan = SubscriptionPlan.objects.get(name=plan_name)
#         except Client.DoesNotExist:
#             return JsonResponse({'ok': False, 'reason': 'tenant not found'}, status=404)
#         except SubscriptionPlan.DoesNotExist:
#             return JsonResponse({'ok': False, 'reason': 'plan not found'}, status=404)


#         # Extend paid_until
#         today = date.today()
#         # If already has paid_until in future, extend from that date
#         base = client.paid_until if client.paid_until and client.paid_until >= today else today
#         client.paid_until = base + timedelta(days=plan.duration_days)
#         client.plan = plan
#         client.is_active = True
#         client.save()


#         return JsonResponse({'ok': True})


#     return JsonResponse({'ok': True})





# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.utils import timezone
from datetime import timedelta
from .models import *

@csrf_exempt
def paystack_webhook(request):
    try:
        payload = json.loads(request.body)
        event = payload.get('event')

        data = payload.get('data', {})
        metadata = data.get('metadata', {})
        tenant_name = metadata.get('tenant')
        plan_name = metadata.get('plan_name')

        tenant = Client.objects.filter(schema_name=tenant_name).first()
        plan = SubscriptionPlan.objects.filter(name=plan_name).first()

        if not tenant or not plan:
            return JsonResponse({'error': 'Invalid tenant or plan'}, status=400)

        # ✅ Handle recurring payment success
        if event in ['subscription.create', 'subscription.renewed', 'charge.success']:
            tenant.plan = plan
            tenant.paid_until = timezone.now() + timedelta(days=plan.duration_days)
            tenant.is_active = True
            tenant.save()

        # ❌ Handle failed payments
        elif event in ['invoice.payment_failed', 'subscription.not_renewed']:
            tenant.is_active = False
            tenant.save()
        
        PaystackEventLog.objects.create(event=event, raw_data=payload)


        return JsonResponse({'status': 'success'})
    

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
