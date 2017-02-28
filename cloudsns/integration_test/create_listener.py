import boto3
from cloudsns.cloudlistener import CloudListener
import uuid

# create session and listeners
session = boto3.Session(region_name="us-east-1")
cfn = session.client("cloudformation")
listener = CloudListener(str(uuid.uuid4()), session=session)
listener.start()
