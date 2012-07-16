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
                  .with_args([0x01, 0x05])
                  .and_return([0x41, 0x05, 0x7b]))
        temperature = self.obd.get_current_ect()
        assert temperature == 0x7b - 40

    def test_get_current_engine_rpm(self):
        (self.mock.should_receive('send_obdii_command')
                   .with_args([0x01, 0x0c])
                   .and_return([0x41, 0x0c, 0x1a, 0xf8]))

        rpm = self.obd.get_current_engine_rpm()
        assert rpm == 1726

#    def test_is_pid_supported(self):
#        self.obd.supported_pids[0x01][0] = [0x28, 0x00, 0x01, 0x00]
#
        #assert self.obd.is_pid_supported(0x01, 0x1e)
        #assert not self.obd.is_pid_supported(0x01, 0x1f)
        #assert self.obd.is_pid_supported(0x01, 0x1c)
        #assert self.obd.is_pid_supported(0x01, 0x09)
        #assert not self.obd.is_pid_supported(0x01, 0x0a)

    def test_read_supported_pids(self):
        (self.mock.should_receive('send_obdii_command')
                  .with_args([0x01, 0x00])
                  .and_return([0x41, 0x00, 0x98, 0x18, 0x00, 0x13]))

        self.obd._read_supported_pids()






