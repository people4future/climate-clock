from time import sleep
from climateclock_counter import Countobject
from climateclock_counter_simulate import Countobject

countobject = Countobject()

while True:
    print(countobject.count())
    sleep(countobject.sleeptime)
