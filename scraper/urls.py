from django.urls import path
from scraper.api import (
    AuthorizeView,
    RefreshTokenView,
    OAuth2CallbackView,
    RevokeView,
    YouTubeSubscriptionsView,
)
from scraper.views import (
    GroupListCreateView,
    GroupRetrieveUpdateDestroyView,
    ChannelView,
    VideoListView,
)

urlpatterns = [
    path('channels/', ChannelView.as_view(), name='channels'),
    path('groups/', GroupListCreateView.as_view(), name='groups'),
    path('group/<int:pk>/', GroupRetrieveUpdateDestroyView.as_view(),
         name='group-detail'),
    path('videos/', VideoListView.as_view(), name='video-list-create'),

    path('subscriptions/', YouTubeSubscriptionsView.as_view(),
         name='youtube-subscriptions'),
    path('authorize/', AuthorizeView.as_view(),
         name='authorize'),  # login with google
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('oauth2callback/', OAuth2CallbackView.as_view(),
         name='oauth2callback'),
    path('revoke/', RevokeView.as_view(), name='revoke'),  # logout
]
