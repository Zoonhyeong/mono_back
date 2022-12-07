from django.urls import path, include
from .views import Registration, Login, MemberListAPI, MemberAPI, SubscribeListAPI,SubscribeSidAPI, SubGroupListAPI, SubGroupSidAPI, SubscribeListAndGroupAPI, SubscribeCancelAPI, SummaryAPI
urlpatterns = [
    path('signup/', Registration.as_view()),
    path('signin/', Login.as_view()),
    path('members/', MemberListAPI.as_view()),
    path('members/<str:username>', MemberAPI.as_view()),
    path('members/<str:username>/subscribe', SubscribeListAPI.as_view()), 
    path('members/<str:username>/subscribe/<int:sid>', SubscribeSidAPI.as_view()),
    path('members/<str:username>/subscribes-groups', SubGroupListAPI.as_view()),
    path('members/<str:username>/subscribes-groups/<int:sid>', SubGroupSidAPI.as_view()),
    path('members/<str:username>/subscribe-lists', SubscribeListAndGroupAPI.as_view()),
    path('members/<str:username>/subscribe/<int:sid>/cancel', SubscribeCancelAPI.as_view()),
    path('members/<str:username>/summary', SummaryAPI.as_view())
]