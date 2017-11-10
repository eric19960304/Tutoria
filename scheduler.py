import schedule
import time
import os 


def job():
    os.system('python manageSession.py')

#schedule.every().seconds.do(job)
#schedule.every(30).minutes.do(job)
#schedule.every().hour.do(job)
#schedule.every().day.at("10:30").do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)

while True:
    schedule.run_pending()
    time.sleep(1000)