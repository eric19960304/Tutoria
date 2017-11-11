import schedule
import time
import os 


def job():
    os.system('python manage.py managesession >> manage_session_log.txt')

#schedule.every().seconds.do(job)
schedule.every(30).minutes.do(job)
#schedule.every().hour.do(job)
#schedule.every().day.at("12:53").do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)

while True:
    schedule.run_pending()
    time.sleep(59)