import json
import logging
import os
from typing import Any, Dict, List

import requests

from shared_types.aws_types import SQSEvent
from shared_types.movie_list import Top10Movies, Movie

logger = logging.getLogger()
logger.setLevel("INFO")


def get_imdb_data(movie_id: str) -> dict:
    """
    Fetches additional IMDb data for a given movie ID.

    Parameters:
        movie_id (str): The IMDb ID of the movie.

    Returns:
        dict: A dictionary containing the IMDb data for the movie.
    """
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        logger.error("OMDB_API_KEY environment variable is not set.")
        raise ValueError("OMDB_API_KEY environment variable is not set.")

    logger.info("Fetching IMDb data for movie ID: %s", movie_id)
    url = f"https://www.omdbapi.com/?apikey={api_key}&i={movie_id}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        logger.error("Error fetching IMDb data for movie ID %s: %s", movie_id, str(e))
        raise


def enrich_movie_list(movieList: List[Movie]) -> List[Dict[str, Any]]:
    """Placeholder"""
    """
    Enriches the top 10 movies with additional IMDb data.

    Parameters:
        top10Movies (Top10Movies): The top 10 movies to enrich.
    """
    logger.info("Enriching top 10 movies with IMDb data...")
    enriched_movies = []
    for movie in movieList:
        imdb_data = get_imdb_data(movie["id"])
        movie = {**movie, **imdb_data}
        enriched_movies.append(movie)

    return enriched_movies

def store_s3_data(data: Dict[str, Any], bucket_name: str, object_key: str) -> None:
    """
    Stores the enriched movie data in an S3 bucket.

    Parameters:
        data (Dict[str, Any]): The enriched movie data to store.
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key under which to store the data in the bucket.
    """
    import boto3

    s3 = boto3.client("s3")
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        logger.info("Successfully stored enriched movies in S3 bucket %s under key %s", bucket_name, object_key)
    except Exception as e:
        logger.error("Error storing enriched movies in S3: %s", str(e))
        raise


def handler(event: SQSEvent, context: Any) -> None:
    """
    Main Lambda handler function
    Parameters:
        event: Dict containing the Lambda function event data. This should be an SQS event.
        context: Lambda runtime context
    Returns:
        TODO
    """
    body = event["Records"][0]["body"]
    logger.info("Processing body: %s", body)
    movies = json.loads(body).get("top10", [])

    if not movies:
        logger.warning("No movies found in the message body.")
        return

    enriched_movies = enrich_movie_list(movieList=movies)
    logger.info("Enriched movies: %s", enriched_movies)
    with_date = {
        "top10": enriched_movies,
        "date": event["Records"][0]["attributes"]["SentTimestamp"]}
    logger.info("Storing enriched movies in S3...")
    store_s3_data(
        data=with_date,
        bucket_name="top10-movies-stack-top10moviesstorage-mdsjbvn2jnp2", # TODO
        object_key="enriched_top10_movies.json"
    )