## 요구조건
- docker >= 1.12.0
- docker-compose >= 1.6.0

## 처음 실행

```
docker-compose up
```

```shell
"indocker"
python manage.py makemigrations <APPNAME>
python manage.py migrate

or

"shell"
docker -it exec <django container> python manage.py makemigrations <APPNAME>
docker -it exec <django container> python manage.py migrate
```



## 모델이 업데이트 되었을 떄

- django 도커 내부에서 아래 명령어 사용하기

```shell
python manage.py makemigrations <APPNAME>
python manage.py migrate
```


## 오류해결


- "python/r" 을 찾을 수 없다는 오류
  - CRLF, LF 문제니 git 설정을 아래와 같이 바꿀 것
  - 그리고 모든 파일의 포맷을 LF 포맷으로 바꿀 것
```
git config --global core.eol lf
git config --global core.autocrlf input
```

## 갑자기 접속이 안될경우

- docker에서 mysql을 먼저 실행한 후 django를 실행해볼 것