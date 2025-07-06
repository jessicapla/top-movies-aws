import json
import logging
from typing import Any, Dict

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_to_sqs(
    data: Dict[str, Any],
    queueName: str,
    messageGroupId: str,
    messageDeduplicationId: str,
) -> None:
    """
    Sends data to a SQS FIFO queue.

    Parameters:
      data (Dict[str, Any]): The data to send.
      queueName (str): The name of the SQS queue to send the message to.
      messageGroupId (str): The ID of the message group for FIFO queues.
      messageDeduplicationId (str): The ID used to deduplicate messages in FIFO queues.
    """
    try:
        sqs = boto3.resource("sqs")
        queue = sqs.get_queue_by_name(QueueName=queueName)

        response = queue.send_message(
            MessageBody=json.dumps(data),
            MessageGroupId=messageGroupId,
            MessageDeduplicationId=messageDeduplicationId,
        )

        logger.info(f"Message sent to SQS. MessageId: {response['MessageId']}")
    except Exception as e:
        logger.error(f"Error when sending message to SQS: {str(e)}")
        raise

def store_json_s3(data: Dict[str, Any], bucket_name: str, object_key: str) -> None:
    """
    Stores data as JSON in an S3 bucket.

    Parameters:
        data (Dict[str, Any]): The JSON data to store.
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key under which to store the data in the bucket.
    """
    
    s3 = boto3.client("s3")
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        logger.info("Successfully JSON data in S3 bucket %s under key %s", bucket_name, object_key)
    except Exception as e:
        logger.error("Error storing JSON data in S3: %s", str(e))
        raise