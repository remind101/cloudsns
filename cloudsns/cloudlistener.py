import boto3
from message import Message

# Value Constants
TOPIC_NAME = 'CloudSNSTopic'


class CloudListener(object):

    def __init__(self, queue_name, session=None):
        self.session = session or boto3.Session()
        self.queue_name = queue_name

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
            }""" % (self.sqs_arn, self.sns_arn)

    def start(self):

        self.sns = self.session.client("sns")
        self.sqs = self.session.client("sqs")

        topic = self.sns.create_topic(Name=TOPIC_NAME)
        self.sns_arn = topic["TopicArn"]

        queue = self.sqs.create_queue(
            QueueName=self.queue_name,
            Attributes={"MessageRetentionPeriod": "60"}
        )
        self.sqs_url = queue["QueueUrl"]

        attr = self.sqs.get_queue_attributes(
            QueueUrl=self.sqs_url,
            AttributeNames=["QueueArn"]
        )
        self.sqs_arn = attr["Attributes"]["QueueArn"]

        self.sqs.set_queue_attributes(
            QueueUrl=self.sqs_url,
            Attributes={
                "Policy": self.create_policy()},
        )

        result = self.sns.subscribe(
            TopicArn=self.sns_arn,
            Protocol="sqs",
            Endpoint=self.sqs_arn
        )

        self.sub_arn = result["SubscriptionArn"]

        self.sns.set_subscription_attributes(
            SubscriptionArn=self.sub_arn,
            AttributeName="RawMessageDelivery",
            AttributeValue="true"
        )

    def poll(self, user_fn):
        completed = False

        while not completed:
            messages = self.get_messages()
            for message in messages:

                # Run the function and check status
                completed = user_fn(message)
                self.delete_message(message)

    def delete_message(self, message):
        self.sqs.delete_message(
            QueueUrl=self.sqs_url,
            ReceiptHandle=message.message["ReceiptHandle"]
        )

    def get_messages(self):
        updates = self.sqs.receive_message(
            QueueUrl=self.sqs_url,
            AttributeNames=["All"],
            WaitTimeSeconds=20
        )

        if "Messages" in updates:
            return [Message(m) for m in updates["Messages"]]

        return []
