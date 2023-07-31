from django.urls import path, include
from .views import *
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', pg_index),
    path('lav/<int:lav_id>/', pg_lav_page, name='lav_page'),
    path('add_rating/', pg_add_rating, name='add_rating'),
    path('lav_points/', pg_lav_points, name='lav_points'),
    path('add_form/', AddForm.as_view(redirect_authenticated_user=True), name='add_form'),
    path('edit_form/<int:lav_id>/', EditForm.as_view(redirect_authenticated_user=True), name='edit_form'),
    path('profile/', pg_profile, name='profile'),
    path('api/points/', pg_api_points),
    path('login/', MyLoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('signup/', Signup.as_view(redirect_authenticated_user=True), name = 'signup'),
    path('confirm_email/', TemplateView.as_view(template_name='registration/confirm_email.html'),
        name='confirm_email'),
    path('verify_email/<uidb64>/<token>/',
        EmailVerify.as_view(),
        name='verify_email',
        ),
    path('invalid_verify/',
        TemplateView.as_view(template_name='registration/invalid_verify.html'),
        name='invalid_verify'
        
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
