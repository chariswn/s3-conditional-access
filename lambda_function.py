import boto3
import csv
import json
import pprint

IAM_S3ROLE_ARN= 'arn:aws:iam::608814894868:role/s3folderaccess'
IAM_S3ROLE_UniquID='AROAY3QBSB4KDLJASJNPC'



def lambda_handler(event, context):
    bucketname = 'sample-data-drop'
    username = 'luobin'
    sessionid = 'asdhfkldllge'
    userfolder = IAM_S3ROLE_UniquID+':' + sessionid
    
    
    '''assume role and get s3 client based on the role'''
    s3_access_session = get_s3_session(role_arn=IAM_S3ROLE_ARN, session_name=sessionid)
    
    s3client=s3_access_session.client('s3')
    
    '''list folder before uploading'''
    response = s3client.list_objects(
        Bucket= bucketname,
        Prefix= userfolder,
    )
    pprint.pprint("======response of listting  user folder START==========")
    pprint.pprint(response)
    pprint.pprint("======response of listting  user folder END==========")
    
    
    ''' construct file content'''
    with open('/tmp/userfile.csv', 'w', newline='') as newfile:
        file_writer = csv.writer(newfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['ARN', 'ACCOUNT', 'USERNAME'])
        mySts = s3_access_session.client('sts').get_caller_identity()
        myArn = mySts["Arn"]
        myAccount = mySts["Account"]
        myUser = myArn.split('/')[-1]
        #print("My profile user: {}".format(myUser))
        file_writer.writerow([myArn, myAccount, myUser])
        
    ''' upload file'''    
    with open('/tmp/userfile.csv', 'rb') as file_to_upload:
        response=s3client.put_object(
            Body=file_to_upload, 
            Bucket=bucketname, 
            Key=userfolder + "/userfile.csv")
        pprint.pprint("======response of uploading file to user folder START==========")
        pprint.pprint(response)
        pprint.pprint("======response of uploading file to user folder END==========")
        
    '''list folder after uploading'''
    response = s3client.list_objects(
        Bucket=bucketname,
        Prefix=userfolder,
    )
    pprint.pprint("======response of listting  user folder START==========")
    pprint.pprint(response)
    pprint.pprint("======response of listting  user folder END==========")
    
    ''' dowload file'''    
    response=s3client.get_object(
        Bucket=bucketname, 
        Key=userfolder + "/userfile.csv")
    pprint.pprint("======response of downloading file from user folder START==========")
    pprint.pprint(response)
    pprint.pprint(response['Body'].read().decode('utf-8'))
    pprint.pprint("======response of downloading file from user folder END==========")
        
    '''trying to access unauthorized folder'''
    try:
        response = s3client.list_objects(
            Bucket=bucketname,
            Prefix= IAM_S3ROLE_UniquID+':user2',
        )
        pprint.pprint("======response of listting  unauthorized folder START==========")
        pprint.pprint(response)
        pprint.pprint("======response of listting  unauthorized folder END==========")
    except Exception as e:
        pprint.pprint(e)
        return
    return


def get_s3_session(role_arn=None, session_name='my_session'):
    if role_arn:
        client = boto3.client('sts')
        response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
        print(response)
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'])
        #print(response['Credentials']['AccessKeyId'],response['Credentials']['SecretAccessKey'], response['Credentials']['SessionToken'])
        return session
    else:
        return boto3.Session()
