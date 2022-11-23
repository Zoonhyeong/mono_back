from django.urls import path, include
from .views import Registration, Login, MemberListAPI, MemberAPI, SubscribeListAPI

urlpatterns = [
    path('signup/', Registration.as_view()),
    path('signin/', Login.as_view()),
    path('members/', MemberListAPI.as_view()),
    path('members/<str:username>', MemberAPI.as_view()),
    path('members/<str:username>/subscribe', SubscribeListAPI.as_view())
]