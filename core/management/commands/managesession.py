from django.core.management.base import BaseCommand, CommandError
from datetime import time,datetime, timedelta
from core.models import *
from core.utility import *
from core.handleTransaction import *

class Command(BaseCommand):
    help = 'Purposes: Lock all sessions and end session.'

    def handle(self, *args, **options):

        current = datetime.now()
        current = getNearestHalfHour(current)
        current = toLocalDatetime(current)
        oneDayAfter = current + timedelta(hours=24)

        print("[{}] Session management begin...".format(current.strftime("%d/%b/%Y %H:%M:%S")))
        # booked -> locked
        s = Session.objects.filter(isBlackedout=False).filter(status="booked").filter(start_date=oneDayAfter)
        for each in s:
            # update status
            each.status = "locked"
            each.save()
            print("[{}] Locked session: {}".format(current.strftime("%d/%b/%Y %H:%M:%S"), each))
            transferTutorFee(each.tutor)
            print("[{}] Transfered fee to tutor {}".format(current.strftime("%d/%b/%Y %H:%M:%S"), each.tutor.profile.getUsername))
            sendTutorPaymentNotification(each)
            print("[{}] Sent payment notification to tutor {}".format(current.strftime("%d/%b/%Y %H:%M:%S"), each.tutor.profile.getUsername))
        # locked -> ended
        e_s = Session.objects.filter(isBlackedout=False).filter(status="locked").filter(end_date__lt=current)
        for each in e_s:
            each.status = "ended"
            each.save()
            print("[{}] Ended session: {}".format(current.strftime("%d/%b/%Y %H:%M:%S"), each))
            reviewInvitation(each)
            print("[{}] Send review invitation to {}".format(current.strftime("%d/%b/%Y %H:%M:%S"), each.student))
        
        # delete expired temp url
        url_list = ReviewTempUrl.objects.filter(expires__lt=getCurrentDatetime())
        if len(url_list)>0:
            print("[{}] Deleted expired ReviewTempUrls: {}".format(current.strftime("%d/%b/%Y %H:%M:%S"), url_list))
        url_list.delete()
        # delete expired Coupon
        c_list = Coupon.objects.filter(expire_date__lt=getCurrentDatetime())
        if len(c_list)>0:
            print("[{}] Deleted expired Coupons: {}".format(current.strftime("%d/%b/%Y %H:%M:%S"), c_list))
        c_list.delete()

        print("[{}] Session management finished.".format(current.strftime("%d/%b/%Y %H:%M:%S")))