import boto3
import requests
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger()
logger.setLevel("INFO")


def get_top10_movies() -> List[Dict[str, str]]:
    """
    Fetches the top 10 movies from the IMDB Top 250 Movies list.

    This function makes an HTTP GET request to the Top250Movies.json file stored in an AWS S3 bucket,
    parses the JSON response, and returns the first 10 movie items.

    Returns:
      list: A list containing dictionaries with information about the top 10 movies.
          Each dictionary contains details such as title, rating, year, etc.

    Raises:
      Exception: Logs any errors that occur during the HTTP request or JSON parsing,
            and raises them to the caller.
    """
    try:
        response = requests.get(
            "https://top-movies.s3.eu-central-1.amazonaws.com/Top250Movies.json"
        )
        data = response.json()

        logger.info("Successfully fetched list of movies.")
        return data["items"][:10]
    except Exception as e:
        logger.error(f"Error fetching Top Movies list: {str(e)}")
        raise


def send_to_sqs(
    data: Dict[str, Any],
    queueName: str,
    messageGroupId: str,
    messageDeduplicationId: str,
) -> None:
    """
    Sends data to a SQS FIFO queue.

    Parameters:
      data (Dict[str, Any]): The top 10 movies data to send.
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


def handler(event: Dict[str, Any], context: Any) -> None:
    """
    Main Lambda handler function.
    Fetches the top 10 movies and sends them to an SQS FIFO queue.
    Parameters:
        event: Dict containing the Lambda function event data
        context: Lambda runtime context
    """
    logger.info("Fetching list of top movies...")
    top_movies = get_top10_movies()
    data = {
        "movies": top_movies,
    }

    logger.info(f"Sending top movies data to SQS: {data}")
    send_to_sqs(
        data=data,
        queueName="top10-movies-stack-top10Queue-RoB0UvqyJxxk.fifo",  # TODO: export consts
        messageGroupId="top10-movies",
        messageDeduplicationId="top10-movies-batch",
    )
