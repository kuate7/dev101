import json
from botocore.vendored import requests
import boto3
import base64
from botocore.exceptions import ClientError

# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/





def get_secret():

    secret_name = "ServiceNowSecret"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])





def lambda_handler(event, context):
    #print(event)
    secretRespose = get_secret()
    print(secretRespose)
    
    instance_id = event['detail']['instance-id']
    instance_state = event['detail']['state']
    region = event['region']
    


    

    client = boto3.client('ec2')
    
    response = client.describe_instances(
    InstanceIds=[
        instance_id,
    ]
)

    #print(response)
    
    try: 
        private_ip_address = response["Reservations"][0]["Instances"][0]["PrivateIpAddress"]
    except:
        private_ip_address = ""
        
    
    try:    
        public_ip_address = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    except:
        public_ip_address = ""
  
    try:
        vpc_id = response["Reservations"][0]["Instances"][0]["VpcId"]
    except:
        vpc_id = ""
        

    #print(vpc_id)
    
    payload = ("{\"u_instance_id\": \"" + instance_id + "\", \
\"u_instance_state\": \"" + instance_state + "\", \
\"u_private_ip_address\": \"" + private_ip_address + "\", \
\"u_public_ip_address\": \"" + public_ip_address + "\", \
\"u_region\": \"" + region + "\", \
\"u_vpc_id\": \"" + vpc_id + "\" \
}")
    
    
   # \"u_instance_state\":\"running\", \
   # \"u_private_ip_address\":\"10.0.0.3\", \
   # \"\":\"7.7.7.7\", \
   # \"\":\"us-east-1\", \ 
    #\"u_security_group_id\":\"sgroup-12345\", \
    #\"\":\"vpc-67890\"}")
    
    #print(payload)
    
    # Set the request parameters
    url = 'https://dev51495.service-now.com/api/now/import/u_ec2_instanse_state'
    # Eg. User name="admin", Password="admin" for this code sample.
    
    user = ""
    pwd = ""
    
    
    
    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    
    # Do the HTTP request
    response = requests.post(url, auth=(user, pwd), headers=headers ,data=payload)
    
    # Check for HTTP codes other than 200
    if response.status_code != 201:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data
    data = response.json()
    #print(data)
    print("this is a test for luis")
  
    
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully Uploaded to ServiceNow')
    }
