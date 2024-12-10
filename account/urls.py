from django.urls import path
from account.views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, SendPasswordResetEmailView, UserPasswordResetView, SendOTPView, VerifyOTPView, CorrespondenceAddressView, ResidentialAddressView, EducationDetailsAppearingView, EducationDetailsPassedView, ProfileCompletionView

urlpatterns = [

    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-email-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-email-password-email'),
    path('reset-password/<uid>/<token>', UserPasswordResetView.as_view(), name='reset-password'),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('correspondence-address/', CorrespondenceAddressView.as_view(), name='correspondence-address'),
    path('residential-address/', ResidentialAddressView.as_view(), name='residential-address'),
    path('education-details-appearing/', EducationDetailsAppearingView.as_view(), name='education-details-appearing'),
    path('education-details-passed/', EducationDetailsPassedView.as_view(), name='education-details-passed'),
    path('profile-completion-status/', ProfileCompletionView.as_view(), name='profile-completion-status'),





]
