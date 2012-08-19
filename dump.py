import elm
import obdii
import sys
import time
import json

def main():
    port = sys.argv[1]

    adapter = elm.Elm(port)
    data = {}
    adapter.send_control_command('H1')

    for pid in range(0, 0xe0):
        response = adapter.send('01%2.2x' % pid)
        data['%2.2x' % pid] = response

    print json.dumps(data, sort_keys=True, indent=4)



if __name__ == '__main__':
    main()
