import schedule
import time
import os 

def job_placer():
    print("Places the job:")
    schedule.every(30).minutes.do(job)
    return schedule.CancelJob # only cancel the job_placer() routine and will not affect the sheduled job()

def job():
    os.system('python manage.py managesession >> manage_session_log.txt')

schedule.every().day.at("01:59").do(job_placer)
#schedule.every().seconds.do(job)
#schedule.every().hour.do(job)
#schedule.every().day.at("12:53").do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)

while True:
    schedule.run_pending()
    time.sleep(59)