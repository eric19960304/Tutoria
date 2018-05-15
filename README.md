# tutoria

HKU COMP3297 Software engineering
Group 10 - Jamsandwich Co.

All features:
sign up/login/logout/forgot password, search tutor, edit profile, book tutor, tutor manage timeslot, internal messaging, email handing, internal transaction, manage timetable, coupon, server side scheduled job

python version: 3.6.3
django version: 1.11.6

Prerequisite install:
pip install pillow

admin username: admin
admin password: jamsandwich

Database initialization:
If the database is reset, the following instance should be created before running the server:
(a) a Wallet instance
(b) a System instance containing a wallet instance created in (a)
(c) University instances

To run server:
python manage.py runserver

To run session manage command:
python manage.py managesession >> manage_session_log.txt

The session manage command will invoke a function that convert the current time to the neartest half hour and manage the sessions by that time. i.e. 9:28 -> 9:30, 10:15:00 -> 10:00, 10:15:01 -> 10:30 ...


[Python scheduler, optional]
To use python scheduler to periodically run session manage command, first install schedule module by running the command:
pip install schedule

To schedule the session management routine, running:
python scheduler.py [schedule time in %H:%M]

For example, the command "python scheduler.py 8:30", then the command "python manage.py managesession >> manage_session_log.txt" will be run in every 30 minutes starting at 8:30 at the day of running the script.

#############################
Limitation:
1) Tag is not user defined, tutor can only select the tag that we provided.
2) After the session is ended, there is a notification telling tutor the money is transferred to her/his account, but no email is sent.

#############################
Minor fixed after the demo:
1) Tutor's detailed profile can now display the rating of each review correctly.
2) The timetable will not display the time row "18:30" (indicating 18:30 to 19:00 which is not in the working hour).
3) The completeness check of tutor profile is now consistant with the searching result.

#############################
Features that implemented but hasn't shown in Demo:
1) Send private message (as Notification instance) to tutor, tutor reply message to student.
2) Upload profile picture.
3) Delete Notifications.