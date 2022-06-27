# run.pyw
#
# to do:
# - implement a separate thread for the timer function as otherwise using the toolbar on the matplotlib drawing
#   exhibits some delay
# - there is still the error from pyvisa when exit the program with an active connection. Until now there seems to
#   be no solution. Trying to close the visa resource within the destructor methods failed.
#
# VISA error: VISA error: VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.
# Exception ignored in: <function Resource.__del__ at 0x000000000B67EEE8>
# Traceback (most recent call last):
#   File "...\lib\site-packages\pyvisa\resources\resource.py", line 108, in __del__
#   File "...\lib\site-packages\pyvisa\resources\resource.py", line 243, in close
#   File "...\lib\site-packages\pyvisa\resources\resource.py", line 235, in before_close
#   File "...\lib\site-packages\pyvisa\resources\resource.py", line 252, in __switch_events_off
#   File "...\lib\site-packages\pyvisa\resources\resource.py", line 309, in disable_event
#   File "...\lib\site-packages\pyvisa\ctwrapper\functions.py", line 410, in disable_event
#   File "...\lib\site-packages\pyvisa\ctwrapper\highlevel.py", line 188, in _return_handler
# pyvisa.errors.VisaIOError: VI_ERROR_INV_OBJECT (-1073807346): The given session or object reference is invalid.

from control import Control
from model import Model
app = Control(Model())
app.run()
