#!/usr/bin/env python
"""Diagnose why the payment receipt email is not received.

Checks, in order:
  1. the effective email settings loaded from .env,
  2. the receipt templates render without error,
  3. the most recent enrollments and their ``receipt_sent`` flag,
  4. a real SMTP connection + a real receipt send to the configured mailbox.

Run with:  python diagnose_receipt.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elearning_site.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402
from django.core.mail import get_connection  # noqa: E402
from django.template.loader import render_to_string  # noqa: E402

from courses.models import Course  # noqa: E402
from elearning_site.emails import send_receipt_email  # noqa: E402
from enrollments.models import Enrollment  # noqa: E402


def line(title):
    print("\n" + "=" * 62)
    print(title)
    print("=" * 62)


line("1. EMAIL SETTINGS ACTUALLY LOADED")
print(f"   EMAIL_BACKEND       : {settings.EMAIL_BACKEND}")
print(f"   EMAIL_HOST          : {settings.EMAIL_HOST}")
print(f"   EMAIL_PORT          : {settings.EMAIL_PORT}")
print(f"   EMAIL_USE_TLS       : {settings.EMAIL_USE_TLS}")
print(f"   EMAIL_HOST_USER     : {settings.EMAIL_HOST_USER!r}")
pwd = settings.EMAIL_HOST_PASSWORD
print(f"   EMAIL_HOST_PASSWORD : {'set (' + str(len(pwd)) + ' chars)' if pwd else 'EMPTY !!'}")
print(f"   DEFAULT_FROM_EMAIL  : {settings.DEFAULT_FROM_EMAIL!r}")
print(f"   SITE_URL            : {settings.SITE_URL!r}")
print(f"   STRIPE_WEBHOOK_SECRET: {'set' if getattr(settings, 'STRIPE_WEBHOOK_SECRET', '') else 'EMPTY (webhook inactive)'}")

line("2. RECEIPT TEMPLATES RENDER")
enrollment = Enrollment.objects.select_related("user", "course").order_by("-id").first()
if enrollment is None:
    print("   ! No enrollment in the database to build a sample context.")
else:
    ctx = {
        "user": enrollment.user,
        "course": enrollment.course,
        "enrollment": enrollment,
        "amount_paid": enrollment.course.price,
        "payment_status": "Paid",
        "payment_reference": "pi_diagnostic",
        "payment_date": enrollment.enrollment_date,
        "payment_method": "Credit / Debit card (Stripe)",
        "site_url": settings.SITE_URL,
        "support_email": settings.DEFAULT_FROM_EMAIL,
        "site_name": "E-Learning Platform",
    }
    for tpl in ("emails/receipt.txt", "emails/receipt.html"):
        try:
            render_to_string(tpl, ctx)
            print(f"   OK  {tpl}")
        except Exception as exc:
            print(f"   FAIL {tpl}: {type(exc).__name__} - {exc}")

line("3. LAST 10 ENROLLMENTS (receipt flag + recipient address)")
rows = Enrollment.objects.select_related("user", "course").order_by("-id")[:10]
if not rows:
    print("   ! No enrollments found.")
for e in rows:
    print(
        f"   #{e.id:<4} user={e.user.username:<18} "
        f"email={(e.user.email or '<<EMPTY>>'):<32} "
        f"course={e.course.name[:22]:<22} receipt_sent={e.receipt_sent}"
    )

line("4. REAL SMTP CONNECTION TEST")
try:
    conn = get_connection(backend=settings.EMAIL_BACKEND)
    conn.open()
    print("   OK  SMTP login succeeded (credentials are valid).")
    conn.close()
    smtp_ok = True
except Exception as exc:
    smtp_ok = False
    print(f"   FAIL {type(exc).__name__}: {exc}")

line("5. REAL RECEIPT SEND (to the last enrollment's user)")
if enrollment is None:
    print("   Skipped - no enrollment.")
elif not smtp_ok:
    print("   Skipped - SMTP connection failed above.")
elif not enrollment.user.email:
    print(f"   Skipped - user '{enrollment.user.username}' has NO email address on the account.")
else:
    sent = send_receipt_email(
        enrollment.user,
        enrollment.course,
        enrollment=enrollment,
        amount_paid=enrollment.course.price,
        payment_reference="pi_diagnostic_test",
        payment_date=enrollment.enrollment_date,
    )
    print(f"   send_receipt_email(...) returned: {sent}")
    print(f"   recipient: {enrollment.user.email}")

print("\nDone.\n")
