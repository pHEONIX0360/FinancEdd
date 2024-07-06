from django.contrib import admin
from .models import Course, Student, User

# Register your models here.
admin.site.register(User)
admin.site.register(Student)
admin.site.register(Course)