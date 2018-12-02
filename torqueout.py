"""
Dyno Torque Sensor Torque Output Logging Script
"""

import sys
from labjack import ljm
import time
from datetime import datetime
import numpy as np
import signal
import csv

def signal_handler(signal, frame):
    global handle
    print("\nStop Stream")
    ljm.eStreamStop(handle)

    # Close handle
    ljm.close(handle)
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

MAX_REQUESTS = 50 # The number of eStreamRead calls that will be performed.

# Open first found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

try:
    aNames = ["AIN1_EF_INDEX",    #setup what extended feeature to use -- thermocouple type
    "AIN2_EF_INDEX"]          #reference for on board temperature Sensor

    aValues = [1,                # 22 --> K type thermocouple
    1]                        # register value for on board temperature reference
    ljm.eWriteNames(handle, len(aNames), aNames, aValues)
    output_names = ["TIME", "VOLTAGE_1", "VOLTAGE_2", "TORQUE"]
    start = datetime.now()

    cur_log = ("cvttorque" + "_" + str(start.month) + "_" + str(start.day) + "_"+ str(start.year) + "_" + str(start.hour) + "_" + str(start.minute) + "_" + str(start.second) + ".csv")

    with open(cur_log, "w") as f:
        write = csv.writer(f)
        write.writerow(output_names)

    start = time.time()
    while True:
        ref = time.time() - start
        voltage1 = ljm.eReadName(handle, "AIN1_EF_READ_A")
        voltage2 = ljm.eReadName(handle, "AIN2_EF_READ_A")

        #torque output is linear 5v to -5v
        if (voltage1 > 0):
            torque = voltage1*200
        else:
            torque = voltage2*200

        output_values = [ref, voltage1, voltage2, torque]

        print(output_values)

        with open(cur_log,'a') as f:
          write = csv.writer(f)
          write.writerow(output_values)
        time.sleep(5)

    end = datetime.now()

except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)
