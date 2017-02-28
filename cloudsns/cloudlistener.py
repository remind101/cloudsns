import boto3
from message import Message
import uuid
import logging

# Value Constants
TOPIC_NAME = 'CloudSNSTopic'


class NotInitialized(Exception):

    def __init__(self, name, *args, **kwargs):
        message = "`%s` has not been initialized yet. " % name
        message += "Call the start method to initialize everything"

        super(NotInitialized).__init__(message, *args, **kwargs)


class CloudListener(object):

    def __init__(self, queue_name, session=None):
        self.session = session or boto3.Session()
        self.queue_name = queue_name
        self._queueUrl = None
        self._topicArn = None
        self._queueArn = None

    def create_policy(self):
        return """{
              "Version":"2012-10-17",
              "Statement":[
                {
                  "Sid":"SNSCloudPolicy",
                  "Effect":"Allow",
                  "Principal":"*",
                  "Action":"sqs:SendMessage",
                  "Resource":"%s",
                  "Condition":{
                    "ArnEquals":{
                      "aws:SourceArn":"%s"
                    }
                  }
                }
              ]
            }""" % (self.QueueArn, self.TopicArn)

    def start(self):
        logging.info('Creating cloudsns resources')
        self.sns = self.session.client("sns")
        self.sqs = self.session.client("sqs")

        self.sqs.set_queue_attributes(
            QueueUrl=self.QueueUrl,
            Attributes={
                "Policy": self.create_policy()},
        )

        result = self.sns.subscribe(
            TopicArn=self.TopicArn,
            Protocol="sqs",
            Endpoint=self.QueueArn
        )

        sub_arn = result["SubscriptionArn"]

        self.sns.set_subscription_attributes(
            SubscriptionArn=sub_arn,
            AttributeName="RawMessageDelivery",
            AttributeValue="true"
        )
        logging.info('Done creating cloudsns resources')

    @property
    def TopicArn(self):
        if not self.sqs or not self.sns:
            raise NotInitialized('TopicArn')
        if not self._topicArn:
            topic = self.sns.create_topic(Name=TOPIC_NAME)
            self._topicArn = topic["TopicArn"]

        return self._topicArn

    @property
    def QueueUrl(self):
        if not self.sqs or not self.sns:
            raise NotInitialized('QueueUrl')
        if not self._queueUrl:
            prefix = str(uuid.uuid4())
            queue = self.sqs.create_queue(
                QueueName="%s_%s" % (self.queue_name, str(uuid.uuid4())),
                Attributes={"MessageRetentionPeriod": "60"}
            )
            self._queueUrl = queue["QueueUrl"]

        return self._queueUrl

    @property
    def QueueArn(self):
        if not self.sqs or not self.sns:
            raise NotInitialized('QueueArn')
        if not self._queueArn:
            attr = self.sqs.get_queue_attributes(
                QueueUrl=self.QueueUrl,
                AttributeNames=["QueueArn"]
            )
            self._queueArn = attr["Attributes"]["QueueArn"]

        return self._queueArn

    def poll(self, user_fn):
        completed = False
        while not completed:
            messages = self.get_messages()
            for message in messages:
                completed = user_fn(message)
                message.delete()

    def get_messages(self):
        updates = self.sqs.receive_message(
            QueueUrl=self.QueueUrl,
            AttributeNames=["All"],
            WaitTimeSeconds=20
        )

        if "Messages" in updates:
            return [Message(m, self) for m in updates["Messages"]]

        return []

    def delete_messages(self, messages):
        receipts = []
        for m in messages:
            unique_id = str(uuid.uuid4())
            receipts.append({
                'Id': unique_id,
                'ReceiptHandle': m.ReceiptHandle
            })

        self.sqs.delete_message_batch(
            QueueUrl=self.QueueUrl,
            Entries=receipts
        )

    def purge(self):
        self.sqs.purge_queue(QueueUrl=self.QueueUrl)

    def close(self):
        logging.info('Deleting cloudsns resources')
        self.sqs.delete_queue(
            QueueUrl=self.QueueUrl
        )

        self.sns.delete_topic(
            TopicArn=self.TopicArn
        )
        logging.info('Done deleting cloudsns resources')
