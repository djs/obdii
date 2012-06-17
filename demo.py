import elm
import obdii
import sys
import time

def main():
    port = sys.argv[1]

    adapter = elm.Elm(port)
    obd = obdii.Obdii(adapter)

    while True:
        rpm = obd.get_current_engine_rpm()
        ect = obd.get_current_ect()

        print "RPM: %d rpm, ECT: %d C" % (rpm, ect)
        time.sleep(1)


if __name__ == '__main__':
    main()
