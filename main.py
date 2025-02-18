import json
import logging
import os
import threading

from atlassian import Jira
import boto3
from flask import Flask
from dotenv import load_dotenv
from requests import HTTPError

app = Flask(__name__)

# loading variables from .env file
load_dotenv()
AWS_REGION = os.getenv('AWS_REGION')
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
P2_QUEUE = os.getenv('P2_QUEUE')
JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def process_message():
    sqs = boto3.client('sqs', region_name=AWS_REGION, aws_access_key_id=ACCESS_KEY,
                       aws_secret_access_key=SECRET_ACCESS_KEY)

    response = sqs.receive_message(QueueUrl=P2_QUEUE, MessageAttributeNames=['All'],
                                   MaxNumberOfMessages=1, WaitTimeSeconds=20)

    messages = response.get('Messages')
    if messages is not None:
        message = messages[0]
        logger.info("Message received from queue with ID" + json.dumps(response.get('MessageId')))
        body = json.loads(message['Body'])
        if "title" in body and "description" in body:
            if body["title"] and body["description"]:

                jira = Jira(
                    url=JIRA_URL,
                    username=JIRA_EMAIL,
                    password=JIRA_TOKEN,
                    cloud=True
                )

                try:
                    logger.info("Attempting to create issue")
                    jira.create_issue(fields={
                        'project': {'key': JIRA_PROJECT_KEY},
                        'issuetype': {
                            "name": "Task"
                        },
                         'summary': body["title"],
                         'description': body["description"],
                    })
                    logger.info("Jira task created, payload" + json.dumps({
                        'project': {'key': JIRA_PROJECT_KEY},
                        'issuetype': {
                            "name": "Task"
                        },
                         'summary': body["title"],
                         'description': body["description"],
                    }))
                    logger.info("Issue created")
                except HTTPError as e:
                    logger.error(e.response.text)
            else:
                logger.error("Either the title or description or both are empty")
        else:
            logger.error("Either the title or description or both are missing from the SQS message")


        sqs.delete_message(
            QueueUrl=P2_QUEUE,
            ReceiptHandle=message['ReceiptHandle']
        )
        logger.info("Message deleted from queue with ID" + json.dumps(response.get('MessageId')))
    else:
        logger.info("No messages in queue")

def background_thread():
    thread = threading.Thread(target=process_message, daemon=True)
    thread.start()
    return thread

bg_thread = background_thread()

if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0")
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        stop_flag = True
        bg_thread.join()

@app.route('/', methods=['GET'])
def health_check():
    return 'OK', 200