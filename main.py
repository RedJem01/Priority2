import json
import os

from atlassian import Jira
import boto3
from flask import Flask
from dotenv import load_dotenv
from requests import HTTPError

app = Flask(__name__)

def process_message():
    # loading variables from .env file
    load_dotenv()
    sqs = boto3.client('sqs', region_name=os.getenv('AWS_REGION'), aws_access_key_id=os.getenv('ACCESS_KEY'),
                       aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'))

    response = sqs.receive_message(QueueUrl=os.getenv('P2_QUEUE'), MessageAttributeNames=['All'],
                                   MaxNumberOfMessages=1, WaitTimeSeconds=20)

    messages = response.get('Messages')
    if messages is not None:
        message = messages[0]
        body = json.loads(message['Body'])
        print(body)

        jira = Jira(
            url=os.getenv('JIRA_URL'),
            username=os.getenv('JIRA_EMAIL'),
            password=os.getenv('JIRA_TOKEN'),
            cloud=True
        )

        try:
            print("Attempting to create issue")
            jira.create_issue(fields={
                'project': {'key': os.getenv('JIRA_PROJECT_KEY')},
                'issuetype': {
                    "name": "Task"
                },
                 'summary': body["title"],
                 'description': body["description"],
            })
            print("Issue created")
        except HTTPError as e:
            print(e.response.text)


        sqs.delete_message(
            QueueUrl=os.getenv('P2_QUEUE'),
            ReceiptHandle=message['ReceiptHandle']
        )

if __name__ == '__main__':
    process_message()
    app.run()

@app.route('/health', methods=['GET'])
def health_check():
    return 'Service is all good', 200