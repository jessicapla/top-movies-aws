import json
import logging
import os
from typing import Any, Dict, List

import requests
from helpers.aws import store_json_s3
from helpers.environment import get_env_var
from shared_types.aws_types import SQSEvent
from shared_types.movie_list import Movie

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
    api_key = get_env_var("OMDB_API_KEY")

    logger.info("Fetching IMDb data for movie ID: %s", movie_id)
    url = f"https://www.omdbapi.com/?apikey={api_key}&i={movie_id}"

    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        logger.error("Error fetching IMDb data for movie ID %s: %s", movie_id, str(e))
        raise


def enrich_movie_list(movieList: List[Movie]) -> List[Dict[str, Any]]:
    """
    Enriches a list of movies with additional IMDb data.
    Parameters:
        movieList (List[Movie]): The list of movies to enrich.
    """
    logger.info("Enriching top 10 movies with IMDb data...")
    enriched_movies = []
    for movie in movieList:
        imdb_data = get_imdb_data(movie["id"])
        movie = {**movie, **imdb_data}
        enriched_movies.append(movie)

    return enriched_movies


def handler(event: SQSEvent, context: Any) -> None:
    """
    Main Lambda handler function.
    Processes an SQS event containing a list of top 10 movies, enriches the movie
    data with additional IMDb information, and stores the enriched data in an S3 bucket.

    Parameters:
        event: Dict containing the SQS event data.
        context: Lambda runtime context
    Returns:
        None
    """
    bucket_name = get_env_var("TOP10MOVIESSTORAGE_BUCKET_NAME")

    body = event["Records"][0]["body"]
    movies = json.loads(body).get("top10", [])

    if not movies:
        logger.warning("No movies found in the message body.")
        return

    enriched_movies = enrich_movie_list(movieList=movies)
    with_date = {
        "top10": enriched_movies,
        "date": event["Records"][0]["attributes"]["SentTimestamp"],
    }

    logger.info("Storing enriched movies in S3...")
    store_json_s3(
        data=with_date,
        bucket_name=bucket_name,
        object_key="enriched_top10_movies.json",
    )
