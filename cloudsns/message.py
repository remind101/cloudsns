import re


class Message():

    def __init__(self, message):
        self._message = self.parse_message(message)

    def parse_message(self, message):
        msg_re = re.compile("(?P<key>[^=]+)='(?P<value>[^']*)'\n")
        body = message["Body"]
        data = dict(msg_re.findall(body))
        return data

    @property
    def status(self):
        return self._message["ResourceStatus"]

    @property
    def reason(self):
        return self._message['ResourceStatusReason']
