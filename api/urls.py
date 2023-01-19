from django.urls import path, include
from .views import (
    UrlListView,
    UrlDetailView,
    UserListView,
    UserDetailedView,
    UserPasswordChangeView,
    PasswordReset,
    ResetPassword,
)

urlpatterns = [
    path('users/', UserListView.as_view()),
    path('users/details/', UserDetailedView.as_view()),
    path('users/change-password/', UserPasswordChangeView.as_view()),
    path('users/request-password-reset/', PasswordReset.as_view(), name='request-password-reset'),
    path('users/password-reset/<str:encoded_pk>/<str:token>/', ResetPassword.as_view(), name='password-reset'),
    path('urls/', UrlListView.as_view()),
    path('urls/<int:url_id>/', UrlDetailView.as_view()),
]