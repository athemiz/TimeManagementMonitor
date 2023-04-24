import ctypes
from datetime import datetime
from ctypes import wintypes

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hwnd', wintypes.HWND),
        ('uCallbackMessage', wintypes.UINT),
        ('uEdge', wintypes.UINT),
        ('rc', wintypes.RECT),
        ('lParam', wintypes.LPARAM)
    ]

def calculate_task_size(beginTime, endTime, screenwidth):
    beginHours, beginMinutes = map(int, beginTime.split(':'))
    endHours, endMinutes = map(int, endTime.split(':'))
    dayTimeInSeconds = 24 * 3600
    beginTimeInSeconds = beginHours * 3600 + beginMinutes * 60
    endTimeInSeconds = endHours * 3600 + endMinutes * 60
    beginPercentage = beginTimeInSeconds / dayTimeInSeconds
    endPercentage = endTimeInSeconds / dayTimeInSeconds
    return (endPercentage - beginPercentage) * screenwidth

def calculate_task_position(beginTime):
    beginHours, beginMinutes = map(int, beginTime.split(':'))
    beginTimeInSeconds = beginHours * 3600 + beginMinutes * 60
    totalDayTimeInSeconds = 24 * 3600
    position = beginTimeInSeconds / totalDayTimeInSeconds
    return position

def calculate_time_mark_percentage():
    todayTime = datetime.today().time()
    currentTimeInSeconds = todayTime.hour * 3600 + todayTime.minute * 60 + todayTime.second
    totalDayTimeInSeconds = 24 * 3600
    return currentTimeInSeconds / totalDayTimeInSeconds
    
def get_taskbar_height_and_position():
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    ABM_GETTASKBARPOS = 0x00000005
    ctypes.windll.shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(abd))
    rect = abd.rc
    height = (rect.bottom - rect.top) / 4
    position = (rect.left, rect.top - height)
    return height, position