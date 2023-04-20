import boto3
import requests

response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
instance_id = response.text

print(instance_id)

client = boto3.client('ec2', "ap-northeast-1")

resp = client.describe_instances(
    InstanceIds=[instance_id]
)

for resv in resp['Reservations']:
    for inst in resv['Instances']:
        tags = inst['Tags']
        print([f"{tag['Key']}={tag['Value']}" for tag in tags])
