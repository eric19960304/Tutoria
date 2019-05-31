from pytz import timezone
from datetime import datetime, timedelta
from tutoriabeta import settings
from django.utils.timezone import activate

# datetime related function

activate(settings.TIME_ZONE)

def toLocalDatetime(date):
    local_timezone = timezone(settings.TIME_ZONE)
    try:
        result = date.astimezone(local_timezone)
    except Exception:
        result = date
    return result

def getCurrentDatetime():
    return toLocalDatetime(datetime.now())

def getTimeStr(date):
    return toLocalDatetime(date).strftime('%H:%M')

def getDatetimeStr(date):
    return toLocalDatetime(date).strftime('%Y-%m-%d %H:%M')

def getDateStr(date):
    return toLocalDatetime(date).strftime('%Y-%m-%d')

def getDatetimeStr2(date):
    return toLocalDatetime(date).strftime('%e %b %Y, %H:%M')

def getDateStr2(date):
    return toLocalDatetime(date).strftime('%e %b %Y')

def getNextHalfHour(date):
    delta = timedelta(minutes=30)
    return date + (datetime.min - date) % delta

def getNearestHalfHour(date):
    ceiling = getNextHalfHour(date)
    if date > date.replace(minute=30,second=0, microsecond=0):
        floor = date.replace(minute=30,second=0, microsecond=0)
    else:
        floor = date.replace(minute=0,second=0, microsecond=0)
    if date - floor <= ceiling - date:
        return floor
    else:
        return ceiling