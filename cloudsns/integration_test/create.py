import boto3
import json
import re
from cloudsns.cloudlistener import CloudListener
import os

TEMPLATE_PATH = "cloudsns/integration_test/template.json"
STACK_NAME = "my-test-stack"

# create session and listeners
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
        NotificationARNs=[listener.TopicArn]
    )


def delete_stack():
    cfn.delete_stack(
        StackName=STACK_NAME,
    )


def print_msg(message):
    print "Stack Status: %s - %s" % (message.ResourceStatus,
                                     message.EventId)


def run_once(end_status):
    def print_fn(message):
        print_msg(message)
        return (message.ResourceStatus == end_status)
    return print_fn


print "*-----------------------------------*"
print "Creating stack."
create_stack()
listener.poll(run_once("CREATE_COMPLETE"))


print "*-----------------------------------*"
print "Deleting stack."
delete_stack()
listener.poll(run_once("DELETE_COMPLETE"))

print "*-----------------------------------*"
print "Stack creation with more granular control"
create_stack()
completed = False
while not completed:
    messages = listener.get_messages()
    for message in messages:
        print_msg(message)
        if message.ResourceStatus == "CREATE_COMPLETE":
            completed = True
        message.delete()

print "*-----------------------------------*"
print "Stack deletion with more granular control"
delete_stack()
completed = False
while not completed:
    messages = listener.get_messages()
    for message in messages:
        print_msg(message)
        if message.ResourceStatus == "DELETE_COMPLETE":
            completed = True
        message.delete()

print "*-----------------------------------*"
print "Demo completed succesfully!"
