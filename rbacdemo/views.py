from django.shortcuts import render,HttpResponse
from rbacdemo.models import User
from rbacdemo.service.permission import initial_session

# Create your views here.
def login(request):
    if request.method=="POST":
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")

        user = User.objects.filter(name=user,pwd=pwd).first()
        if user:
            request.session["user_id"] = user.pk
            #注册权限到session
            initial_session(user,request)
            return HttpResponse("登陆成功")
    return render(request,"login.html")





