import boto3
import json
import re
from cloudsns.cloudlistener import CloudListener
import os

TEMPLATE_PATH = "cloudsns/integration_test/template.json"
STACK_NAME = "my-test-stack"

session = boto3.Session(region_name="us-east-1")
cfn = session.client("cloudformation")

listener = CloudListener("cloudSNSListener", session=session)
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


def print_status(message):
    print "Stack Status: %s" % message.status

    if (message.status == "CREATE_COMPLETE" or
            message.status == "DELETE_COMPLETE"):
        return True

    return False

print "Creating stack."
create_stack()

listener.poll(print_status)

print "Deleting stack."
delete_stack()

listener.poll(print_status)
