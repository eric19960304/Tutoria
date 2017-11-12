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
from django.db.models import Q
from .handleTransaction import *
from .factory import initDatabase, createUser
from .utility import *
from decimal import Decimal



@login_required
def reviewTutor(request, url_token):
    url_not_found = False
    url = ReviewTempUrl.objects.filter(temp_url=url_token).filter(expires__gte=datetime.now())
    if len(url) == 0:
        context={'url_not_found': True}
        return render(request, 'review_tutor.html', context)
    url = url[0]
    if not request.POST:
        student = url.student
        tutor = url.tutor
        context = {'student': student, 'tutor': tutor, 'url_token': url_token}
        return render(request, 'review_tutor.html', context)
    else:
        isAnonymous = False
        if 'isAnonymous' in request.POST and request.POST['isAnonymous']=="True":
            isAnonymous = True
        
        if 'comment' in request.POST and request.POST['comment']!="":
            r = Review(tutor=url.tutor, student = url.student, rating=int(request.POST['rating']), date=getCurrentDatetime() , comment=request.POST['comment'], isAnonymous=isAnonymous)
        else:
            r = Review(tutor=url.tutor, student = url.student, rating=int(request.POST['rating']), date=getCurrentDatetime() ,  isAnonymous=isAnonymous)
        
        r.save()
        url.delete()
        context = {'submitted':True}
        return render(request, 'review_tutor.html', context)

    

@login_required
def viewWallet(request):
    if request.user.username =="admin":
        return HttpResponse("You logged in as admin.")
    
    wallet = request.user.profile.wallet
    context={'amount':wallet.amount}
    return render(request, 'view_wallet.html', context)


@login_required
def viewTimetable(request):
    if request.user.username =="admin":
        return HttpResponse("You logged in as admin.")

    user_profile = request.user.profile

    context={'profile':user_profile}

    if(user_profile.isStudent):
        s = Session.objects.filter(isBlackedout=False).exclude(status="ended").filter(student=user_profile.student).order_by('-booking_date')
        context['student_session_list'] = s
    if(user_profile.isTutor):
        s = Session.objects.filter(isBlackedout=False).exclude(status="ended").filter(tutor=user_profile.tutor).order_by('-booking_date')
        context['tutor_session_list'] = s

    if request.POST:
        IDs = request.POST.getlist('session_id')
        hasPrivateTutor = False
        hasCancelled = False
        user_debit_amount = 0
        msg = ""

        if len(IDs)==0:
            return render(request, 'timetable.html', context)
        
        for each in IDs:
            s = Session.objects.get(pk=each)
            if s.tutor.isPrivateTutor:
                hasPrivateTutor = True
                user_debit_amount += bookingRefund(s)
            if s.status =="booked":
                # send email to tutor
                sendCancelEmailToTutor(s)
                msg += "\nSession at {} from {} to {} canceled successfully.\n".format(s.getBookedDateStr, s.getStartTimeStr, s.getEndTimeStr)
                hasCancelled = True
                s.delete()
            else:
                msg += "\nSession at {} from {} to {} will begin within 24 hours and cannot be cancelled.\n".format(s.getBookedDateStr, s.getStartTimeStr, s.getEndTimeStr)

        if hasPrivateTutor and hasCancelled:
                    msg += '%.2f'%user_debit_amount + ' HKD has been refunded to your wallet.'
        
        context['cancel_session_msg']=msg
    
    return render(request, 'timetable.html', context)



@login_required
def bookTutor(request, tutor_id):
    if request.user.username =="admin":
        return HttpResponse("You logged in as admin.")
    
    # get tutor with tutor_id
    tutor = get_object_or_404(Tutor, pk=tutor_id)

    # tutor with tutor_id not exist
    if tutor not in Tutor.objects.exclude(tutor_type__isnull=True):
        return HttpResponse("This Tutor not available.")
    
    # get tutor unavaliableTimeslot in next 7 date
    current = getCurrentDatetime()
    week_after = current + timedelta(days=7)
    allTimeObj = Session.objects.filter(tutor=tutor).filter(start_date__date__range=[current,week_after])
    unavailable_time = [ getDatetimeStr(t.start_date)+" - "+getDatetimeStr(t.end_date) for t in allTimeObj]
    
    context = {'tutor': tutor, 'unavailable_time': unavailable_time}
    if tutor.isPrivateTutor:
        amount = tutor.hourly_rate*Decimal(1.05)
        context['fee']= '%.2f'%amount


    if not request.POST:
        # form not submitted
        return render(request, 'book_tutor.html', context)
    
    else:
        # form submitted
        use_coupon = False
        coupon_valid = False
        student = request.user.profile.student
        credited_amount = 0
        booking_date = request.POST['booking_date']
        booking_time = request.POST['booking_time']
        date_start = parse_datetime(booking_date+"T"+booking_time)
        if tutor.isPrivateTutor:
            date_end = date_start+timedelta(hours=1)
        else:
            date_end = date_start+timedelta(minutes=30)
        
        date_start = toLocalDatetime(date_start)
        date_end = toLocalDatetime(date_end)
        # check coupon
        if 'coupon_code' in request.POST and request.POST['coupon_code']!='':
            use_coupon = True
            coupon_code = request.POST['coupon_code']
            if Coupon.validate( str(coupon_code) ):
                coupon_valid = True
        
        # handle coupon invalid error
        if (use_coupon) and (not coupon_valid):
            context['error_msg']="Coupon Code Invalid."
            return render(request, 'book_tutor.html', context)
        
        # check user wallet amount
        if tutor.isPrivateTutor:
            if not hasSufficientBalance(student, tutor, (use_coupon and coupon_valid) ):
                context['error_msg']="Insufficient wallet balance."
                return render(request, 'book_tutor.html', context)
        
        booking_time_valid = validateBookingDatetime(date_start, date_end, tutor)
        
        # check booking valid or not
        if not booking_time_valid :
            context['error_msg']="The timeslot you slected is unavailable. Please select another."
            return render(request, 'book_tutor.html', context)

        fair_book = checkFairBook(date_start, date_end, tutor, student)

        # check booking valid or not
        if not fair_book :
            context['error_msg']="Student only allowed booking ONE timeslot for the same tutor for any single day."
            return render(request, 'book_tutor.html', context)


        s = Session(student=student,tutor=tutor,booking_date=getCurrentDatetime(), start_date=date_start,end_date=date_end,status="booked", isCouponUsed=(use_coupon and coupon_valid))
        s.save()
        if tutor.isPrivateTutor:
            # credit user wallet
            credited_amount = bookingCredit(s)
        sendBookingEmailToTutor(s)
        sendBookingNotification( s, credited_amount)

        request.session['booking_msg'] = "You have booked a session with "+tutor.profile.getUserFullName+"\nDate: "+s.getBookedDateStr+"\nTimeslot: "+s.getStartTimeStr+" to "+s.getEndTimeStr
        if tutor.isPrivateTutor:
            request.session['booking_msg'] += '\n'+('%.2f'%credited_amount) +' has been deducted from your wallet.'
            if use_coupon and coupon_valid:
                request.session['booking_msg'] += "\nCoupon has been used, 5 percent is saved :)"

        return HttpResponseRedirect(reverse('after_booked'))

@login_required
def afterBooked(request):
    return render(request, 'after_booked.html', {'msg':request.session['booking_msg']})

def searchTutor(request):
    
    if not request.GET:
        context = {'tag':Tag.objects.all(), 'course': Course.objects.all() }
        return render(request, 'search_tutor.html', context)
    else:
        tutor_list = Tutor.objects.exclude(tutor_type__isnull=True) \
                              .exclude(hourly_rate__isnull=True) \
                              .exclude(university__isnull=True) \
                              .exclude(bio__isnull=True)\
                              .exclude(profile__user__first_name__isnull=True)\
                              .exclude(profile__user__last_name__isnull=True)

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
            for tutor in tutor_list:
                if not checkNext7day(tutor):
                    tutor_list = tutor_list.exclude(pk=tutor.pk)

        context = {'tag':Tag.objects.all(), 'course': Course.objects.all(),'tutor_list': tutor_list}
        return render(request, 'search_result.html', context)

def viewTutorProfile(request, tutor_id):
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    reviews = Review.objects.filter(tutor=tutor)
    context= {'tutor':tutor, 'reviews': reviews}
    if len(reviews)<3:
        context['noAverage']=True
    return render(request, 'view_tutor_profile.html', context)

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


def homepage(request):
    return render(request, 'homepage.html')