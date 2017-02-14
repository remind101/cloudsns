import re


class Message():

    def __init__(self, message):
        self.message = message
        self.parsed_message = self.parse_message(message)

    def parse_message(self, message):
        msg_re = re.compile("(?P<key>[^=]+)='(?P<value>[^']*)'\n")
        body = message["Body"]
        data = dict(msg_re.findall(body))
        return data

    @property
    def status(self):
        return self.parsed_message["ResourceStatus"]

    @property
    def reason(self):
        return self.parsed_message['ResourceStatusReason']
