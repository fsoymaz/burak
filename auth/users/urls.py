from django.urls import path, include  # include fonksiyonunu ekledik
from .views import RegisterView, LoginView,  LogoutView ,TwoFactor, TwoFactorActive, Login42View, QRCodeURL, UpdateUser, SendFriendRequestView, AcceptFriendRequestView , DeclineFriendRequestView, Uploadpp
from .views import InvitationsView, FriendsListView, BlockedFriendRequestView, BlockedListView, UnblockFriendView
from .views import  UserStatus
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    #path('user/', UserView.as_view(), name='user'),
    path('2fa/', TwoFactor.as_view(), name='2fa'),
    path('2faactive/', TwoFactorActive.as_view(), name='2faactive'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login42/', Login42View.as_view(), name='login42'),
    path('updateuser/', UpdateUser.as_view(), name='updateuser'),
	path('qrUrl/', QRCodeURL.as_view(), name='qrUrl'),
	path('uploadpp/', Uploadpp.as_view(), name='uploadpp'),
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/accept/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friend-request/decline/', DeclineFriendRequestView.as_view(), name='decline-friend-request'),
    path('friend-request/blocked/', BlockedFriendRequestView.as_view(), name="blocked-friend-reqest"),
    path('friend-request/unblock/', UnblockFriendView.as_view(), name='unblock-friend'),
    path('friend-request/blocked-list/', BlockedListView.as_view(), name='blocked-friend-list'),
    path('friend-request/invitations/', InvitationsView.as_view(), name='get-invitations'),
    path('friend-request/friends/', FriendsListView.as_view(), name='get-friends-list'),
    path('user-status/<str:username>/', UserStatus.as_view(), name='user-status'),
]