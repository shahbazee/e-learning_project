import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elearning_site.settings")
django.setup()

from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

print("stripe version:", stripe.VERSION)
print("has top-level StripeObject:", hasattr(stripe, "StripeObject"))
try:
    so_cls = stripe.StripeObject
except Exception as e:
    so_cls = None
    print("stripe.StripeObject attr error:", e)
if so_cls is not None:
    print("StripeObject class:", so_cls, so_cls.__module__)

# ---- 1) Create + retrieve a real test Checkout Session (no charge) ----
print("\n== REAL STRIPE TEST SESSION ==")
try:
    sess = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Metadata Probe Course"},
                    "unit_amount": 500,
                },
                "quantity": 1,
            }
        ],
        success_url="https://example.com/payment-success/?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://example.com/cancel/",
        metadata={"course_id": "2", "user_id": "75"},
    )
    print("created session:", sess.id)
    print("metadata type:", type(sess.metadata), "- value:", sess.metadata)

    retrieved = stripe.checkout.Session.retrieve(sess.id)
    md = retrieved.metadata
    print("retrieved metadata type:", type(md))
    try:
        print("  md.get('user_id') ->", md.get("user_id"))
    except Exception as e:
        print("  md.get('user_id') RAISED:", type(e).__name__, "-", str(e)[:120])
    print("  md['user_id']       ->", md["user_id"])
    print("  md.user_id (attr)   ->", md.user_id)
    print("  md.to_dict()        ->", md.to_dict() if hasattr(md, "to_dict") else "no to_dict")
    print("  md type check... isinstance dict:", isinstance(md, dict), "has get:", hasattr(md, "get"))
except Exception as e:
    print("STRIPE API TEST FAILED:", type(e).__name__, "-", str(e)[:300])

# ---- 2) What does construct_event return? ----
print("\n== WEBHOOK EVENT TYPE ==")
try:
    from stripe._webhook import WebhookSignature
    payload = b'{"type": "checkout.session.completed", "data": {"object": {"id": "cs_test_wh", "metadata": {"course_id": "2", "user_id": "75"}}}}'
    secret = "whsec_this_is_a_test_secret_for_inspection"
    sig_header = WebhookSignature.generate_signature_header(payload, secret)
    evt = stripe.Webhook.construct_event(payload, sig_header, secret)
    print("event type:", type(evt))
    print("  is StripeObject:", isinstance(evt, so_cls) if so_cls is not None else "n/a")
    try:
        print("  evt.get('type') ->", evt.get("type"))
    except Exception as e:
        print("  evt.get('type') RAISED:", type(e).__name__, "-", str(e)[:120])
    print("  evt.type (attr)       ->", evt.type)
    obj = evt.data.object
    print("  data.object type:", type(obj), "| metadata type:", type(obj.metadata))
    try:
        print("  obj.metadata.get('user_id') ->", obj.metadata.get("user_id"))
    except Exception as e:
        print("  obj.metadata.get RAISED:", type(e).__name__, "-", str(e)[:120])
    print("  obj.metadata.to_dict() ->", obj.metadata.to_dict() if hasattr(obj.metadata, "to_dict") else obj.metadata)
except Exception as e:
    print("WEBHOOK TEST FAILED:", type(e).__name__, "-", str(e)[:300])