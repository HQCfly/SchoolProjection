
from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=32,verbose_name="用户名")
    pwd = models.CharField(max_length=32)
    roles = models.ManyToManyField(to="Role",verbose_name="用户角色")

    def __str__(self):
        return self.name
class Role(models.Model):
    title = models.CharField(max_length=32,verbose_name="角色标题")
    permissions = models.ManyToManyField(to="Permission")
    def __str__(self):
        return self.title

class Permission(models.Model):
    title = models.CharField(max_length=32,verbose_name="权限标题")
    url = models.CharField(max_length=64,verbose_name="权限范围")
    action = models.CharField(max_length=32, default="")
    group = models.ForeignKey("PermissionGroup", default=1,on_delete=models.CASCADE,)
    def __str__(self):
        return self.title

class PermissionGroup(models.Model):
    title = models.CharField(max_length=32,verbose_name="权限组")

    def __str__(self): return self.title

