from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Set, SupportsRound, Union


class CalibreDbApi(ABC):
    @abstractmethod
    def search(self, query: str) -> List[int]:
        pass

    @abstractmethod
    def field_for(
        self, field_name: str, book_id: int, default_return: Optional[str] = None
    ) -> Union[str, int, float, None]:
        pass


class CalibreDb(ABC):
    new_api: CalibreDbApi


class CalibreContext(ABC):
    arguments: List[str]

    @property
    @abstractmethod
    def db(self) -> CalibreDb:
        ...


class CalibreBook(ABC):
    series: Optional[str]
    series_index: str


@dataclass
class Book:
    identifier: int
    title: str
    series: Optional[str] = None
    series_index: Optional[Decimal] = None

    def __hash__(self) -> int:
        return self.identifier


def print_result(number: Decimal, zero_padding: int, decimal_places: int) -> str:
    """Print result. Integers should not show any decimal places."""
    if number % 1 == 0:
        return "{:0>{zero_padding}d}".format(int(number), zero_padding=zero_padding)
    return "{:0>{zero_padding}.{decimal_places}f}".format(
        float(number),
        zero_padding=zero_padding + decimal_places + 1,
        decimal_places=decimal_places,
    )


def count_decimal_places(number: SupportsRound[Decimal]) -> int:
    """Count decimal places to a max of two places"""
    return abs(int(round(number, 2).normalize().as_tuple().exponent))


def count_whole_digits(number: Decimal) -> int:
    """Count whole digits. Minimum of one place returned, even for zero values."""
    num_tuple = number.normalize().as_tuple()
    exponent = int(num_tuple.exponent)
    digits = num_tuple.digits if exponent == 0 else num_tuple.digits[:exponent]
    return max(1, len(digits))


def get_books_in_series(calibre_db: CalibreDbApi, series_name: str) -> Set[Book]:
    book_ids = calibre_db.search(f'series:"={series_name}"')
    output = set()
    for book_id in book_ids:
        series_index = calibre_db.field_for("series_index", book_id, "")
        output.add(
            Book(
                identifier=book_id,
                title=str(calibre_db.field_for("title", book_id, "")),
                series=str(calibre_db.field_for("series", book_id, "")) or None,
                series_index=Decimal(series_index) if series_index else None,
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
    books: Set[Book] = get_books_in_series(calibre_db, book.series)
    zero_padding = max(
        {
            count_whole_digits(book.series_index) if book.series_index else 0
            for book in books
        }
    )
    decimal_places = max(
        {
            count_decimal_places(book.series_index) if book.series_index else 0
            for book in books
        }
    )
    return print_result(number, zero_padding, decimal_places)
