import requests
import logging
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
    logger.info(f"Fetching list of top movies...")
    response = requests.get('https://top-movies.s3.eu-central-1.amazonaws.com/Top250Movies.json')
    data = response.json()

    logger.info(f"Successfully fetched list of movies.")
    return data["items"][:10]
  except Exception as e:
    logger.error(f"Error fetching Top Movies list: {str(e)}")
    raise


def handler(event: Dict[str, Any], context: Any) -> None:
  """
  Main Lambda handler function
  Parameters:
      event: Dict containing the Lambda function event data
      context: Lambda runtime context
  Returns:
      TODO
  """
  data = get_top10_movies()