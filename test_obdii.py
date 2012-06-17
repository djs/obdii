import obdii

import json
import os
import re

from flexmock import flexmock
import unittest
import pytest



class ObdiiTests(unittest.TestCase):

    def setup_method(self, method):
        self.mock = flexmock()
        self.obd = obdii.Obdii(self.mock)

    def test_get_current_ect(self):
        (self.mock.should_receive('send_obdii_command')
                  .with_args('0105')
                  .and_return([0x41, 0x05, 0x7b]))
        temperature = self.obd.get_current_ect()
        assert temperature == 0x7b - 40

    def test_get_current_engine_rpm(self):
        (self.mock.should_receive('send_obdii_command')
                   .with_args('010C')
                   .and_return([0x41, 0x0c, 0x1a, 0xf8]))

        rpm = self.obd.get_current_engine_rpm()
        assert rpm == 1726






