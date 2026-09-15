from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:course_id>/', views.CourseDetailView.as_view(), name='courses_detail'),
    path('search/', views.search_courses, name='search_courses'),
    path('filter/', views.filter_courses, name='filter_courses'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path(
    "course/<int:course_id>/checkout/",
    views.create_checkout_session,
    name="create_checkout_session"
),

path(
    "payment-success/",
    views.payment_success,
    name="payment_success"
),

path(
    "stripe/webhook/",
    views.stripe_webhook,
    name="stripe_webhook"
),

    path('api/courses/', views.course_list_api, name='course_list_api'),
]

