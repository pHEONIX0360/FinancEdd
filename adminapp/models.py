from django.db import models

# Create your models here.
from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        STUDENT = "STUDENT", 'Student'

    base_role = Role.ADMIN
    role = models.CharField(max_length=100, choices=Role.choices)
    short_name = models.CharField(max_length=2, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        if self.first_name:
            self.short_name = self.first_name[0] + self.first_name[-1]
        super().save(*args, **kwargs)

class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset()
        return result.filter(role=User.Role.STUDENT)

class Student(User):
    base_role = User.Role.STUDENT

    class Meta:
        proxy = True

    student = StudentManager()

    def welcome(self):
        return "Only for Students"
    
class Course(models.Model):
    course_name = models.CharField(max_length=30,blank=False,null=False,unique=True)
    duration=models.CharField(max_length=20)
    discription=models.TextField()
class Video(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')
    def __str__(self):
        return self.title


# class Post(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

# class Comment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

# class Like(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)    