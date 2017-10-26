from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import SignUpForm
from .models import *
from tutoriabeta import settings
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from django.utils import timezone as django_timezone
from pytz import timezone
from django.db.models import Q
from .extraFunction import *

def homepage(request):
    return render(request, 'homepage.html')

def searchTutor(request):
    tutor_list = Tutor.objects.exclude(tutor_type__isnull=True) \
                              .exclude(hourly_rate__isnull=True) \
                              .exclude(university__isnull=True) \
                              .exclude(bio__isnull=True)
    type_list=[ tutor.tutor_type.tutor_type for tutor in tutor_list]
    zip_list = zip(tutor_list, type_list)
    context = {'zip_list': zip_list}
    return render(request, 'search_tutor.html', context)

@login_required
def viewWallet(request):
    wallet = profile=request.user.profile.wallet
    context={'amount':wallet.amount}
    return render(request, 'view_wallet.html', context)

@login_required
def cancelSession(request):
    IDs = request.POST.getlist('session_id')
    for each in IDs:
        s = Session.objects.get(pk=each)
        bookingRefund(s.student,s.tutor,s)
        s.delete()
        
    context = {'cancel_session_msg': 'Delete success!'}
    return render(request, 'cancel_session.html', context)


@login_required
def viewTimetable(request):
    user_profile = request.user.profile
    s=[]
    if(user_profile.user_type.user_type=="tutor"):
        s = Session.objects.filter(tutor=user_profile.tutor)
        context={'session_list': s}
    elif(user_profile.user_type.user_type=="student"):
        s = Session.objects.filter(student=user_profile.student)
        context={'session_list': s}
    else:
        # select user_profile = tutor or user_profile = student
        s = Session.objects.filter( Q( tutor= user_profile.tutor) | Q(student=user_profile.student))
        context={'session_list': s}
    
    return render(request, 'timetable.html', context)


@login_required
def bookTutor(request, tutor_id):
    
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    if tutor not in Tutor.objects.exclude(tutor_type__isnull=True):
        return HttpResponse("Tutor not available yet.")

    local_timezone = timezone(settings.TIME_ZONE)

    current = django_timezone.now()
    week_after = current + timedelta(days=7)

    allTimeObj = UnavailableTimeslot.objects.filter(start_time__date__range=[current,week_after]).filter(tutor=tutor)
    unavailable_time = [ t.start_time.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M')+" - "+t.end_time.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M') for t in allTimeObj]

    typeOfTutor = tutor.tutor_type.tutor_type

    context = {'tutor': tutor, 'unavailable_time': unavailable_time,'tutor_type':  typeOfTutor}
    
    #check if form is submitted
    if not request.POST:
        return render(request, 'book_tutor.html', context)
    else:
        #not submitted
        if typeOfTutor=="private":
            coupon_valid = False
            student = request.user.profile.student
            if request.POST['coupon_code']: #coupon code entered
                coupon_valid = validateCoupon(request.POST['coupon_code'])
            if (not coupon_valid) and (request.POST['coupon_code']):
                context['error_msg']="Coupon Code Invalid."
                return render(request, 'book_tutor.html', context)

            # deduct money from user
            if(coupon_valid):
                credited_amount = bookingCredit(student, tutor,True)
            else:
                credited_amount = bookingCredit(student, tutor, False)

            if credited_amount < 0:
                context['error_msg']="Insufficient wallet balance."
                return render(request, 'book_tutor.html', context)

            booking_date = request.POST['booking_date']
            booking_time = request.POST['booking_time']
            date_start = parse_datetime(booking_date+"T"+booking_time)
            
            date_end = date_start+timedelta(hours=1)
            
            s = Session(student=student,tutor=tutor,booking_date=django_timezone.now(), start_date=date_start,end_date=date_end)
            s.save()
            
            if coupon_valid:
                # since coupon need session object
                markCouponUsed(request.POST['coupon_code'], s)
        
            request.session['booking_message1'] = "You have booked a session with "+tutor.profile.user.first_name+" " +tutor.profile.user.first_name
            request.session['booking_message2'] = "Date: "+s.getBookedDate()+"  /  Timeslot: "+s.getStartTime()+" to "+s.getEndTime()
            request.session['useCoupon']=True
            return HttpResponseRedirect(reverse('after_booked'))
        else:
            student = request.user.profile.student

            # deduct money from user
            credited_amount = bookingCredit(student, tutor)

            if credited_amount < 0:
                context['error_msg']="Insufficient wallet balance."
                return render(request, 'book_tutor.html', context)

            booking_date = request.POST['booking_date']
            booking_time = request.POST['booking_time']
            date_start = parse_datetime(booking_date+"T"+booking_time)
            date_end = date_start+timedelta(minutes=30)
            
            s = Session(student=student,tutor=tutor,booking_date=django_timezone.now(), start_date=date_start,end_date=date_end)
            s.save()
        
            request.session['booking_message1'] = "You have booked a session with "+tutor.profile.user.first_name+" " +tutor.profile.user.first_name
            request.session['booking_message2'] = "Date: "+s.getBookedDate()+"  /  Timeslot: "+s.getStartTime()+" to "+s.getEndTime()
            request.session['useCoupon']=False
            return HttpResponseRedirect(reverse('after_booked'))

@login_required
def afterBooked(request):
    msg1 = ""
    msg2 = ""
    if 'booking_message1' in request.session:
        msg1=request.session['booking_message1']
    if 'booking_message2' in request.session:
        msg2=request.session['booking_message2']
    
    context={'message1':msg1,'message2':msg2}
    context['coupon_msg']=""
    if 'useCoupon' in request.session:
        if request.session['useCoupon']==True:
            context['coupon_msg']="Coupon has been used, 5 percent is saved :)"
        
    return render(request, 'after_booked.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            phone_no = form.cleaned_data.get('phone_no')
            user_type = form.cleaned_data['user_type']
            if user_type=="student":
                t = UserType.objects.get(user_type="student")
            elif user_type=="tutor":
                t = UserType.objects.get(user_type="tutor")
            else:
                t = UserType.objects.get(user_type="both")
            pr = Profile(user=user,phone=phone_no,user_type=t)
            pr.save()

            w = Wallet(profile=pr)
            w.save()

            if user_type=="student":
                s = Student(profile=pr)
                s.save()
            elif user_type=="tutor":
                t = Tutor(profile=pr)
                t.save()
            else:
                s = Student(profile=pr)
                t = Tutor(profile=pr)
                s.save()
                t.save()
            
            
            if user_type=="student":
                t = UserType.objects.get(user_type="student")
            elif user_type=="tutor":
                t = UserType.objects.get(user_type="tutor")
            else:
                t = UserType.objects.get(user_type="both")

            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('homepage')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})




