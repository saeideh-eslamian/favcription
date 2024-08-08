from django.urls import path
from scraper import views
from scraper.views import (
    YouTubeSubscriptionsView,
    GroupListCreateView,
    GroupRetrieveUpdateDestroyView,
    ChannelListView,
    RefreshTokenView,
)

# app_name = "scraper"
urlpatterns = [
    path('subscriptions/', YouTubeSubscriptionsView.as_view(), name='youtube-subscriptions'),
    path('channels/', ChannelListView.as_view(),name='channels'),
    path('authorize/', views.AuthorizeView.as_view(), name='authorize'), # login with google
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('oauth2callback/', views.OAuth2CallbackView.as_view(), name='oauth2callback'),
    path('revoke/', views.RevokeView.as_view(), name='revoke'), # logout
]
