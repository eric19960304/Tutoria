from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import SearchTutorForm, SignUpForm
from .models import *
from tutoriabeta import settings
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from django.utils import timezone as django_timezone
from pytz import timezone
from django.db.models import Q
from .handleTransaction import *
from .factory import *
from .utility import *

def homepage(request):
    return render(request, 'homepage.html')
    

@login_required
def viewWallet(request):
    if request.user.username =="admin":
        return HttpResponse("You logged in as admin.")
    
    wallet = request.user.profile.wallet
    context={'amount':wallet.amount}
    return render(request, 'view_wallet.html', context)

@login_required
def cancelSession(request):

    IDs = request.POST.getlist('session_id')
    hasPrivateTutor = False

    if len(IDs)==0:
        return HttpResponse("You have not selected any tutorial session.")

    for each in IDs:
        s = Session.objects.get(pk=each)
        if s.tutor.getTutorType=="private":
            hasPrivateTutor = True
            user_debit_amount = bookingRefund(s.student,s.tutor,s)
            
        s.delete()
    if hasPrivateTutor:
        msg = 'Delete success. '+ str(user_debit_amount) + ' HKD has been refunded to your wallet.'
    else:
         msg = 'Delete success.'

    context = {'cancel_session_msg':msg}
    return render(request, 'cancel_session.html', context)


@login_required
def viewTimetable(request):
    if request.user.username =="admin":
        return HttpResponse("You logged in as admin.")

    user_profile = request.user.profile

    if(user_profile.user_type.user_type=="tutor"):
        s = Session.objects.filter(tutor=user_profile.tutor)
    elif(user_profile.user_type.user_type=="student"):
        s = Session.objects.filter(student=user_profile.student)       
    else:
        # select user_profile = tutor or user_profile = student
        s = Session.objects.filter( Q( tutor= user_profile.tutor) | Q(student=user_profile.student))

    context={'session_list': s}
    
    return render(request, 'timetable.html', context)

def searchTutor(request):
    
    form = SearchTutorForm()
    if not request.GET:
        context = {'form':form, 'tag':Tag.objects.all(), 'course': Course.objects.all() }
        return render(request, 'search_tutor.html', context)
    else:
        tutor_list = Tutor.objects.exclude(tutor_type__isnull=True) \
                              .exclude(hourly_rate__isnull=True) \
                              .exclude(university__isnull=True) \
                              .exclude(bio__isnull=True)

        if 'tutor_type' in request.GET:
            t = request.GET['tutor_type']
            tutor_list = tutor_list.filter(tutor_type__tutor_type=t)
        if 'university' in request.GET:
            tutor_list = tutor_list.filter(university__abbrev=request.GET['university'])
        if 'course' in request.GET:
            course_list = request.GET.getlist('course')
            for each in course_list:
                tutor_list = tutor_list.filter(course__code=each)
        if 'tag' in request.GET:
            tag_list = request.GET.getlist('tag')
            for each in tag_list:
                tutor_list = tutor_list.filter(tag__name=each)
        if len(request.GET['first_name'])>0 :
            fn = request.GET['first_name']
            tutor_list = tutor_list.filter(profile__user__first_name=fn)
        if len(request.GET['last_name'])>0:
            ln = request.GET['last_name']
            tutor_list = tutor_list.filter(profile__user__last_name=ln)
        if len(request.GET['min'])>0:
            min = request.GET['min']
            tutor_list = tutor_list.filter(hourly_rate__gte=min)
        if len(request.GET['max'])>0:
            max = request.GET['max']
            tutor_list = tutor_list.filter(hourly_rate__lte=max)
        if 'next7' in request.GET:
            pass
        

        context = {'form':form, 'tag':Tag.objects.all(), 'course': Course.objects.all(),'tutor_list': tutor_list, 'searched': True}
        return render(request, 'search_tutor.html', context)

@login_required
def bookTutor(request, tutor_id):
    if request.user.username =="admin":
        return HttpResponse("You logged in as admin.")
    
    # get tutor with tutor_id
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    typeOfTutor = tutor.getTutorType

    # tutor with tutor_id not exist
    if tutor not in Tutor.objects.exclude(tutor_type__isnull=True):
        return HttpResponse("This Tutor not available.")
    
    if not request.POST:
        # form not submitted

        # get tutor unavaliableTimeslot in next 7 date
        local_timezone = timezone(settings.TIME_ZONE)
        current = django_timezone.now()
        week_after = current + timedelta(days=7)
        allTimeObj = UnavailableTimeslot.objects.filter(start_time__date__range=[current,week_after]).filter(tutor=tutor)
        unavailable_time = [ t.start_time.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M')+" - "+t.end_time.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M') for t in allTimeObj]

        # get timeslot that already booked
        # ----------to be finished----------
        
        context = {'tutor': tutor, 'unavailable_time': unavailable_time}
        if typeOfTutor=="private":
            amount = tutor.hourly_rate*1.05
            context['fee']= '%.2f'%amount

        return render(request, 'book_tutor.html', context)
    
    else:
        # form submitted

        isPrivateTutor = (typeOfTutor=="private")
        use_coupon = False
        coupon_valid = False
        student = request.user.profile.student
        credited_amount = 0
        
        if 'coupon_code' in request.POST and request.POST['coupon_code']!='':
            use_coupon = True
            coupon_code = request.POST['coupon_code']
            if Coupon.validate( str(coupon_code) ):
                coupon_valid = True
        
        # handle coupon invalid error
        if (use_coupon) and (not coupon_valid):
            context['error_msg']="Coupon Code Invalid."
            return render(request, 'book_tutor.html', context)
        
        # credit user's wallet
        if isPrivateTutor:
            credited_amount = bookingCredit(student, tutor, use_coupon and coupon_valid)
            if credited_amount < 0:
                context['error_msg']="Insufficient wallet balance."
                return render(request, 'book_tutor.html', context)
        
        booking_date = request.POST['booking_date']
        booking_time = request.POST['booking_time']
        date_start = parse_datetime(booking_date+"T"+booking_time)
        if isPrivateTutor:
            date_end = date_start+timedelta(hours=1)
        else:
            date_end = date_start+timedelta(minutes=30)
        #change timezone
        local_timezone = timezone(settings.TIME_ZONE)
        s = Session(student=student,tutor=tutor,booking_date=django_timezone.now(), start_date=date_start.astimezone(local_timezone),end_date=date_end.astimezone(local_timezone))
        s.save()

        if isPrivateTutor and coupon_valid and use_coupon:
            # since coupon need session object
            Coupon.markCouponUsed(request.POST['coupon_code'], s)

        request.session['booking_msg1'] = "You have booked a session with "+tutor.profile.getUserFullName
        request.session['booking_msg2'] = "Date: "+s.getBookedDateStr+"  /  Timeslot: "+s.getStartTimeStr+" to "+s.getEndTimeStr
        request.session['booking_isPrivateTutor'] = isPrivateTutor

        if isPrivateTutor:
            request.session['booking_msg3'] = ('%.2f'%credited_amount) +' has been deducted from your wallet.'
            if use_coupon and coupon_valid:
                request.session['useCoupon']=True
            else:
                request.session['useCoupon']=False
        else:
            request.session['booking_msg3'] = None


        sendEmailToTutor(s)
        sendNotification(s, isPrivateTutor, credited_amount)

        return HttpResponseRedirect(reverse('after_booked'))

@login_required
def afterBooked(request):
    isPrivateTutor = False
    
    msg1=request.session['booking_msg1']
    msg2=request.session['booking_msg2']
    msg3=request.session['booking_msg3']
    isPrivateTutor = request.session['booking_isPrivateTutor']
    context={'msg1':msg1,'msg2':msg2}

    
    
    if isPrivateTutor:
        context['msg3'] = msg3
        if request.session['useCoupon']==True:
            context['coupon_msg']="Coupon has been used, 5 percent is saved :)"
    
    return render(request, 'after_booked.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            user_type = form.cleaned_data['user_type']
            phone_no = form.cleaned_data.get('phone_no')
            

            createUser(user, user_type, phone_no)

            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('homepage')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def notification(request):
    notif_list = Notification.objects.filter(profile=request.user.profile).order_by('-date')

    context={'list':notif_list}
    return render(request, 'notification.html', context)


