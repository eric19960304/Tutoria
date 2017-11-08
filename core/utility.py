from .models import *
from django.core.mail import send_mail
import datetime
from django.utils import timezone as django_timezone

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

def sendNotification(s,isPrivateTutor, credited_amount=0):
    now = django_timezone.now()
    amount = str(credited_amount)
    #for student
    student_msg = 'Dear '+s.student.profile.user.username+', You have successfully booked a session with tutor '+s.tutor.profile.user.username+\
                  ' at '+s.getBookingDateStr+'.\n'+\
                  'The session will start at ' +s.getBookedDateStr+ ' from ' +s.getStartTimeStr+ ' to ' + s.getEndTimeStr+'.\n'\
                  'Please remind that, you will not able to cancel the booked session at the time that the session is about to start within 24 hour.\n'
    if isPrivateTutor:
        student_msg += '\nSince you have booked a private tutor, '+\
                       'HKD '+amount+' has been deducted from your wallet.\n'+\
                       'This amount will be refunded if you cancel the session at less 24 hour before the starting time of the session.\n'
    
    s_n = Notification(profile = s.student.profile, message = student_msg, date=now )
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
    
    t_n = Notification(profile = s.tutor.profile, message = tutor_msg, date=now )
    t_n.save()