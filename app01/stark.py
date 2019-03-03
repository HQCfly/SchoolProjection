from datetime import datetime, timedelta

from stark.service.stark import starkSite,ModelStark
from django.db.models import Q
from .models import *
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.http import JsonResponse

from django.shortcuts import HttpResponse, redirect, render

starkSite.register(School)

class UserConfig(ModelStark):
    list_display = ["name","email","depart"]

starkSite.register(UserInfo,UserConfig)

class ClassConfig(ModelStark):
    def display_classname(self,obj=None,header=None):
        if header:
            return "班级名称"
        class_name = "%s(%s)"%(obj.course.name,str(obj.semester))
        return class_name
    list_display = [display_classname,"tutor","teachers"]

starkSite.register(ClassList,ClassConfig)

class CusotmerConfig(ModelStark):
    def display_gender(self, obj=None, header=None):
        if header:
            return "性别"
        return obj.get_gender_display()


    def display_course(self,obj=None,header=None):
        if header:
            return "咨询课程"
        temp=[]
        for course in obj.course.all():
            s = "<a href='/stark/app01/customer/cancel_course/%s/%s' style='border:1px solid #369;padding:3px 6px'><span>%s</span></a>&nbsp;"%(obj.pk,course.pk,course.name)
            temp.append(s)
        return mark_safe("".join(temp))

    list_display = ["name", display_gender, display_course, "consultant", ]

    def cancel_course(self, request, customer_id, course_id):
        print(customer_id, course_id)

        obj = Customer.objects.filter(pk=customer_id).first()
        obj.course.remove(course_id)
        return redirect(self.get_list_url())

    def public(self,request,):

        now = datetime.now()
        delta_day3 = timedelta(days=3)
        delta_day15 = timedelta(days=15)
        user_id = request.session.get("user_id")
        # user_id = request.session["user_id"]
        customer_list=Customer.objects.filter(Q(last_consult_date=now-delta_day3)|Q(recv_date__lt=now-delta_day15),status=2,).exclude(consultant=user_id)
        print(user_id)


        return render(request,"public.html",locals())
    def further(self,request,customer_id):
        user_id = request.session.get("user_id")
        now = datetime.now()
        delta_day3 = timedelta(days=3)
        delta_day15 = timedelta(days=15)
        ret = Customer.objects.filter(pk=customer_id).filter(Q(last_consult_date=now-delta_day3)|Q(recv_date__lt=now-delta_day15),status=2,).update(consultant=user_id,last_consult_date=now,recv_date__lt=now)
        if not ret:
            return HttpResponse("已经被跟进")
        CustomerDistrbute.objects.create(customer_id=customer_id,consultant_id=user_id,date=now,status=1)

        return HttpResponse("跟进成功")

    def mycustomer(self,request):
        user_id = request.session.get("user_id")
        customer_distrbute_list=CustomerDistrbute.objects.filter(consultant=user_id)
        return render(request,"mycustomers.html",locals())

    def extra_url(self):

        temp = []

        temp.append(url(r"cancel_course/(\d+)/(\d+)", self.cancel_course))
        temp.append(url(r"public/", self.public))
        temp.append(url(r"further/(\d+)", self.further))
        temp.append(url(r"mycustomer/", self.mycustomer))

        return temp



starkSite.register(Customer,CusotmerConfig)
starkSite.register(Department)
starkSite.register(Course)
class ConsultConfig(ModelStark):
    list_display = ["customer","consultant","date","note"]



starkSite.register(ConsultRecord,ConsultConfig)

class StudentConfig(ModelStark):
    def score_view(self,request,sid):
        if request.is_ajax():
            sid = request.GET.get("sid")
            cid = request.GET.get("cid")
            study_record_list = StudyRecord.objects.filter(student=sid,course_record__class_obj=cid)
            data_list = []
            for study_record in study_record_list:
                day_num = study_record.course_record.day_num
                data_list.append(["day%s"%day_num,study_record.score])
            return JsonResponse(data_list,safe=False)
        else:
            student = Student.objects.filter(pk=sid).first()
            class_list = student.class_list.all()
            return render(request, "score_view.html", locals())
    def extra_url(self):
        temp=[]
        temp.append(url(r"score_view/(\d+)", self.score_view))
        return temp

    def score_show(self,obj=None,header=False):
        if header:
            return "查看成绩"
        return mark_safe("<a href='/stark/app01/student/score_view/%s'>查看成绩</a>"%obj.pk)
    list_display = ["customer","class_list",score_show]
    list_display_links = ["customer"]
starkSite.register(Student,StudentConfig)
class CouseRecordConfig(ModelStark):
    def score(self,request,course_record_id):
        if request.method =="POST":
            data={}
            for key,value in request.POST.items():
                if key == "csrfmiddlewaretoken":continue
                field, pk = key.rsplit("_",1)
                if pk in data:
                    data[pk][field]=value
                else:
                    data[pk]={field:value}
            for pk,update_data in data.items():
                StudyRecord.objects.filter(pk=pk).update(**update_data)
            return redirect(request.path)
        else:

            student_record_list = StudyRecord.objects.filter(course_record=course_record_id)
            score_choices =StudyRecord.score_choices
            return render(request,"score_view.html",locals())

    def extra_url(self):

        temp = []
        temp.append(url(r"record_score/(\d+)", self.score))
        return temp

    def record(self, obj=None, header=False):
        if header:
            return "学习记录"
        return mark_safe("<a href='/stark/app01/studyrecord/?course_record=%s'>记录</a>" % obj.pk)

    def record_score(self, obj=None, header=False):
        if header:
            return "录入成绩"
        return mark_safe("<a href='record_score/%s'>录入成绩</a>" % obj.pk)

    list_display = ["class_obj", "day_num", "teacher", record, record_score]

    def patch_studyrecord(self, request, queryset):
        print(queryset)
        temp = []
        for course_record in queryset:
            # 与course_record关联的班级对应所有学生
            student_list = Student.objects.filter(class_list__id=course_record.class_obj.pk)
            for student in student_list:
                obj = StudyRecord(student=student, course_record=course_record)
                temp.append(obj)
        StudyRecord.objects.bulk_create(temp)

    patch_studyrecord.short_description = "批量生成学习记录"
    actions = [patch_studyrecord, ]
starkSite.register(CourseRecord,CouseRecordConfig)
class StudyConfig(ModelStark):
    list_display = ["student", "course_record", "record", "score"]

    def patch_late(self, request, queryset):
        queryset.update(record="late")

    patch_late.short_description = "迟到"
    actions = [patch_late]


starkSite.register(StudyRecord, StudyConfig)
starkSite.register(CustomerDistrbute)




