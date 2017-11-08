from .models import *
from decimal import Decimal

def bookingCredit(student, tutor, use_coupon=False):
    if tutor.tutor_type.tutor_type=="private":
        if not use_coupon:
            user_credit_amount = tutor.hourly_rate*1.05
        else:
            user_credit_amount = tutor.hourly_rate
        
        wallet = student.profile.wallet
        
        if wallet.amount < user_credit_amount:
            return -1 #negative number indicates booking failure
        else:
            wallet.credit(Decimal(user_credit_amount))
            wallet.save()
            sys_wallet = Wallet.getSystemWallet()
            sys_wallet.debit(Decimal(user_credit_amount))
            sys_wallet.save()
            return user_credit_amount
    else:
        return 0
        
def bookingRefund(student, tutor, session):
    if tutor.tutor_type.tutor_type=="private":
        coupon_list = Coupon.objects.all()
        coupon_is_used = False

        #check if coupon is used
        for each in coupon_list:
            if session==each.used_session:
                coupon_is_used = True
        
        if coupon_is_used:
            user_debit_amount = tutor.hourly_rate
        else:
            user_debit_amount = tutor.hourly_rate*1.05
        
        # debit user wallet
        wallet = student.profile.wallet
        wallet.debit( Decimal(user_debit_amount) )
        wallet.save()
        # credit system wallet
        sys_wallet = Wallet.getSystemWallet()
        sys_wallet.credit( Decimal(user_debit_amount) )
        sys_wallet.save()

        return user_debit_amount
    else:
        return 0

    