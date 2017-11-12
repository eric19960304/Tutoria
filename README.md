# tutoria

HKU COMP3297 Software engineering
Group 10 - Jamsandwich Co.

python version: 3.6.3
django version: 1.11.6

admin username: admin
admin password: jamsandwich

run server:
python manage.py runserver

run session manage command:
python manage.py managesession >> manage_session_log.txt

[optional]
To use python scheduler to periodically run session manage command, first install schedule module:
pip install schedule

Then run:
python scheduler.py