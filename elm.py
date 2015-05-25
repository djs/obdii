import serial
import re
import time
import serialenum

def available_ports():
    return serialenum.enumerate()

class Elm(object):
    PROMPT = ">"
    LINE_TERMINATION = '\r'
    AT_PREFIX = 'AT'

    PROMPT_REGEX = re.compile(">", re.M)
    RESPONSE_REGEX = re.compile("^.*?[\r]+(.*)\r\r>$", re.M)

    def __init__(self, interface, baud=None):
        if not hasattr(interface, 'read'):
            if baud == None:
                baud = 38400

            self.interface = serial.Serial(port=interface,
                          baudrate=baud,
                          bytesize=serial.EIGHTBITS,
                          parity=serial.PARITY_NONE,
                          stopbits=serial.STOPBITS_ONE,
                          timeout=5)
        else:
            if baud != None:
                raise ValueError

            self.interface = interface

        self._connect()

    def reset(self):
        response = self.send_control_command('Z')
        self._check_reset(response)

    def warm_reset(self):
        response = self.send_control_command('WS')
        self._check_reset(response)

    def _check_reset(self, response):
        if response != "ELM327 v1.3a":
            print 'received: ' + response
            raise Exception


    def _connect(self):
        self.reset()

        response = self.send_control_command('SP0')
        response = self.send_control_command('DP')
        self.send('0100')
        # TODO deal with multiple ECUs properly
        self.send_control_command('CRA7E8')

    def send(self, command):
        data = ""

        self.interface.write(command + self.LINE_TERMINATION)

        while not self.PROMPT_REGEX.search(data):
            data = data + self.interface.read(1)
            #print data

        print 'data read: ' + data.replace('\r', '\n')
        return self.RESPONSE_REGEX.search(data).group(1)


    def send_control_command(self, command):
        return self.send(self.AT_PREFIX + command)

    def send_obdii_command(self, command):
        cmd = ['%.2X' % x for x in command]
        text = self.send(''.join(cmd)).strip()

        if text.find('\n') != -1:
            raise NotImplementedError, "multiline response not yet supported"

        data = []

        for byte in text.split(' '):
            data.append(int(byte, 16))

        return data


    def get_device_info(self):
        print 'Device Description: ' + self.send_control_command('@1')
        print 'Device Identifier: ' + self.send_control_command('@2')

    def read_voltage(self):
        response = self.send_control_command('RV')
        return response

class ElmFull(Elm):
    def _connect(self):
        self.reset()

        response = self.send_control_command('SP0')
        response = self.send_control_command('DP')
        self.send('0100')

        self.send_control_command('H1')

    def send_obdii_command(self, command):
        cmd = ['%.2X' % x for x in command]
        text = self.send(''.join(cmd))


        response = {}

        for line in text.split('\r'):
            if line == '':
                continue
            segments = line.strip().split(' ')
            ecu = int(segments[0], 16)
            data = [int(x, 16) for x in segments[1:]]

            # todo: respect sequence numbers for ooo data
            pci = data[0]
            if pci & 0xF0 == 0x00:
                # single frame
                response[ecu] = data[1:]
            elif pci & 0xF0 == 0x10:
                # first frame
                response[ecu] = data[2:]
            elif pci & 0xF0 == 0x20:
                # consecutive frame
                if ecu in response:
                    response[ecu].extend(data[1:])
                else:
                    raise Exception
            else:
                raise Exception

        return response
