
class UnexpectedResponse(ValueError):
    pass

class UnexpectedModeResponse(UnexpectedResponse):
    pass

class UnexpectedPIDResponse(UnexpectedResponse):
    pass

class UnexpectedDataValue(UnexpectedResponse):
    pass

class Obdii(object):
    supported_pids = { 0x01 : {},
                       0x05 : {}
                       }
    def __init__(self, adapter):
        self.adapter = adapter

    def _get_response(self, command):
        response = self.adapter.send_obdii_command(command)
        data = self._parse_response_data(command, response)

        return data

    def get_current_ect(self):
        data = self._get_response([0x01, 0x05])

        if len(data) != 1:
            raise UnexpectedDataValue

        return data[0] - 40

    def get_current_engine_rpm(self):
        data = self._get_response([0x01, 0x0C])

        if len(data) != 2:
            raise UnexpectedDataValue

        return ((data[0] << 8) + (data[1])) / 4

    def get_vehicle_speed(self):
        data = self._get_response([0x01, 0x0D])

        if len(data) != 1:
            raise UnexpectedDataValue

        return data[0]

    def get_throttle_position(self):
        data = self._get_response([0x01, 0x11])

        if len(data) != 1:
            raise UnexpectedDataValue

        return (data[0] * 100.0) / 255

    def get_fuel_level_input(self):
        data = self._get_response([0x01, 0x2F])

        if len(data) != 1:
            raise UnexpectedDataValue

        return data[0]

    def get_maf_airflow_rate(self):
        data = self._get_response([0x01, 0x10])

        if len(data) != 2:
            raise UnexpectedDataValue

        return ((data[0] << 8) + (data[1]))

    def _parse_response_data(self, command, response):
        #command = command.strip()
        #cmd = [int(command[i:i + 2], 16) for i in range(0, len(command), 2)]

        if response[0] != command[0] + 0x40:
            raise UnexpectedModeResponse

        if response[1] != command[1]:
            raise UnexpectedPIDResponse

        return response[2:]

    def _read_supported_pids(self):
        control_pids = [0x00, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0]

        mode = 0x01
        for cp in control_pids:
            if cp == 0x00 or self.is_pid_supported(mode, cp):
                self.supported_pids[mode][cp] = self._get_response([mode, cp])
            else:
                break

    def is_pid_supported(self, mode, pid):
        if pid > 0xE0:
            raise ValueError

        if pid == 0:
            return True

        cp = ((pid - 1) / 0x20) * 0x20
        co = pid - cp - 1
        cs = 3  - (co / 8)

        if self.supported_pids[mode][cp][cs] & (1 << ((co % 8) - 1)):
            return True
        else:
            return False

    def get_supported_pids(self, mode):
        supported = []

        for pid in range(0, 0xe0):
            if self.is_pid_supported(mode, pid):
                supported.append(pid)

        return supported


