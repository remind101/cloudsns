import boto3
import json
import re
from cloudsns import CloudSNS

session = boto3.Session(region_name="us-east-1")

cfn = session.client("cloudformation")

STACK_NAME = "my-test-stack"

listener = CloudSNS(session)

listener.start()


def create_stack():
    with open("template.json") as fd:
        template = fd.read()

    cfn.create_stack(
        StackName=STACK_NAME,
        TemplateBody=template,
        NotificationARNs=[listener.sns_arn]
    )


def delete_stack():
    cfn.delete_stack(
        StackName=STACK_NAME,
    )

print "Creating stack."
create_stack()

complete = False

while not complete:
    messages = listener.get_messages()
    for message in messages:
        print message.reason
        print message.status


print "Deleting stack."
delete_stack()

complete = False

while not complete:
    messages = listener.get_messages()
    for message in messages:
        if message.status == "DELETE_COMPLETE":
            complete = True
