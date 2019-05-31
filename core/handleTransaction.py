from .models import *
from decimal import Decimal
from .utility import *

class TransactionException(Exception):
    pass

# only check, no money is transfered
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
        if user_credit_amount > 0:

            # credit user wallet
            wallet = student.profile.wallet
            wallet.credit( user_credit_amount )
            wallet.save()
            # debit system wallet
            sys_wallet = Wallet.getSystemWallet()
            sys_wallet.debit( user_credit_amount )
            sys_wallet.save()
        
            # record the transaction
            t = Transaction(profile=student.profile, date=getCurrentDatetime(), amount=user_credit_amount, session=session, isDebit=False,isTutorFeeRelated=True, isSystemWalletRelated=True, description="Tutor fee payment")
            t.save()

            st = Transaction(date=getCurrentDatetime(), amount=user_credit_amount,session=session, isDebit=True,isTutoriaOwned=True, isSystemWalletRelated=True, isTutorFeeRelated=True, description="Tutor fee from student")
            st.save()
        
        return user_credit_amount
    else:
        # contracted tutor, no money is transfered
        return 0
        
def bookingRefund(session):
    student = session.student
    tutor = session.tutor
    if tutor.isPrivateTutor:
        
        if session.isCouponUsed:
            user_debit_amount = tutor.hourly_rate
        else:
            user_debit_amount = tutor.hourly_rate*Decimal(1.05)
        
        if user_debit_amount > 0:
            # debit user wallet
            wallet = student.profile.wallet
            wallet.debit( user_debit_amount )
            wallet.save()
            # credit system wallet
            sys_wallet = Wallet.getSystemWallet()
            sys_wallet.credit( user_debit_amount )
            sys_wallet.save()

            # record the transaction
            t = Transaction(profile=student.profile, date=getCurrentDatetime(), amount=user_debit_amount, session=session, isDebit=True, isTutorFeeRelated=True, isSystemWalletRelated=True, description="Tutor fee refund")
            t.save()

            st = Transaction(date=getCurrentDatetime(), amount=user_debit_amount, session=session, isDebit=False,isTutoriaOwned=True, isSystemWalletRelated=True, isTutorFeeRelated=True, description="Refund to student")
            st.save()

        return user_debit_amount
    else:
        return 0

def transferTutorFee(session):
    tutor = session.tutor
    student = session.student
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

        # record transaction
        t = Transaction(profile=tutor.profile, date=getCurrentDatetime(), amount=tutor_debit_amount, session=session, isDebit=True, isTutorFeeRelated=True, isSystemWalletRelated=True, description="Tutor fee deposit")
        t.save()

        st = Transaction(date=getCurrentDatetime(), amount=tutor_debit_amount,session=session, isDebit=False,isTutoriaOwned=True, isSystemWalletRelated=True, isTutorFeeRelated=True, description="Tutor fee to tutor")
        st.save()


def studentAddToWallet(profile, amount):
    if amount > 0:
        # debit the student's wallet
        w = Wallet.objects.get(profile=profile)
        w.debit( Decimal(amount) )
        w.save()

        # record transaction
        t = Transaction(profile=profile,  date=getCurrentDatetime(), amount=amount, isDebit=True,  isBankRelated=True, description="Top up wallet")
        t.save()


        print("{} : add HKD {} to wallet.".format(profile.student,amount))
    else:
        raise TransactionException


def tutorDrawFromWallet(profile,amount):
    if amount >0:
        w = Wallet.objects.get(profile=profile)
        w.credit( Decimal(amount) )
        w.save()

        # record transaction
        t = Transaction(profile=profile,  date=getCurrentDatetime(), amount=amount, isDebit=False, isBankRelated=True, description="Withdraw amount from wallet")
        t.save()

        print("{} : transfered HKD {} from wallet to bank account.".format(profile.tutor,amount))
    else:
        raise TransactionException

def adminDrawFromTutoriaWallet(amount):
    if amount >0:
        s = System.objects.all()[0]
        w = s.wallet
        w.credit( Decimal(amount) )
        w.save()

        # record transaction
        t = Transaction(date=getCurrentDatetime(), amount=amount, isDebit=False,isTutoriaOwned=True, isBankRelated=True, isSystemWalletRelated=True, description="Withdraw amount from wallet")
        t.save()

        print("Admin : transfered HKD {} from wallet to Tutoria's bank account.".format(amount))
    else:
        raise TransactionException
