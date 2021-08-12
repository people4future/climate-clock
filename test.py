from time import sleep
from climateclock_counter import Countobject
from climateclock_counter_simulate import Countobject

countobject = Countobject(256)

while True:
    print(countobject.count())
    sleep(0.01)
