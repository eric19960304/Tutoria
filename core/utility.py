from django.core.mail import send_mail
from django.utils import timezone as django_timezone
from tutoriabeta import settings
from pytz import timezone
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from .models import *


def toLocalDatetime(date):
    local_timezone = timezone(settings.TIME_ZONE)
    return date.astimezone(local_timezone)


# datetime related function
def getCurrentDatetime():
    local_timezone = timezone(settings.TIME_ZONE)
    return datetime.now().astimezone(local_timezone)

def getTimeStr(date):
    local_timezone = timezone(settings.TIME_ZONE)
    return date.astimezone(local_timezone).strftime('%H:%M')

def getDatetimeStr(date):
    local_timezone = timezone(settings.TIME_ZONE)
    return date.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M')

def getDateStr(date):
    local_timezone = timezone(settings.TIME_ZONE)
    return date.astimezone(local_timezone).strftime('%Y-%m-%d')

def getDatetimeStr2(date):
    local_timezone = timezone(settings.TIME_ZONE)
    return date.astimezone(local_timezone).strftime('%e %b %Y, %H:%M')

def getDateStr2(date):
    local_timezone = timezone(settings.TIME_ZONE)
    return date.astimezone(local_timezone).strftime('%e %b %Y')

def getNextHalfHour(date):
    delta = timedelta(minutes=30)
    return date + (datetime.min - date) % delta


# other function that do not want to put in views
def sendEmailToTutor(s):
    msg_body = 'Dear '+s.tutor.profile.user.username+",\n"+\
               'Student with username <'+s.student.profile.user.username+ '>'+\
               ' has booked a session with you at '+s.getBookingDateStr+ ".\n" + \
               'The session will start at ' +s.getBookedDateStr+ ' from ' +s.getStartTimeStr+ ' to ' + s.getEndTimeStr+'.\n'\
               'The contact number of the student is '+s.student.profile.phone+"."

    send_mail(
        'You have a new session booked',
        msg_body,
        'noreplay@tutoria.com',
        [s.tutor.profile.user.email],
        fail_silently=False,
        )

def sendNotification(s,isPrivateTutor, credited_amount):
    now = getCurrentDatetime()

    amount = '%.2f'%credited_amount
    #for student
    student_msg = 'Dear '+s.student.profile.user.username+', You have successfully booked a session with tutor '+s.tutor.profile.user.username+\
                    ' at '+s.getBookingDateStr+'.\n'+\
                    'The session will start at ' +s.getBookedDateStr+ ' from ' +s.getStartTimeStr+ ' to ' + s.getEndTimeStr+'.\n'\
                    'Please remind that, you will not able to cancel the booked session at the time that the session is about to start within 24 hour.\n'
    if isPrivateTutor:
        student_msg += '\nSince you have booked a private tutor, '+\
                        'HKD '+amount+' has been deducted from your wallet.\n'+\
                        'This amount will be refunded if you cancel the session at less 24 hour before the starting time of the session.\n'

    s_n = Notification(profile = s.student.profile, message = student_msg, date=now)
    s_n.save()

    #for tutor
    tutor_msg = 'Dear '+s.tutor.profile.user.username+",\n"+\
                'Student with username '+s.student.profile.user.username+ \
                ' has booked a session with you at '+s.getBookingDateStr+ ".\n" + \
                'The session will start at ' +s.getBookedDateStr+ ' from ' +s.getStartTimeStr+ ' to ' + s.getEndTimeStr+'.\n'\
                'The contact number of the student is '+s.student.profile.phone+"."
    
    if isPrivateTutor:
        student_msg += 'HKD '+amount+' will be transer to your wallet, '+\
                        'if the session has not been cancelled at less 24 hour before the starting time of the session.\n'

    t_n = Notification(profile = s.tutor.profile, message = tutor_msg, date=now)
    t_n.save()

def validateBookingDatetime(date_start, date_end, tutor):
    session_list = Session.objects.exclude(end_date__lte = date_start).exclude(start_date__gte=date_end)
    if len(session_list)>0:
        print("booking date invalid: {}".format(session_list))
        return False
    else:
        return True

def checkFairBook(date_start, date_end, tutor, student):
    session_list = Session.objects.filter(isBlackedout=False).filter(tutor=tutor).filter(student=student).filter(start_date__date=date_start.date())
    if len(session_list)>0:
        return False
    else:
        return True
