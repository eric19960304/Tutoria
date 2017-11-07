from .models import *

def initDatabase():
    if len(UserType.objects.filter(user_type="student"))==0:
        UserType(user_type="student").save()
    if len(UserType.objects.filter(user_type="tutor"))==0:
        UserType(user_type="tutor").save()
    if len(UserType.objects.filter(user_type="both"))==0:
        UserType(user_type="both").save()
    if len(TutorType.objects.filter(tutor_type="private"))==0:
        TutorType(tutor_type="private").save()
    if len(TutorType.objects.filter(tutor_type="contracted"))==0:
        TutorType(tutor_type="contracted").save()
    if len(System.objects.all())==0:
        w = Wallet()
        w.save()
        s = System(wallet=w)
        s.save()


def createUser(user, user_type, phone_no ):

    initDatabase()

    #create wallet
    w = Wallet()
    w.save()

    #create profile
    #get UserType object
    if user_type=="student":
        userType = UserType.objects.get(user_type="student")
    elif user_type=="tutor":
        userType = UserType.objects.get(user_type="tutor")
    else:
        userType = UserType.objects.get(user_type="both")
    pr = Profile(user=user,phone=phone_no,user_type=userType, wallet=w)
    pr.save()

    # create Student and/or Tutor instance for this user
    if user_type=="student":
        s = Student(profile=pr)
        s.save()
    elif user_type=="tutor":
        t = Tutor(profile=pr)
        t.save()
    else: #both
        s = Student(profile=pr)
        t = Tutor(profile=pr)
        s.save()
        t.save()

    

        