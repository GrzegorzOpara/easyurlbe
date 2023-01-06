from django.urls import path, include
from .views import (
    UrlListView,
    UrlDetailView,
    UserListView,
    UserDetailedView,
    UserPasswordChangeView
)

urlpatterns = [
    path('users/', UserListView.as_view()),
    path('users/delete', UserDetailedView.as_view()),
    path('users/changepassword', UserPasswordChangeView.as_view()),
    path('urls/', UrlListView.as_view()),
    path('urls/<int:url_id>/', UrlDetailView.as_view()),
]