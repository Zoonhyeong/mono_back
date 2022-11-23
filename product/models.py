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

class Subscribe(models.Model):
    #아이콘 하나 만들기
    icon = models.ImageField(blank=True, null=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)

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
