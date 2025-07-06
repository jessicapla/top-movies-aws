from typing import TypedDict


class Movie(TypedDict):
    """Type definition for a movie object from the IMDb top movies list."""
    id: str
    rank: str
    title: str
    fullTitle: str
    year: str
    image: str
    crew: str
    imDbRating: str
    imDbRatingCount: str


class MovieList(TypedDict):
    """Type definition for a list of movies."""
    items: list[Movie]

class Top10Movies(TypedDict):
    """Type definition for the top 10 movies."""
    top10: list[Movie]