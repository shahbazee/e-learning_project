"""Central email helpers for the E-Learning platform.

All user-facing emails are sent through these helpers so that:
  * recipients, subjects and messages stay consistent,
  * every HTML email also carries a plain-text fallback,
  * send failures are logged (not raised) so a flaky SMTP
    connection never breaks a user flow.
"""
import logging
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _send_html_email(subject, recipient_list, template_name, context):
    """Render ``<template_name>.html`` + ``.txt`` and send a multipart email."""
    context.setdefault("site_name", "E-Learning Platform")
    try:
        text_body = render_to_string(f"{template_name}.txt", context)
        html_body = render_to_string(f"{template_name}.html", context)
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as exc:  # noqa: BLE001 - defensive: never break the user flow
        logger.warning(
            "Failed to send email '%s' to %s: %s", subject, recipient_list, exc
        )
        return False


def send_welcome_email(user):
    """Sent once the user activates their account through email OTP."""
    return _send_html_email(
        "Welcome to E-Learning Platform — Your account is active!",
        [user.email],
        "emails/welcome",
        {"user": user},
    )


def send_password_reset_confirmation_email(user):
    """Sent after a successful password reset."""
    return _send_html_email(
        "Your E-Learning password has been reset",
        [user.email],
        "emails/password_reset_confirmation",
        {"user": user},
    )


def send_receipt_email(
    user,
    course,
    session=None,
    enrollment=None,
    amount_paid=None,
    payment_reference=None,
    payment_date=None,
):
    """Send a payment receipt after a verified, successful Stripe payment.

    Returns ``True`` when the email left the server, ``False`` when it could
    not be sent (the caller can then retry later - delivery is tracked by
    ``Enrollment.receipt_sent``).
    """
    payment_status = "Paid"

    if session is not None:
        if amount_paid is None:
            raw_amount = getattr(session, "amount_total", None)
            if raw_amount is not None:
                amount_paid = Decimal(str(raw_amount)) / Decimal("100")
        if payment_reference is None:
            payment_reference = (
                getattr(session, "payment_intent", None) or getattr(session, "id", None)
            )
        if payment_date is None:
            created_at = getattr(session, "created", None)
            if created_at:
                try:
                    payment_date = datetime.fromtimestamp(int(created_at))
                except (TypeError, ValueError, OSError):
                    payment_date = None
        # Prefer the email used on the Stripe checkout, falling back to the
        # account email the user signed up with.
        if getattr(session, "customer_email", None):
            user.email = session.customer_email

    context = {
        "user": user,
        "course": course,
        "enrollment": enrollment,
        "amount_paid": amount_paid if amount_paid is not None else course.price,
        "payment_status": payment_status,
        "payment_reference": payment_reference or "—",
        "payment_date": payment_date or getattr(enrollment, "enrollment_date", None),
        "payment_method": "Credit / Debit card (Stripe)",
        "site_url": settings.SITE_URL,
        "support_email": settings.DEFAULT_FROM_EMAIL,
    }
    return _send_html_email(
        f"Payment Receipt — {course.name}",
        [user.email],
        "emails/receipt",
        context,
    )


def send_contact_admin_email(message):
    """Notify the site administrator about a new contact-form submission."""
    recipient = settings.ADMIN_EMAIL or settings.EMAIL_HOST_USER
    if not recipient:
        logger.warning("No admin email configured; contact submission not emailed.")
        return False
    return _send_html_email(
        f"New contact message: {message.subject}",
        [recipient],
        "emails/contact_admin",
        {"message": message},
    )