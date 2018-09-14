import schedule
import time
import os 
import sys
import datetime

if len(sys.argv)<2:
    print("usage: python scheduler.py [schedule time in %H:%M]")
    exit()
else:
    print("Job will be start at {}...".format(sys.argv[1]))

def job_placer():
    print("The job is now on routine.")
    os.system('python manage.py managesession >> manage_session_log.txt')
    print("Invoked at {}".format(datetime.datetime.now()))

    schedule.every(30).minutes.do(job)
    
    return schedule.CancelJob # only cancel the job_placer() routine and will not affect the sheduled job()

def job():
    os.system('python manage.py managesession >> manage_session_log.txt')
    print("Invoked at {}".format(datetime.datetime.now()))

schedule.every().day.at(sys.argv[1]).do(job_placer)
#schedule.every().seconds.do(job)
#schedule.every().hour.do(job)
#schedule.every().day.at("12:53").do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)