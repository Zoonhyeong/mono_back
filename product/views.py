from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework import generics # generics class-based view 사용할 계획
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer


from datetime import datetime
from dateutil.relativedelta import relativedelta

from .serializers import MemberRegisterSerializer, MemberLoginSerializer, MemberSerializer, SubscribeSerializer, SubGroupSerializer
from .models import Member, Subscribe, SubGroup, SubCancellation, SubTemplate
from .utils import process_filter, process_sorted

# Create your views here.

# 누구나 접근 가능
@permission_classes([AllowAny]) 
class Registration(generics.GenericAPIView):
    serializer_class = MemberRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({"message": "Request Body Error."}, status=status.HTTP_409_CONFLICT)

        serializer.is_valid(raise_exception=True)

        member = serializer.save(request) # request 필요 -> 오류 발생

        return Response(
            {
            # get_serializer_context: serializer에 포함되어야 할 어떠한 정보의 context를 딕셔너리 형태로 리턴
            # 디폴트 정보 context는 request, view, format
                "member": MemberSerializer(
                    member, context=self.get_serializer_context()
                ).data
            },
                status=status.HTTP_201_CREATED,
        )

@permission_classes([AllowAny])
class Login(generics.GenericAPIView):
    serializer_class = MemberLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid(raise_exception=True):
            return Response({"message": "Request Body Error."}, status=status.HTTP_409_CONFLICT)

        serializer.is_valid(raise_exception=True)
        member = serializer.validated_data
        if member['username'] == "None":
            return Response({"message": "fail"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "member": MemberLoginSerializer(
                    member, context=self.get_serializer_context()
                ).data
            }
        )

#멤버 리스트를 위한 API
@permission_classes([AllowAny])
class MemberListAPI(generics.GenericAPIView):
    serializer_class = MemberSerializer
    queryset = ""

    def get(self, request):
        """
        API형식
        GET /members?
                    query=<table id>&           기준 정렬은 없는 것이 기본
                    asc=<int:0, 1::default=0>&  내림차순이 기본
                    offset=<int::default=0>&    0번 부터 불러오는 것이 기본
                    limit=<int::default = 10>   최대 10까지 불러오는 것이 기본
        """
        queryset = Member.objects.all()
        queryset = process_filter(request, queryset, 
            is_active=("__is_active", bool, True)
        )
        queryset = process_sorted(request, queryset,
            target=[
                ("query", None, "asc", False),
            ],
            offset=0,                               
            limit=10,
        )
        serializer = MemberSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        #many=True면 배열을 기대한다.
        serializer = MemberSerializer(data=request.data)

        #유효성 확인
        if(not serializer.is_valid()):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=201)

#단일 멤버를 위한 API
@permission_classes([AllowAny])
class MemberAPI(generics.GenericAPIView):
    serializer_class = MemberSerializer
    queryset = ""
    def get(self, request, username):
        queryset = Member.objects.get(username=username)
        serializer = MemberSerializer(queryset)
        return Response(serializer.data, status=200)

    def put(self, request, username): 
        #예외처리하기 key값이 없는거라던가
        original_query = Member.objects.get(username=username)
        original_object = MemberSerializer(original_query).data
        
        update_object = {k: v and v or original_object.get(k, '') for k, v in request.data.items()}

        serializer = MemberSerializer(update_object)

        Member.objects.filter(username=username).update(**serializer.data)
        return Response(status=200)

    def delete(self, request, username):
        #실제로 데이터를 없애진 말자
        Member.objects.filter(username=username).update(is_active=False)
        return Response(status=200)

#구독 리스트를 위한 API
@permission_classes([AllowAny])
class SubscribeListAPI(generics.GenericAPIView):
    serializer_class = SubscribeSerializer
    queryset = ""

    def get(self, request, username):
        """
        API형식
        GET /members?
                    query=<table id>&           기준 정렬은 없는 것이 기본
                    asc=<int:0, 1::default=0>&  내림차순이 기본
                    offset=<int::default=0>&    0번 부터 불러오는 것이 기본
                    limit=<int::default = 10>   최대 10까지 불러오는 것이 기본
        """

        #정렬관련 쿼리 
        #?query=username&asc=0&offset=0&limit=3
        #정렬할 대상
        #query = request.GET.get('query', None)                              

        #해당하는 유저를 찾는다.
        member = Member.objects.get(username=username)
        member = MemberSerializer(member).data

        queryset = Subscribe.objects.all()
        #filter processing
        queryset = process_filter(request, queryset, 
            member_id=("__member_id", int, member.get("id", None)),
            id=("id", int, None)
        )
        queryset = process_sorted(request, queryset,
            target=[
                ("target1", None, "rev1", False),   #target1 기준 정렬, 오름차순
                ("target2", None, "rev2", False),   #target2 기준 정렬, 내림차순
            ],
            offset=0,                               #조회페이지 디폴트값
            limit=10,
        )

        serializer = SubscribeSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, username):
        #요청한 유저를 찾는다.
        member = Member.objects.get(username=username)
        member = MemberSerializer(member).data

        next_purchase_date = datetime.now()

        now = datetime.now()
        pmonth = int(request.data.get("purchase_month", 0))
        pday = int(request.data.get("purchase_date", 0))

        #이미 지난날이면
        if now.day >= pday:
            next_purchase_date = datetime.now() + relativedelta(months=pmonth)

        next_purchase_date = next_purchase_date.replace(day=pday)

        #왜 이렇게 이중으로 바꿔야 하는지 이해를 못함
        data = {k: v for k, v in request.data.items()}
        print(member)
        data["icon"] = None
        data["member"] = member.get("id", None)
        data["next_purchase_date"] = next_purchase_date.date().strftime('%Y-%m-%d')
        data["sum_price"] =0

        print(data)
        
        serializer = SubscribeSerializer(data=data)
        serializer.member = member.get("id", None)
        serializer.next_purchase_date = next_purchase_date.date().strftime('%Y-%m-%d')
        serializer.sum_price = 0

        #유효성 확인
        if(not serializer.is_valid()):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data, status=201)


#sid값 구독정보를 위한 API
@permission_classes([AllowAny])
class SubscribeSidAPI(generics.GenericAPIView):
    serializer_class = SubscribeSerializer
    queryset = ""

    def get(self, request, username, sid):
        #모든 구독 정보를 불러오고 id값에 맞는 구독 정보를 넘겨준다
        queryset = Subscribe.objects.get(id=sid)
        serializer = SubscribeSerializer(queryset)
        return Response(serializer.data, status=200)

    def put(self, request, username, sid): 
        #변경점 업데이트
        serializer = SubscribeSerializer(request.data)
        Subscribe.objects.filter(id=sid).update(serializer.data)

        return Response(status=200)

    def delete(self, request, username, sid):
        #삭제
        Subscribe.objects.filter(id=sid).delete()
        return Response(status=200)

#그룹 리스트를 위한 API
@permission_classes([AllowAny])
class SubscribeGroupListAPI(generics.GenericAPIView):
    serializer_class = SubGroupSerializer
    queryset = ""

    def get(self, request, username):
        #그룹 리스트를 불러온다.
        queryset = SubGroup.objects.all()

        serializer = SubGroupSerializer(queryset, many=True)

        return Response(serializer.data, status=200)

    def post(self, request, username):
        #해당하는 유저를 찾는다.
        member = Member.objects.get(username=username)
        member = MemberSerializer(member).data

        serializer = SubGroupSerializer(data=request.data)

        #유효성 확인
        if(not serializer.is_valid()):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=201)

#sid값 구독그룹를 위한 API
@permission_classes([AllowAny])
class SubGroupSidAPI(generics.GenericAPIView):
    serializer_class = SubGroupSerializer
    queryset = ""

    def get(self, request, username, sid):
        #모든 그룹 정보를 불러오고 id값에 맞는 그룹 정보를 넘겨준다
        queryset = SubGroup.objects.get(id=sid)
        serializer = SubGroupSerializer(queryset)
        return Response(serializer.data, status=200)

    def put(self, request, username, sid):
        #변경점 업데이트
        SubGroup.objects.filter(id=sid).update(**request.data)

        return Response(status=200)

    def delete(self, request, username, sid):
        #삭제
        SubGroup.objects.filter(id=sid).delete()
        return Response(status=200)


#구독, 그룹 리스트를 위한 API
@permission_classes([AllowAny])
class SubscribeListAndGroupAPI(generics.GenericAPIView):
    serializer_class = SubscribeSerializer
    queryset = ""

    def get(self, request, username):
        #요청한 유저를 찾는다.
        member = Member.objects.get(username=username)
        member = MemberSerializer(member).data
        
        #subscribe 쿼리셋
        queryset_subscribe = Subscribe.objects.all()
        queryset_subscribe = queryset_subscribe.filter(member_id=member.get("id", None))

        sublist = SubscribeSerializer(queryset_subscribe, many=True).data

        #SubGroup 쿼리셋
        queryset_sub_group = SubGroup.objects.all()
        groups = [
            queryset_sub_group.filter(data["group"]) for data in sublist if data.get("group", None)
        ]

        
        result = sublist + groups
        return Response(result, status=200)

#구독 취소 리스트 API
@permission_classes([AllowAny])
class SubscribeCancelAPI(generics.GenericAPIView):
    serializer_class = SubscribeSerializer
    queryset = ""
    def get(self, request, username, sid):

        result = []

        queryset = SubCancellation.objects.all()
        queryset = queryset.filter(subscribe=sid)

        result = list(queryset)

        return Response(result, status=200)