import elm
import json
import os
import re

import unittest
import pytest

class MockElm327(object):
    COMMAND_RECEIVED = re.compile('^(.*?)\r', re.M)

    def __init__(self):
        self.in_data = ""
        self.out_data = ""
        self.echo = True

        fh = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'elm.json'), 'r')
        self.command_table = json.load(fh)
        fh.close()

    def write(self, data):
        self.in_data = self.in_data + data

        while True:
            m = self.COMMAND_RECEIVED.search(self.in_data)
            if m:
                command = m.group(1).replace(' ', '')
                self.in_data = self.COMMAND_RECEIVED.sub('', self.in_data)

                try:
                    if self.echo:
                        self.out_data = self.out_data + command + '\r'

                    self.out_data = self.out_data + self.command_table[m.group(1)] + '\r\r>'
                except KeyError:
                    pass
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






