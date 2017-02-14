import boto3
import json
import re
from cloudsns.cloudlistener import CloudListener
import os

TEMPLATE_PATH = "cloudsns/integration_test/template.json"
STACK_NAME = "my-test-stack"

session = boto3.Session(region_name="us-east-1")
cfn = session.client("cloudformation")

listener = CloudListener(session)
listener.start()


def create_stack():
    with open(os.path.abspath(TEMPLATE_PATH)) as fd:
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
        print "Stack status: %s" % message.status
        if message.status == "CREATE_COMPLETE":
            complete = True


print "Deleting stack."
delete_stack()

complete = False

while not complete:
    messages = listener.get_messages()
    for message in messages:
        print "Stack status: %s" % message.status
        if message.status == "DELETE_COMPLETE":
            complete = True
