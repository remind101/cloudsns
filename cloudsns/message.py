import re


class Message(object):

    def __init__(self, metadata, parent_queue):
        self._metadata = metadata
        self._parent_queue = parent_queue

        parsed_message = self.parse_message(metadata)

        for key, value in parsed_message.iteritems():
            setattr(self, key, value)

    def parse_message(self, message):
        msg_re = re.compile("(?P<key>[^=]+)='(?P<value>[^']*)'\n")
        body = message["Body"]
        data = dict(msg_re.findall(body))
        return data

    def delete(self):
        self._parent_queue.sqs.delete_message(
            QueueUrl=self._parent_queue.QueueUrl,
            ReceiptHandle=self._metadata["ReceiptHandle"]
        )
