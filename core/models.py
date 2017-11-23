from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from tutoriabeta import settings
from datetime import datetime, timedelta
from pytz import timezone
from django.utils import timezone as django_timezone
from decimal import Decimal

# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone



class Tag(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return str(self.id)+": "+self.name

class University(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=10)
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

class Wallet(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0, blank=True, null=True)
    def __str__(self):
        if len(Wallet.objects.exclude(profile=None).filter(pk=self.id))>0:  # not system wallet
            return "Wallet "+str(self.id)+': ' +self.profile.user.username
        else:
            return str(self.id)+": System wallet"
    def credit(self, credit_amount): #decrease amount
        self.amount -= credit_amount
    def debit(self, debit_amount):  #increase amount
        self.amount += debit_amount
    @staticmethod
    def getSystemWallet():
        return Wallet.objects.filter(profile=None)[0]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    user_type =  models.ForeignKey(UserType)
    wallet = models.OneToOneField(Wallet)
    def __str__(self):
        return "Profile "+str(self.id)+": "+self.user.username+"'s profile"
    @property
    def getUserType(self):
        return self.user_type.user_type
    @property
    def isStudent(self):
        return self.user_type.user_type=="student" or self.user_type.user_type=="both"
    @property
    def isTutor(self):
        return self.user_type.user_type=="tutor" or self.user_type.user_type=="both"
    @property
    def isBoth(self):
        return self.user_type.user_type=="both"
    @property
    def getUserFullName(self):
        user=self.user
        fname=""
        if user.first_name != None:
            fname += user.first_name

        if user.first_name != None and user.last_name != None:
            fname += " " + user.last_name
        elif user.last_name != None:
            fname += user.last_name
        
        return fname
    @property
    def hasNotification(self):
        return len(Notification.objects.filter(profile=self,checked=False))>0
    @property
    def getNotificationNum(self):
        return len(Notification.objects.filter(profile=self,checked=False))
    @property
    def getUsername(self):
        return self.user.username


class Course(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    university = models.ForeignKey(University)
    def __str__(self):
        return "Course "+str(self.id)+": "+self.name


class Student(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    university = models.OneToOneField(University, blank=True,null=True)
    def __str__(self):
        return "Student "+str(self.id)+": "+self.profile.user.username

class Tutor(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    tutor_type =  models.ForeignKey(TutorType, blank=True, null=True )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0.0))
    tag = models.ManyToManyField(Tag, blank=True)
    university = models.ForeignKey(University, blank=True,null=True)
    course = models.ManyToManyField(Course, blank=True)
    bio = models.CharField(max_length=500, blank=True,null=True)
    def __str__(self):
        return "Tutor "+str(self.id)+": "+self.profile.user.username
    @property
    def profileCompleteness(self):
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
    @property
    def getTutorType(self):
        return self.tutor_type.tutor_type
    @property
    def isPrivateTutor(self):
        return self.tutor_type.tutor_type=="private"
    @property
    def getAverageRating(self):
        if len( Review.objects.filter(tutor=self) )>0:
            return Review.getAverageScore(self)
        else:
            return 999



class Session(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10,blank=True,null=True) # possible value: booked, cancelled, locked, ended
    isCouponUsed = models.BooleanField(default=False)
    isBlackedout = models.BooleanField(default=False)
    def __str__(self):
        local_timezone = timezone(settings.TIME_ZONE)
        s_d = self.start_date.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M')
        n_d = self.end_date.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M')
        try:
            return "Session "+str(self.id)+": "+self.student.profile.user.username+" <-> "+self.tutor.profile.user.username +\
                    ", " + s_d + " - " + n_d
        except AttributeError:
            return str(self.id)+": "+self.tutor.profile.user.username+'\'s '+"Blackedout ("+s_d+" - "+n_d+")"
    @property
    def getStartTimeStr(self):
        local_timezone = timezone(settings.TIME_ZONE)
        return self.start_date.astimezone(local_timezone).strftime('%H:%M')
    @property
    def getEndTimeStr(self):
        local_timezone = timezone(settings.TIME_ZONE)
        return self.end_date.astimezone(local_timezone).strftime('%H:%M')
    @property
    def getBookedDateStr(self):
        local_timezone = timezone(settings.TIME_ZONE)
        return self.start_date.astimezone(local_timezone).strftime('%e %b %Y')
    @property
    def getBookingDateStr(self):
        local_timezone = timezone(settings.TIME_ZONE)
        return self.booking_date.astimezone(local_timezone).strftime('%e %b %Y, %H:%M')

class Transaction(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE )
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    session = models.ForeignKey(Session, blank=True, null=True)
    isDebit = models.BooleanField()
    isTutorFeeRelated = models.BooleanField(default=False)
    isSystemWalletRelated = models.BooleanField(default=False)
    isBankRelated = models.BooleanField(default=False)
    description = models.CharField(max_length=50, blank=False,null=True)
    def __str__(self):
        if self.isTutorFeeRelated:
            return "Transaction "+str(self.id)+": "+self.profile.user.username+" <-> "+self.session.tutor.profile.user.username+", "+self.description
        else:
            return "Transaction "+str(self.id)+": "+self.profile.user.username+", "+self.description
    @property
    def getDate(self):
        local_timezone = timezone(settings.TIME_ZONE)
        return self.date.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M')

class System(models.Model):  #single record table storing system info
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE)
    def __str__(self):
        return "System info"

class Notification(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)
    date = models.DateTimeField()
    checked = models.BooleanField(default=False)
    def __str__(self):
        return "Notification "+str(self.id)+": "+self.profile.user.username   

class Coupon(models.Model):
    code = models.CharField(max_length=12, unique=True)
    expire_date = models.DateTimeField()
    #used_date = models.DateTimeField(null=True, blank=True)
    #used_session = models.OneToOneField(Session, null=True, blank=True)
    def __str__(self):
        return "Coupon "+str(self.id)
    
    @staticmethod
    def validate( coupon_code):
        local_timezone = timezone(settings.TIME_ZONE)
        c = Coupon.objects.filter(code=coupon_code).filter(expire_date__gte=datetime.now().astimezone(local_timezone))
        return len(c)!=0
    '''
    @staticmethod
    def markCouponUsed( coupon_code, session):
        c = Coupon.objects.filter(code=coupon_code)
        if len(c)!=0:
            c[0].used_session = session
            c[0].save()
    '''

class Review(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student)
    rating = models.IntegerField()
    date = models.DateTimeField()
    comment = models.CharField(max_length=500, blank=True,null=True)
    isAnonymous = models.BooleanField()
    def __str__(self):
        return "Review "+str(self.id)+": "+self.tutor.profile.user.username+"<->"+self.student.profile.user.username
    
    @staticmethod
    def getAverageScore(tutor):
        sum = 0
        r_list = Review.objects.filter(tutor=tutor)
        for each in r_list:
            sum += each.rating
        return "%.2f"%(sum / len(r_list))

class ReviewTempUrl(models.Model):
    temp_url = models.CharField(blank=False, max_length=32, unique=True)
    tutor = models.ForeignKey(Tutor)
    student = models.ForeignKey(Student)
    expires = models.DateTimeField()
    def __str__(self):
        return "Review url "+str(self.id)+": "+self.tutor.profile.user.username+"<->"+self.student.profile.user.username