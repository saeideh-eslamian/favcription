from django.urls import path
from scraper import views
from scraper.views import (
    YouTubeSubscriptionsView,
    GroupListCreateView,
    GroupRetrieveUpdateDestroyView,
    ChannelListView,
)

# app_name = "scraper"
urlpatterns = [
    path('subscriptions/', YouTubeSubscriptionsView.as_view(), name='youtube-subscriptions'),
    path('channels/', ChannelListView.as_view(),name='channels'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('test/', views.TestAPIView.as_view(), name='test_api_request'),
    path('authorize/', views.AuthorizeView.as_view(), name='authorize'),
    path('oauth2callback/', views.OAuth2CallbackView.as_view(), name='oauth2callback'),
    path('revoke/', views.RevokeView.as_view(), name='revoke'),
    path('clear/', views.ClearCredentialsView.as_view(), name='clear_credentials'),
]
