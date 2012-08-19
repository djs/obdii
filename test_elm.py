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
        self.state = self.State.RESET

        fh = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'elm.json'), 'r')
        self.command_table_h0 = json.load(fh)
        fh.close()

        fh = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'elm_h1.json'), 'r')
        self.command_table_h1 = json.load(fh)
        fh.close()

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
                print "old in_data = " + repr(self.in_data)
                self.in_data = self.COMMAND_RECEIVED.sub('', self.in_data)
                print "new in_data = " + repr(self.in_data)

                if command == 'ATH0':
                    self._set_h0()
                elif command == 'ATH1':
                    self._set_h1()

                if command in self.command_table:
                    if self.echo:
                        self.out_data = self.out_data + command + '\r'

                    self.out_data = self.out_data + self.command_table[command] + '\r\r>'
                else:
                    print "wtf @ " + command
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






