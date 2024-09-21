from django.contrib.auth import views as auth_views

from django.urls import path
from .views import views, stripe_views

urlpatterns = [
    path('send-test-email', views.send_test_email),
    path('', views.log_in, name='login'),
    path('to_dos/<str:tag_unique_str>', views.to_dos, name='to_dos'),
    path('<int:id>/', views.details, name='details'),
    path('new_todo/', views.new_todo, name="new_todo"),
    path('delete_list/', views.delete_list, name='delete_list'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.log_in, name='login'),
    path('edit_todo/<int:id>', views.edit_todo, name='edit_todo'),
    path('delete_todo/<int:id>', views.delete_todo, name='delete_todo'),
    path('create_tag/', views.create_tag, name='create_tag'),
    path('access_tag/', views.access_tag, name='access_tag'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/my_password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/my_password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/my_password_reset_complete.html'), name='password_reset_complete'),   
    path('support/', stripe_views.SupportView.as_view(), name='support'),
    path('create-checkout-session/', stripe_views.CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('success/', stripe_views.SuccessView.as_view(), name='success'),
    path('cancel/', stripe_views.CancelView.as_view(), name='cancel'),
    path('stripe_webhook/', stripe_views.stripe_webhook_view, name='stripe_webhook'),
]
