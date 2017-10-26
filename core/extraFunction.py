from .models import *
from decimal import Decimal

def bookingCredit(student, tutor, use_coupon=False):
    if not use_coupon:
        user_credit_amount = tutor.hourly_rate*1.05
    else:
        user_credit_amount = tutor.hourly_rate
    wallet = student.profile.wallet
    if wallet.amount < user_credit_amount:
        return -1
    else:
        wallet.amount -= Decimal(user_credit_amount)
        wallet.save()
        sys_wallet = System.objects.all()[0]
        sys_wallet.wallet_amount += Decimal(user_credit_amount)
        sys_wallet.save()
        return user_credit_amount
        
def bookingRefund(student, tutor, session):
    coupon_list = Coupon.objects.all()
    for each in coupon_list:
        if session==each.used_session:
            coupon_is_used = True
        else:
            coupon_is_used = False
    if coupon_is_used:
        user_credit_amount = tutor.hourly_rate
    else:
        user_credit_amount = tutor.hourly_rate*1.05
    wallet = student.profile.wallet
    wallet.amount += Decimal(user_credit_amount)
    wallet.save()
    sys_wallet = System.objects.all()[0]
    sys_wallet.wallet_amount -= Decimal(user_credit_amount)
    sys_wallet.save()

def validateCoupon(coupon_code):
    c = Coupon.objects.filter(code=coupon_code).filter(used_session__isnull=True)
    if len(c)==0:
        return False
    else:
        return True

def markCouponUsed(coupon_code, session):
    c = Coupon.objects.filter(code=coupon_code).filter(used_session__isnull=True)
    if len(c)!=0:
        c[0].used_session = session
        c[0].save()

    