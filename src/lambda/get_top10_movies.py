import logging
import os
from typing import Any, Dict, List

import requests
from helpers.aws import send_to_sqs
from shared_types.movie_list import Movie, Top10Movies

logger = logging.getLogger()
logger.setLevel("INFO")

TOP_MOVIES_URL = "https://top-movies.s3.eu-central-1.amazonaws.com/Top250Movies.json"


def get_top10_movies() -> List[Movie]:
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
        logger.info("Fetching list of top movies...")
        response = requests.get(TOP_MOVIES_URL)
        data = response.json()

        logger.info("Successfully fetched list of movies.")
        return data["items"][:10]
    except Exception as e:
        logger.error(f"Error fetching Top Movies list: {str(e)}")
        raise


def handler(event: Dict[str, Any], context: Any) -> None:
    """
    Main Lambda handler function.
    Fetches the top 10 movies and sends them to an SQS FIFO queue.
    Parameters:
        event: Dict containing the Lambda function event data
        context: Lambda runtime context
    """

    queue_name = os.environ.get("TOP10QUEUE_QUEUE_NAME")
    if not queue_name:
        logger.error("TOP10QUEUE_QUEUE_NAME environment variable is not set.")
        raise ValueError("TOP10QUEUE_QUEUE_NAME environment variable is not set.")

    top_movies = get_top10_movies()
    data: Top10Movies = {
        "top10": top_movies,
    }

    logger.info(f"Sending top movies data to SQS: {data}")
    send_to_sqs(
        data=dict(data),
        queueName=queue_name,
        messageGroupId="top10-movies",
        messageDeduplicationId="top10-movies-batch",
    )
