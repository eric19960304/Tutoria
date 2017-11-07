from django.contrib import admin
# Register your models here.

from .models import *

admin.site.register(Coupon)
admin.site.register(UserType)
admin.site.register(Profile)
admin.site.register(Tutor)
admin.site.register(TutorType)
admin.site.register(Student)
admin.site.register(System)
admin.site.register(Course)
admin.site.register(Tag)
admin.site.register(University)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Session)
admin.site.register(UnavailableTimeslot)
admin.site.register(Notification)
