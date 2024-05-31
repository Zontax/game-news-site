from django.urls import path

from users.views import UserRegisterView, UserLoginView, UserProfileView, ResetWaitView, UserRegisterConfirmView, PasswordResetView, UserPasswordResetConfirmView, UserLogoutView, UserDetailView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('register-wait/', ResetWaitView.as_view(), name='reset_wait'),
    path('register-confirm/<token>/', UserRegisterConfirmView.as_view(), name='register_confirm'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('detail/<str:username>/', UserDetailView.as_view(), name='detail'),
]
