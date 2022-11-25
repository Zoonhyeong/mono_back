from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth.models import UserManager, AbstractUser
from datetime import datetime
# Create your models here.

class Member(AbstractUser):
    objects = UserManager()

    #username
    #first_name
    #last_name
    #email
    #password
    #groups
    #user_permission
    #is_staff
    #is_active
    #is_superuser
    #last_login
    #date_joined

    nickname = models.CharField(max_length=32)
    #자기소개 부분
    profile = models.TextField(blank=True, max_length=200)
    phone = models.CharField(max_length=16)
    
    profile_image = models.ImageField(blank=True, null=True)

    def __repr__(self):
        return f"{self.id}: {self.nickname}"

#구독 그룹
class Sub_group(models.Model):

    #그룹 이름
    group_name = models.CharField(max_length=32, blank=True, null=True)
    #그룹 색
    color = ColorField(default='#FFFFFF')

    def __repr__(self):
        return f"{self.group_name}"


#구독정보 
class Subscribe(models.Model):
    #아이콘 하나 만들기
    icon = models.ImageField(blank=True, null=True)
    #구독 외래키 - 유저를 참조 , 유저가 삭제되면 같이 삭제
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    #구독 그룹 외래키 - 구독 그룹을 참조, 그룹이 삭제되도 구독정보는 삭제X
    group = models.ForeignKey(Sub_group, on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=32)
    memo = models.TextField(blank=True, max_length=254)

    start_date = models.DateField(default=datetime.now)
    next_purchase_date = models.DateField()
    purchase_month = models.PositiveSmallIntegerField() # 0 to 32767
    purchase_date = models.PositiveSmallIntegerField()  # 0 to 32767


    purchase_price = models.BigIntegerField(default=0)
    sum_price = models.BigIntegerField(default=0)

    def __repr__(self):
        return f"{self.member}가 구독한 것 > {self.name}: {self.memo}"

#구독 탈퇴 정보
class Sub_cancellation(models.Model):
    #텍스트
    text = models.TextField(blank=True, max_length=254)
    #스크린 샷(주소)
    screenshot = models.URLField("screenshot url")
    #다음 탈퇴 정보 외래키
    next_cancel = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    #구독 정보 외래키
    subscribe = models.ForeignKey(Subscribe, on_delete=models.CASCADE, null=True)

    def __repr__(self):
        return f"{self.id}: {self.text}"

#구독 템플릿
class Sub_template(models.Model):
    #템플릿 이름
    temp_name = models.CharField(max_length=32, blank=True, null=True)
    #결제 금액
    purchase_price = models.BigIntegerField(default=0)
    #탈퇴 정보 외래키
    sub_cancel = models.ForeignKey(Sub_cancellation, on_delete=models.SET_NULL, null=True)
    def __repr__(self):
        return f"{self.temp_name}"