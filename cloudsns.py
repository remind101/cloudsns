import boto3
from message import Message

# Value Constants
QUEUE_NAME = 'CloudSNSQueue'
TOPIC_NAME = 'CloudSNSTopic'


class CloudSNS(object):

    def __init__(self, session=None):

        if not session:
            session = boto3.Session(region_name="us-east-1")

        self.session = session

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
            QueueName=QUEUE_NAME,
            Attributes={"MessageRetentionPeriod": "60"}
        )
        self.sqs_url = queue["QueueUrl"]

        attr = self.sqs.get_queue_attributes(
            QueueUrl=self.sqs_url,
            AttributeNames=["QueueArn"]
        )
        self.sqs_arn = attr["Attributes"]["QueueArn"]

        print self.create_policy()

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

    def get_messages(self):
        updates = self.sqs.receive_message(
            QueueUrl=self.sqs_url,
            AttributeNames=["All"],
            WaitTimeSeconds=20
        )

        res = []

        if "Messages" in updates:
            for message in updates["Messages"]:
                self.sqs.delete_message(
                    QueueUrl=self.sqs_url,
                    ReceiptHandle=message["ReceiptHandle"]
                )
                res.append(Message(message))

        print "Able to return"

        return res
