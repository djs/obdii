
class UnexpectedResponse(ValueError):
    pass

class UnexpectedModeResponse(UnexpectedResponse):
    pass

class UnexpectedPIDResponse(UnexpectedResponse):
    pass

class UnexpectedDataValue(UnexpectedResponse):
    pass

class Obdii(object):
    def __init__(self, adapter):
        self.adapter = adapter

    def get_current_ect(self):
        response = self.adapter.send_obdii_command('0105')
        data = self._parse_response_data('0105', response)

        if len(data) != 1:
            raise UnexpectedDataValue

        return data[0] - 40

    def get_current_engine_rpm(self):
        response = self.adapter.send_obdii_command('010C')
        data = self._parse_response_data('010C', response)

        if len(data) != 2:
            raise UnexpectedDataValue

        return ((data[0] << 8) + (data[1])) / 4

    def _parse_response_data(self, command, response):
        command = command.strip()
        cmd = [int(command[i:i + 2], 16) for i in range(0, len(command), 2)]

        if response[0] != cmd[0] + 0x40:
            raise UnexpectedModeResponse

        if response[1] != cmd[1]:
            raise UnexpectedPIDResponse

        return response[2:]


