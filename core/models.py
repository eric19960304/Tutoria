from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from pytz import timezone
from tutoriabeta import settings

# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone



class Tag(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return str(self.id)+": "+self.name

class University(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return str(self.id)+": "+self.name

class TutorType(models.Model):
    tutor_type =  models.CharField(max_length=10)
    def __str__(self):
        return str(self.id)+": "+self.tutor_type

class UserType(models.Model):
    user_type =  models.CharField(max_length=10)
    def __str__(self):
        return str(self.id)+": "+self.user_type


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    user_type =  models.ForeignKey(UserType, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id)+": "+self.user.username+"'s profile"

class Transaction(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="profile_transaction" )
    involved_profile = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="involved_profile_transaction", null=True, blank=True)
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    isDebit = models.BooleanField()
    to_or_from_system = models.BooleanField(default=False)
    to_or_from_bank = models.BooleanField(default=False)
    description = models.CharField(max_length=50, blank=False,null=True)
    def __str__(self):
        return str(self.id)+": "+self.profile.user.username+"'s transaction"

class Course(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id)+": "+self.name


class Student(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    university = models.OneToOneField(University, on_delete=models.CASCADE, blank=True,null=True)
    def __str__(self):
        return str(self.id)+": "+self.profile.user.username

class Tutor(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    tutor_type =  models.ForeignKey(TutorType, on_delete=models.CASCADE, blank=True, null=True )
    hourly_rate = models.IntegerField(blank=True,null=True) 
    tags = models.ManyToManyField(Tag, blank=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, blank=True,null=True)
    courses = models.ManyToManyField(Course, blank=True)
    bio = models.CharField(max_length=500, blank=True,null=True)
    def __str__(self):
        return str(self.id)+": "+self.profile.user.username
    def checkProfileComplete():
        percent = { 'tutor_type': 25, 'hourly_rate': 25, 'university': 15, 'bio': 15, 'courses': 10, 'tags': 10}
        total = 0
        if self.tutor_type:
            total += percent.get('tutor_type', 0)
        if self.hourly_rate:
            total += percent.get('hourly_rate', 0)
        if self.university:
            total += percent.get('university', 0)
        if self.bio:
            total += percent.get('bio', 0)
        if self.courses:
            total += percent.get('courses', 0)
        if self.tags:
            total += percent.get('tags', 0)
        return "%s"%(total)
        

class UnavailableTimeslot(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    def __str__(self):
        local_timezone = timezone(settings.TIME_ZONE)
        t_start = self.start_time.astimezone(local_timezone)
        t_end = self.end_time.astimezone(local_timezone)
        return str(self.id)+": "+self.tutor.profile.user.username + ": " +t_start.strftime('%Y-%m-%d %H:%M')+" - "+t_end.strftime('%Y-%m-%d %H:%M')

class Session(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    booking_date = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10,default="booked")
    def __str__(self):
        return str(self.id)+": "+self.student.profile.user.username+" <-> "+self.tutor.profile.user.username
    def getStartTime(self):
        local_timezone = timezone(settings.TIME_ZONE)
        return self.start_date.astimezone(local_timezone).strftime('%H:%M')
    def getEndTime(self):
        local_timezone = timezone(settings.TIME_ZONE)
        return self.end_date.astimezone(local_timezone).strftime('%H:%M')
    def getBookedDate(self):
        local_timezone = timezone(settings.TIME_ZONE)
        return str(self.start_date.astimezone(local_timezone).date())


class System(models.Model):  #single record table storing system info
    wallet_amount = models.DecimalField(max_digits=20, decimal_places=2)
    def __str__(self):
        return "System info"

class Wallet(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0, blank=True, null=True)
    def __str__(self):
        return str(self.id)+": "+self.profile.user.username+"'s wallet"

class Coupon(models.Model):
    code = models.CharField(max_length=12)
    expire_date = models.DateTimeField()
    used_date = models.DateTimeField(null=True, blank=True)
    used_session = models.OneToOneField(Session, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return "Coupon "+str(self.id)
    
    @classmethod
    def validate(coupon_code):
        c = Coupon.objects.filter(code=coupon_code).filter(used_session__isnull=True)
        return len(c)!=0

    @classmethod
    def markCouponUsed(coupon_code, session):
        c = Coupon.objects.filter(code=coupon_code).filter(used_session__isnull=True)
        if len(c)!=0:
            c[0].used_session = session
            c[0].save()
    