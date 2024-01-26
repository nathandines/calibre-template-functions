from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Protocol, Set, Union


class CalibreDbApi(Protocol):
    def search(self, query: str) -> List[int]:
        ...

    def field_for(
        self, field_name: str, book_id: int, default_return: Optional[str] = None
    ) -> Optional[Union[str, float]]:
        ...


class CalibreDb(Protocol):
    @property
    def new_api(self) -> CalibreDbApi:
        ...


class CalibreContext(Protocol):
    @property
    def arguments(self) -> List[str]:
        ...

    @property
    def db(self) -> CalibreDb:
        ...


class CalibreBook(Protocol):
    @property
    def series(self) -> Optional[str]:
        ...

    @property
    def series_index(self) -> float:
        ...


@dataclass
class Book:
    identifier: int
    title: str
    series_index: float
    series: Optional[str]

    def __hash__(self) -> int:
        return self.identifier


def print_result(
    number: Union[Decimal, float], zero_padding: int, decimal_places: int
) -> str:
    """Print result. Integers should not show any decimal places."""
    number = Decimal(number)
    if number % 1 == 0:
        return "{:0>{zero_padding}d}".format(int(number), zero_padding=zero_padding)
    return "{:0>{zero_padding}.{decimal_places}f}".format(
        float(number),
        zero_padding=zero_padding + decimal_places + 1,
        decimal_places=decimal_places,
    )


def count_decimal_places(number: Union[Decimal, float]) -> int:
    """Count decimal places to a max of two places"""
    number = Decimal(number)
    return abs(int(round(number, 2).normalize().as_tuple().exponent))


def count_whole_digits(number: Union[Decimal, float]) -> int:
    """Count whole digits. Minimum of one place returned, even for zero values."""
    number = Decimal(number)
    num_tuple = number.normalize().as_tuple()
    exponent = int(num_tuple.exponent)
    digits = num_tuple.digits if exponent == 0 else num_tuple.digits[:exponent]
    return max(1, len(digits))


def get_books_in_series(calibre_db: CalibreDbApi, series_name: str) -> Set[Book]:
    book_ids = calibre_db.search(f'series:"={series_name}"')
    output = set()
    for book_id in book_ids:
        title = calibre_db.field_for("title", book_id)
        assert isinstance(title, str)

        series = calibre_db.field_for("series", book_id, None)
        assert isinstance(series, str) or series is None

        series_index = calibre_db.field_for("series_index", book_id)
        assert isinstance(series_index, float)

        output.add(
            Book(
                identifier=book_id,
                title=title,
                series=series,
                series_index=series_index,
            )
        )
    return output


def evaluate(book: CalibreBook, context: CalibreContext) -> str:
    if not context.arguments[0]:
        return ""
    if book.series is None:
        return ""
    number = Decimal(context.arguments[0])
    calibre_db = context.db.new_api
    books = get_books_in_series(calibre_db, book.series)
    zero_padding = max({count_whole_digits(book.series_index) for book in books})
    decimal_places = max({count_decimal_places(book.series_index) for book in books})
    return print_result(number, zero_padding, decimal_places)
