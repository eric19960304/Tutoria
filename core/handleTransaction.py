from .models import *
from decimal import Decimal

def hasSufficientBalance(student, tutor, isCouponUsed):
    if isCouponUsed:
        user_credit_amount = tutor.hourly_rate
    else:
        user_credit_amount = tutor.hourly_rate*Decimal(1.05)

    wallet = student.profile.wallet
    
    if wallet.amount < user_credit_amount:
        return False
    else:
        return True

def bookingCredit(session):
    student = session.student
    tutor = session.tutor

    if session.isCouponUsed:
        user_credit_amount = tutor.hourly_rate
    else:
        user_credit_amount = tutor.hourly_rate*Decimal(1.05)
        
    
    if tutor.isPrivateTutor:
        
        # credit user wallet
        wallet = student.profile.wallet
        wallet.credit( user_credit_amount )
        wallet.save()
        # debit system wallet
        sys_wallet = Wallet.getSystemWallet()
        sys_wallet.debit( user_credit_amount )
        sys_wallet.save()
        
        return user_credit_amount
    else:
        return 0
        
def bookingRefund(session):
    student = session.student
    tutor = session.tutor
    if tutor.isPrivateTutor:
        
        if session.isCouponUsed:
            user_debit_amount = tutor.hourly_rate
        else:
            user_debit_amount = tutor.hourly_rate*Decimal(1.05)
        
        # debit user wallet
        wallet = student.profile.wallet
        wallet.debit( user_debit_amount )
        wallet.save()
        # credit system wallet
        sys_wallet = Wallet.getSystemWallet()
        sys_wallet.credit( user_debit_amount )
        sys_wallet.save()

        return user_debit_amount
    else:
        return 0

def transferTutorFee(tutor):
    if tutor.isPrivateTutor:
        tutor_debit_amount = tutor.hourly_rate

        # debit tutor wallet
        tutor_wallet = tutor.profile.wallet
        tutor_wallet.debit( tutor_debit_amount )
        tutor_wallet.save()
         # credit system wallet
        sys_wallet = Wallet.getSystemWallet()
        sys_wallet.credit( tutor_debit_amount )
        sys_wallet.save()