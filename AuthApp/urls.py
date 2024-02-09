from django.urls import path
from AuthApp.views import SignUp, SignIn, Profile, ChangePassword, SendPasswordResetEmail, PasswordReset

urlpatterns = [
    # Create your url here.
    path("signup/", SignUp.as_view(), name="signup"),
    path("signin/", SignIn.as_view(), name="signin"),
    path("profile/", Profile.as_view(), name="profile"),
    path("changepassword/", ChangePassword.as_view(), name="changepassword"),
    path("reset-password-email/", SendPasswordResetEmail.as_view(), name="reset-password-email"),
    path("reset-password/<uid>/<token>/", PasswordReset.as_view(), name="reset-password"),

]
