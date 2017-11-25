# tutoria

HKU COMP3297 Software engineering
Group 10 - Jamsandwich Co.

python version: 3.6.3
django version: 1.11.6

Prerequisite install:
pip install pillow

admin username: admin
admin password: jamsandwich

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

For example, the command "python scheduler.py 8:30, then the command "python manage.py managesession >> manage_session_log.txt" will be run in every 30 minutes starting at 8:30 at the day of running the script.