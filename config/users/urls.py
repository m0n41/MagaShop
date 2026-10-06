from django.urls import path
from .views import (
    LoginUser, RegisterUser, ProfileDetail,
    ProfileUserUpdate, ProfileAddressUpdate, 
    UserPasswordChange, UserPasswordChangeDone,
    UserPasswordResetDone, UserPasswordReset,
    UserPasswordResetComplete, UserPasswordResetConfirm,
    BecomeSalaryView, BecomeSalaryCompleteView, RecentViewsView,
    BecomeSalaryConfirmView,
)
from django.contrib.auth.views import LogoutView

app_name = 'users'

urlpatterns = [
    path("login/", LoginUser.as_view(), name="login"),
    path("register/", RegisterUser.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileDetail.as_view(), name="profile"),
    path("views/", RecentViewsView.as_view(), name="views_list"),
    path("profile-edit/", ProfileUserUpdate.as_view(), name="profile_edit"),
    path("profile-edit/address/", ProfileAddressUpdate.as_view(), name="profile_edit_address"),
    path("password-change/", UserPasswordChange.as_view(), name="password_change"),
    path("password-change/done/", UserPasswordChangeDone.as_view(), name="password_change_done"),
    path("password-reset/", UserPasswordReset.as_view(), name="password_reset"),
    path("password-reset/done/", UserPasswordResetDone.as_view(), name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/", UserPasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path("password-reset/complete/", UserPasswordResetComplete.as_view(), name="password_reset_complete"),
    path("become_salary/", BecomeSalaryView.as_view(), name="become_salary"),
    path("become_salary/complete/", BecomeSalaryCompleteView.as_view(), name="become_salary_complete"),
    path("become_salary/confirm/", BecomeSalaryConfirmView.as_view(), name="become_salary_confirm"),
]
