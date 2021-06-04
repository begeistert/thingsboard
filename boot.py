# This file is executed on every boot (including wake-boot from deepsleep)

import uos
import gc
import network
import sys
# import webrepl
# import esp
from wifi import *

sys.path.reverse()

# uos.dupterm(None, 1) # disable REPL on UART(0)
# esp.osdebug(None)
# webrepl.start()
gc.collect()

# Se inicia la conexión WiFi
connection = network.WLAN(network.STA_IF)
connection.active(True)
connection.connect(ssid, password)
