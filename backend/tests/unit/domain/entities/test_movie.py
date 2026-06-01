"""Tests for the Movie entity."""

import pytest

from app.core.domain.entities.movie import Movie
from app.core.domain.entities.person import Person
from app.core.domain.entities.studio import Studio
from app.core.domain.value_objects.cast_member import CastMember
from app.core.domain.value_objects.certification import Certification
from app.core.domain.value_objects.collection_membership import CollectionMembership
from app.core.domain.value_objects.media_links import MediaLinks
from app.core.domain.value_objects.ratings import Ratings


@pytest.fixture
def director() -> Person:
    return Person(tmdb_id=525, name="Christopher Nolan")


@pytest.fixture
def actor() -> Person:
    return Person(tmdb_id=6193, name="Leonardo DiCaprio")


@pytest.fixture
def studio() -> Studio:
    return Studio(tmdb_id=174, name="Warner Bros. Pictures")


@pytest.fixture
def media_links() -> MediaLinks:
    return MediaLinks(
        poster_url="https://image.tmdb.org/poster.jpg",
        trailer_url="https://youtube.com/watch?v=abc",
    )


@pytest.fixture
def ratings() -> Ratings:
    return Ratings(
        community_score=8.8,
        vote_count=35000,
        certifications=(Certification(country="US", rating="PG-13"),),
    )


@pytest.fixture
def cast(actor: Person) -> tuple[CastMember, ...]:
    return (CastMember(person=actor, character_name="Dom Cobb"),)


@pytest.fixture
def valid_movie(
    director: Person,
    cast: tuple[CastMember, ...],
    studio: Studio,
    media_links: MediaLinks,
    ratings: Ratings,
) -> Movie:
    return Movie(
        tmdb_id=27205,
        title="Inception",
        synopsis="A thief who steals corporate secrets through dream-sharing technology.",
        release_year=2010,
        director=director,
        cast=cast,
        studios=(studio,),
        media_links=media_links,
        ratings=ratings,
        original_language="en",
    )


class TestMovieCreation:
    """Valid construction scenarios."""

    def test_creates_with_required_fields(self, valid_movie: Movie) -> None:
        assert valid_movie.tmdb_id == 27205
        assert valid_movie.title == "Inception"
        assert valid_movie.release_year == 2010
        assert valid_movie.original_language == "en"
        assert valid_movie.collection_membership is None

    def test_original_language_normalised_to_lowercase(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        movie = Movie(
            tmdb_id=27205,
            title="Inception",
            synopsis="A synopsis.",
            release_year=2010,
            director=director,
            cast=cast,
            studios=(studio,),
            media_links=media_links,
            ratings=ratings,
            original_language="EN",
        )
        assert movie.original_language == "en"

    def test_creates_with_collection_membership(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        membership = CollectionMembership(collection_id=263, collection_name="The Dark Knight Trilogy", order=2)
        movie = Movie(
            tmdb_id=155,
            title="The Dark Knight",
            synopsis="Batman raises the stakes in his war on crime.",
            release_year=2008,
            director=director,
            cast=cast,
            studios=(studio,),
            media_links=media_links,
            ratings=ratings,
            original_language="en",
            collection_membership=membership,
        )
        assert movie.collection_membership == membership

    def test_director_also_in_cast(self, studio: Studio, media_links: MediaLinks, ratings: Ratings) -> None:
        """A director acting in their own film appears in both fields."""
        clint = Person(tmdb_id=190, name="Clint Eastwood")
        cast = (CastMember(person=clint, character_name="Walt Kowalski"),)
        movie = Movie(
            tmdb_id=12345,
            title="Gran Torino",
            synopsis="A grumpy war veteran befriends a Hmong teenager.",
            release_year=2008,
            director=clint,
            cast=cast,
            studios=(studio,),
            media_links=media_links,
            ratings=ratings,
            original_language="en",
        )
        assert movie.director == movie.cast[0].person

    def test_release_year_at_minimum_boundary(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        movie = Movie(
            tmdb_id=1,
            title="Roundhay Garden Scene",
            synopsis="The oldest surviving film.",
            release_year=1888,
            director=director,
            cast=cast,
            studios=(studio,),
            media_links=media_links,
            ratings=ratings,
            original_language="en",
        )
        assert movie.release_year == 1888


class TestMovieValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_zero_tmdb_id_raises(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        with pytest.raises(ValueError, match="tmdb_id"):
            Movie(
                tmdb_id=0,
                title="Inception",
                synopsis="A synopsis.",
                release_year=2010,
                director=director,
                cast=cast,
                studios=(studio,),
                media_links=media_links,
                ratings=ratings,
                original_language="en",
            )

    def test_empty_title_raises(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        with pytest.raises(ValueError, match="title"):
            Movie(
                tmdb_id=27205,
                title="",
                synopsis="A synopsis.",
                release_year=2010,
                director=director,
                cast=cast,
                studios=(studio,),
                media_links=media_links,
                ratings=ratings,
                original_language="en",
            )

    def test_empty_synopsis_raises(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        with pytest.raises(ValueError, match="synopsis"):
            Movie(
                tmdb_id=27205,
                title="Inception",
                synopsis="",
                release_year=2010,
                director=director,
                cast=cast,
                studios=(studio,),
                media_links=media_links,
                ratings=ratings,
                original_language="en",
            )

    def test_release_year_before_1888_raises(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        with pytest.raises(ValueError, match="release_year"):
            Movie(
                tmdb_id=27205,
                title="Inception",
                synopsis="A synopsis.",
                release_year=1887,
                director=director,
                cast=cast,
                studios=(studio,),
                media_links=media_links,
                ratings=ratings,
                original_language="en",
            )

    def test_empty_studios_tuple_raises(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        with pytest.raises(ValueError, match="studios"):
            Movie(
                tmdb_id=27205,
                title="Inception",
                synopsis="A synopsis.",
                release_year=2010,
                director=director,
                cast=cast,
                studios=(),
                media_links=media_links,
                ratings=ratings,
                original_language="en",
            )

    def test_invalid_original_language_raises(
        self,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        with pytest.raises(ValueError, match="original_language"):
            Movie(
                tmdb_id=27205,
                title="Inception",
                synopsis="A synopsis.",
                release_year=2010,
                director=director,
                cast=cast,
                studios=(studio,),
                media_links=media_links,
                ratings=ratings,
                original_language="eng",
            )


class TestMovieImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_title_is_immutable(self, valid_movie: Movie) -> None:
        with pytest.raises(Exception):
            valid_movie.title = "Other"  # type: ignore[misc]

    def test_cast_tuple_cannot_be_replaced(self, valid_movie: Movie) -> None:
        with pytest.raises(Exception):
            valid_movie.cast = ()  # type: ignore[misc]


class TestMovieEquality:
    """Identity-based equality on tmdb_id."""

    def test_same_tmdb_id_are_equal(
        self,
        valid_movie: Movie,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        duplicate = Movie(
            tmdb_id=27205,
            title="Inception (different title object)",
            synopsis="Different synopsis.",
            release_year=2010,
            director=director,
            cast=cast,
            studios=(studio,),
            media_links=media_links,
            ratings=ratings,
            original_language="en",
        )
        assert valid_movie == duplicate

    def test_different_tmdb_id_not_equal(
        self,
        valid_movie: Movie,
        director: Person,
        cast: tuple[CastMember, ...],
        studio: Studio,
        media_links: MediaLinks,
        ratings: Ratings,
    ) -> None:
        other = Movie(
            tmdb_id=99999,
            title="Inception",
            synopsis="A synopsis.",
            release_year=2010,
            director=director,
            cast=cast,
            studios=(studio,),
            media_links=media_links,
            ratings=ratings,
            original_language="en",
        )
        assert valid_movie != other

    def test_hashable_and_usable_in_set(self, valid_movie: Movie) -> None:
        assert len({valid_movie, valid_movie}) == 1

    def test_not_equal_to_other_types(self, valid_movie: Movie) -> None:
        assert valid_movie != 27205
        assert valid_movie != "Inception"
