import elm
import json
import os
import re

import unittest
import pytest

class MockElm327(object):
    COMMAND_RECEIVED = re.compile('^(.*?)\r', re.M)

    class State(object):
        RESET = 0
        NORMAL = 1

    def __init__(self):
        self.in_data = ""
        self.out_data = ""
        self.echo = True
        self.response = True
        self.spaces = True
        self.state = self.State.RESET

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'elm.json'), 'r') as fh:
            self.command_table_h0 = json.load(fh)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'elm_h1.json'), 'r') as fh:
            self.command_table_h1 = json.load(fh)

        self._set_h0()

    def _set_h1(self):
        self.headers = True
        self.command_table = self.command_table_h1

    def _set_h0(self):
        self.headers = False
        self.command_table = self.command_table_h0

    def open(self):
        pass

    def inWaiting(self):
        return 0

    def write(self, data):
        self.in_data = self.in_data + data

        while True:
            m = self.COMMAND_RECEIVED.search(self.in_data)
            if m:
                command = m.group(1).replace(' ', '').upper()
                #print "old in_data = " + repr(self.in_data)
                self.in_data = self.COMMAND_RECEIVED.sub('', self.in_data)
                #print "new in_data = " + repr(self.in_data)

                if command == 'ATH0':
                    self._set_h0()
                elif command == 'ATH1':
                    self._set_h1()
                elif command == 'ATD':
                    self._set_h0()
                elif command == 'ATE1':
                    self.echo = True
                elif command == 'ATE0':
                    self.echo = False
                elif command == 'ATR0':
                    self.response = False
                elif command == 'ATR1':
                    self.response = True
                elif command == 'ATS0':
                    self.spaces = False
                elif command == 'ATS1':
                    self.spaces = True

                if self.response:
                    if command in self.command_table:
                        if self.echo:
                            self.out_data = self.out_data + command + '\r'

                        if self.spaces:
                            self.out_data = self.out_data + self.command_table[command] + '\r\r>'
                        else:
                            self.out_data = self.out_data + self.command_table[command].strip(' ') + '\r\r>'
                    else:
                        self.out_data = self.out_data + '?' + '\r\r>'
            else:
                break


    def read(self, count):
        rd = self.out_data[:count]
        self.out_data = self.out_data[count:]

        return rd


class ElmTests(unittest.TestCase):

    def setup_method(self, method):
        self.mock = MockElm327()
        self.elm = elm.Elm(self.mock)

    def test_reset(self):
        # supported device
        self.elm.reset()

        # unsupported device
        self.mock.command_table['ATZ'] = '\r\rELM328 v1.1a'
        with pytest.raises(Exception):
            self.elm.reset()

    def test_warm_reset(self):
        # supported device
        self.elm.warm_reset()

        # unsupported device
        self.mock.command_table['ATWS'] = '\r\rELM328 v1.1a'
        with pytest.raises(Exception):
            self.elm.warm_reset()

    def test_connect(self):
        self.elm._connect()


    def test_read_voltage(self):
        data = self.elm.read_voltage()
        assert data == '12.3V'

    def test_get_device_info(self):
        self.elm.get_device_info()

    def test_send_obdii_command(self):
        expected_response = [0x41, 0x0c, 0x1a, 0xf8]

        data = self.elm.send_obdii_command([0x01, 0x0c])
        assert data == expected_response

class ElmFullTests(unittest.TestCase):
    def setup_method(self, method):
        self.mock = MockElm327()
        self.elm = elm.ElmFull(self.mock)

    def test_send_obdii_command(self):
        expected_response = {0x7e8: [0x41, 0x0c, 0x0b, 0xa4, 0x0, 0x0, 0x0],
                             0x7e9: [0x41, 0x0c, 0x0b, 0xa0, 0x0, 0x0, 0x0]}

        data = self.elm.send_obdii_command([0x01, 0x0c])
        assert data == expected_response

    def test_send_obdii_command_with_ml_resp(self):
        expected_response = {0x7e8: [0x49, 0x02, 0x01, 0x31, 0x46, 0x41, 0x48, 0x50, 0x33, 0x4A, 0x32, 0x31, 0x43, 0x4c, 0x32, 0x31, 0x32, 0x39, 0x37, 0x38]}

        data = self.elm.send_obdii_command([0x09, 0x02])
        assert data == expected_response
        print ''.join(chr(i) for i in data[0x7e8][3:])
