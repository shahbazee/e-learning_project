import stripe
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from elearning_site.emails import send_contact_admin_email, send_receipt_email

from .forms import ContactForm
from .models import Course
from .serializers import CourseSerializer
from enrollments.models import Enrollment

User = get_user_model()

TRENDING_COURSE_COUNT = 4



def _enrolled_course_ids(user):
    """Ids of the courses the given user is already enrolled in."""
    if not user.is_authenticated:
        return set()
    return set(
        Enrollment.objects.filter(user=user).values_list("course_id", flat=True)
    )


def _search_courses(q):
    """Case-insensitive search over name, description and instructor."""
    queryset = Course.objects.all()
    q = (q or "").strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(instructor__icontains=q)
        )
    return queryset


def _course_list_context(request, courses, search_query=""):
    return {
        "courses": courses,
        "search_query": search_query,
        "enrolled_course_ids": _enrolled_course_ids(request.user),
    }


def home(request):
    courses = Course.objects.all()
    # Trending = most-enrolled courses, driven by live enrollment data.
    trending_courses = (
        Course.objects.annotate(enrollment_count=Count("enrollment"))
        .order_by("-enrollment_count", "-created_date")[:TRENDING_COURSE_COUNT]
    )
    return render(
        request,
        "courses/home.html",
        {
            "courses": courses,
            "trending_courses": trending_courses,
            "enrolled_course_ids": _enrolled_course_ids(request.user),
        },
    )


class CourseListView(ListView):
    model = Course
    template_name = "courses/courses_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        return _search_courses(self.request.GET.get("q"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = (self.request.GET.get("q") or "").strip()
        context["enrolled_course_ids"] = _enrolled_course_ids(self.request.user)
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/courses_detail.html"
    context_object_name = "course"
    pk_url_kwarg = "course_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_enrolled"] = (
            self.request.user.is_authenticated
            and Enrollment.objects.filter(
                user=self.request.user, course=self.object
            ).exists()
        )
        return context


def search_courses(request):
    query = (request.GET.get("q") or "").strip()
    return render(
        request,
        "courses/courses_list.html",
        _course_list_context(request, _search_courses(query), query),
    )


def filter_courses(request):
    course_type = (request.GET.get("course_type") or "").strip()
    if course_type:
        courses = Course.objects.filter(course_type=course_type)
    else:
        courses = Course.objects.all()

    return render(
        request,
        "courses/courses_list.html",
        _course_list_context(request, courses),
    )


def about(request):
    return render(request, "about.html")


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        message = form.save()
        send_contact_admin_email(message)
        messages.success(
            request,
            "Thank you! Your message has been sent. "
            "We usually reply within one business day.",
        )
        return redirect("contact")

    return render(request, "contact.html", {"form": form})

@api_view(['GET', 'POST'])
def course_list_api(request):

    if request.method == 'GET':
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)


        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = CourseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status= status.HTTP_404_NOT_FOUND
        )

    

@login_required
def create_checkout_session(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id,
        published_status=True
    )

    # Check if user is already enrolled
    already_enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).exists()

    if already_enrolled:
        messages.info(
            request,
            "You are already enrolled in this course.",
        )
        return redirect("courses_detail", course_id=course.id)

    # Free courses enroll directly - never go through Stripe.
    if course.price <= 0:
        return redirect("enroll_course", course_id=course.id)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],

        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": course.name,
                        "description": course.description,
                    },
                    "unit_amount": int(course.price * 100),
                },
                "quantity": 1,
            }
        ],

        mode="payment",

        success_url=(
            request.build_absolute_uri(
           "/payment-success/"
            )
            + "?session_id={CHECKOUT_SESSION_ID}"
            ),

        cancel_url=request.build_absolute_uri(
            f"/courses/{course.id}/"
        ),

        metadata={
            "course_id": str(course.id),
            "user_id": str(request.user.id),
        },
    )

    return redirect(
        checkout_session.url,
        code=303
    )


def _session_attr(session, name, default=None):
    """Read a field from a Stripe session object, webhook dict, or mock."""
    if isinstance(session, dict):
        return session.get(name, default)
    return getattr(session, name, default)


def _to_plain_dict(value):
    """Coerce a Stripe object (or dict) to a plain dict for safe .get() use.

    In stripe 15.x ``session.metadata`` and webhook events are
    ``StripeObject`` instances on which dict methods like ``.get()`` raise
    ``AttributeError``. ``.to_dict()`` gives a plain Python dict that can be
    used normally; plain dicts (webhook fixtures, tests) pass through.
    """
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return value
    return {}


def _fulfill_paid_checkout(session):
    """Shared fulfillment for a *verified, paid* Stripe Checkout Session.

    Used both by the user-facing ``payment_success`` page and by the Stripe
    ``checkout.session.completed`` webhook. It is fully idempotent:

      * it never creates a duplicate enrollment,
      * it sends the receipt email at most once, retrying on later calls
        if the first attempt failed (tracked via ``Enrollment.receipt_sent``).

    Returns a context dict, or ``None`` when the session is unusable
    (missing metadata / unknown user / unknown course).
    """
    metadata = _to_plain_dict(_session_attr(session, "metadata", None))
    user_id = metadata.get("user_id")
    course_id = metadata.get("course_id")
    if not user_id or not course_id:
        return None

    try:
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
    except (User.DoesNotExist, Course.DoesNotExist, ValueError, TypeError):
        return None

    enrollment, created = Enrollment.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            "status": "Active",
            "progress": 0,
        },
    )

    # Keep the enrollment active now that the payment is verified.
    status_changed = getattr(enrollment, "status", "") != "Active"
    if status_changed:
        enrollment.status = "Active"

    amount_paid = None
    raw_amount = _session_attr(session, "amount_total", None)
    if raw_amount is not None:
        amount_paid = Decimal(str(raw_amount)) / Decimal("100")

    payment_reference = (
        _session_attr(session, "payment_intent", None)
        or _session_attr(session, "id", None)
    )

    payment_date = None
    created_at = _session_attr(session, "created", None)
    if created_at:
        try:
            payment_date = datetime.fromtimestamp(int(created_at))
        except (TypeError, ValueError, OSError):
            payment_date = None

    # Idempotent receipt email: only when it has not been sent already,
    # and only mark it sent when the SMTP send really succeeded so a later
    # page refresh / webhook retry can try again. A failing email must
    # never break the customer's payment-success page.
    receipt_sent = bool(enrollment.receipt_sent)
    if not receipt_sent:
        try:
            receipt_sent = send_receipt_email(
                user,
                course,
                session,
                enrollment,
                amount_paid=amount_paid,
                payment_reference=payment_reference,
                payment_date=payment_date,
            )
        except Exception:  # noqa: BLE001 - success page must still render
            receipt_sent = False
        if receipt_sent:
            enrollment.receipt_sent = True
        if status_changed:
            enrollment.save(update_fields=["status", "receipt_sent"])
        else:
            enrollment.save(update_fields=["receipt_sent"])

    return {
        "user": user,
        "course": course,
        "enrollment": enrollment,
        "created": created,
        "already_enrolled": not created,
        "receipt_sent": receipt_sent,
        "customer_email": _session_attr(session, "customer_email", None)
        or user.email,
        "amount_paid": amount_paid if amount_paid is not None else course.price,
        "payment_reference": payment_reference or "—",
        "payment_date": payment_date or enrollment.enrollment_date,
    }


@login_required
def payment_success(request):

    session_id = request.GET.get("session_id")

    if not session_id:
        return render(
            request,
            "courses/payment_success.html",
            {
                "error": "Payment session not found."
            }
        )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Server-side verification - never trust the redirect URL alone.
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        return render(
            request,
            "courses/payment_success.html",
            {
                "error": "Could not verify your payment. Please contact support."
            }
        )

    if getattr(session, "payment_status", None) != "paid":
        return render(
            request,
            "courses/payment_success.html",
            {
                "error": "Payment was not completed."
            }
        )

    metadata = _to_plain_dict(getattr(session, "metadata", None))

    # The charged session must belong to the currently logged-in user.
    if str(metadata.get("user_id", "")) != str(request.user.id):
        return render(
            request,
            "courses/payment_success.html",
            {
                "error": "This payment session does not belong to your account."
            }
        )

    outcome = _fulfill_paid_checkout(session)
    if outcome is None:
        return render(
            request,
            "courses/payment_success.html",
            {
                "error": "Course not found for this payment."
            }
        )

    return render(
        request,
        "courses/payment_success.html",
        {
            **outcome,
            "payment_method": "Credit / Debit card (Stripe)",
            "site_url": request.build_absolute_uri("/"),
        },
    )


@require_POST
@csrf_exempt
def stripe_webhook(request):
    """Handle ``checkout.session.completed`` events from Stripe.

    This is the reliable path that guarantees enrollment + receipt email
    even when the customer closes the browser before the success redirect.
    It stays inactive until ``STRIPE_WEBHOOK_SECRET`` is configured in .env.
    """
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        return JsonResponse(
            {"error": "Stripe webhook is not configured on this server."},
            status=503,
        )

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except (ValueError, stripe.SignatureVerificationError):
        # Invalid signature / payload - refuse loudly.
        return HttpResponse(status=400)

    # In stripe 15.x the constructed event is a StripeObject (not a dict),
    # so read its fields the same safe way the session is read.
    if _session_attr(event, "type") == "checkout.session.completed":
        data = _session_attr(event, "data", {})
        session = _session_attr(data, "object", {})
        _fulfill_paid_checkout(session)

    return JsonResponse({"received": True})
