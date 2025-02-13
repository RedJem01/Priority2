import json
from unittest.mock import patch
import main

class FakeJira:
    def create_issue(self, fields):
        return "Sent"

@patch('main.Jira')
def test_process_message(jira_mock, sqs_client):
    queue = sqs_client.create_queue(QueueName='queue')

    queue_url = queue['QueueUrl']


    # override function global URL variable
    main.P2_QUEUE = queue_url

    jira_mock.return_value = FakeJira()

    expected_msg = json.dumps({'description': 'Happening right now', 'title': 'Bug'})
    sqs_messages = sqs_client.send_message(QueueUrl=queue_url, MessageBody=expected_msg)

    main.process_message()

    messages = sqs_messages.get('Messages')

    assert jira_mock.called
    assert messages is None


@patch('main.Jira')
def test_process_message_wrong_data(jira_mock, sqs_client):
    queue = sqs_client.create_queue(QueueName='queue')

    queue_url = queue['QueueUrl']


    # override function global URL variable
    main.P2_QUEUE = queue_url

    jira_mock.return_value = FakeJira()

    expected_msg = json.dumps({'description': 'Happening right now'})
    sqs_messages = sqs_client.send_message(QueueUrl=queue_url, MessageBody=expected_msg)

    main.process_message()

    messages = sqs_messages.get('Messages')

    assert jira_mock.called == False
    assert messages is None