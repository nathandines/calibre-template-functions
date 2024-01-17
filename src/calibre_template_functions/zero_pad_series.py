from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Book:
    identifier: int
    title: str
    series: str | None
    series_index: Decimal | None

    def __hash__(self):
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


def count_decimal_places(number: Decimal) -> int:
    """Count decimal places to a max of two places"""
    return abs(round(number, 2).normalize().as_tuple().exponent)


def count_whole_digits(number: Decimal) -> int:
    """Count whole digits. Minimum of one place returned, even for zero values."""
    num_tuple = number.normalize().as_tuple()
    digits = (
        num_tuple.digits
        if num_tuple.exponent == 0
        else num_tuple.digits[: num_tuple.exponent]
    )
    return max(1, len(digits))


def get_books_in_series(calibre_db, series_name: str) -> set[Book]:
    book_ids = calibre_db.search(f'series:"={series_name}"', "")
    output = set()
    for book_id in book_ids:
        series_index = calibre_db.field_for("series_index", book_id, "")
        output.add(
            Book(
                identifier=book_id,
                title=calibre_db.field_for("title", book_id, ""),
                series=calibre_db.field_for("series", book_id, "") or None,
                series_index=Decimal(series_index) if series_index else None,
            )
        )
    return output


def evaluate(book, context):
    if not context.arguments[0]:
        return ""
    if book.series is None:
        return ""
    number = Decimal(context.arguments[0])
    calibre_db = context.db.new_api
    books: set[Book] = get_books_in_series(calibre_db, book.series)
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
