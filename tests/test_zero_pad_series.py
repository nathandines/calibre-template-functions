from dataclasses import dataclass
from decimal import Decimal

from calibre_template_functions.zero_pad_series import (
    Book,
    count_decimal_places,
    count_whole_digits,
    evaluate,
    get_books_in_series,
    print_result,
)

from .stubs.calibre import DB as CalibreDB
from .stubs.calibre import Book as CalibreBook
from .stubs.calibre import Context as CalibreContext


@dataclass
class NumberTestData:
    dec: Decimal
    expected_dec_places: int
    expected_whole_digits: int


@dataclass
class BookLookupTestData:
    series_name: str
    db_result: list[CalibreBook]
    expected_output: set[Book]


@dataclass
class EvaluateTestData:
    book: CalibreBook
    search_results: list[CalibreBook]
    expected_result: str


number_input_list: list[NumberTestData] = [
    NumberTestData(dec=Decimal("123"), expected_whole_digits=3, expected_dec_places=0),
    NumberTestData(
        dec=Decimal("0.0000"), expected_whole_digits=1, expected_dec_places=0
    ),
    NumberTestData(dec=Decimal("0.70"), expected_whole_digits=1, expected_dec_places=1),
    NumberTestData(
        dec=Decimal("0.699"), expected_whole_digits=1, expected_dec_places=1
    ),
    NumberTestData(dec=Decimal("0.69"), expected_whole_digits=1, expected_dec_places=2),
    NumberTestData(
        dec=Decimal("0.123000"), expected_whole_digits=1, expected_dec_places=2
    ),
    NumberTestData(
        dec=Decimal("1.123000"), expected_whole_digits=1, expected_dec_places=2
    ),
    NumberTestData(
        dec=Decimal("142.123000"), expected_whole_digits=3, expected_dec_places=2
    ),
    NumberTestData(
        dec=Decimal("142.123"), expected_whole_digits=3, expected_dec_places=2
    ),
    NumberTestData(
        dec=Decimal("142.0123"), expected_whole_digits=3, expected_dec_places=2
    ),
    NumberTestData(dec=Decimal("142"), expected_whole_digits=3, expected_dec_places=0),
    NumberTestData(dec=Decimal("0"), expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=Decimal("000"), expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=Decimal("001"), expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=Decimal("7"), expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=Decimal("27"), expected_whole_digits=2, expected_dec_places=0),
]


class TestZeroPadSeries:
    def test_count_decimal_places(self):
        for number in number_input_list:
            assert count_decimal_places(number.dec) == number.expected_dec_places

    def test_count_whole_digits(self):
        for number in number_input_list:
            assert count_whole_digits(number.dec) == number.expected_whole_digits

    def test_print_result(self):
        assert print_result(Decimal("1"), 2, 2) == "01"
        assert print_result(Decimal("1"), 1, 2) == "1"
        assert print_result(Decimal("14"), 0, 2) == "14"
        assert print_result(Decimal("1.1234"), 2, 2) == "01.12"
        assert print_result(Decimal("14.1234"), 2, 2) == "14.12"
        assert print_result(Decimal("123.1234"), 2, 2) == "123.12"
        assert print_result(Decimal("1.1264"), 2, 2) == "01.13"
        assert print_result(Decimal("1.1264"), 2, 4) == "01.1264"
        assert print_result(Decimal("1.1264"), 0, 4) == "1.1264"
        assert print_result(Decimal("1.1264"), 1, 4) == "1.1264"
        assert print_result(Decimal("1.12"), 1, 4) == "1.1200"

    def test_get_books_in_series(self):
        assertions: list[BookLookupTestData] = [
            BookLookupTestData(
                series_name="Harry Potter",
                db_result=[
                    CalibreBook(
                        title="Harry Potter and the Philosopher's Stone",
                        series="Harry Potter",
                        series_index=1,
                    ),
                    CalibreBook(
                        title="Harry Potter and the Chamber of Secrets",
                        series="Harry Potter",
                        series_index=2,
                    ),
                ],
                expected_output={
                    Book(
                        identifier=0,
                        title="Harry Potter and the Philosopher's Stone",
                        series="Harry Potter",
                        series_index=Decimal("1"),
                    ),
                    Book(
                        identifier=1,
                        title="Harry Potter and the Chamber of Secrets",
                        series="Harry Potter",
                        series_index=Decimal("2"),
                    ),
                },
            ),
            BookLookupTestData(
                series_name="The Witcher",
                db_result=[
                    # For "Sword of Destiny", this is how the value 0.7 was presented in my live instance
                    CalibreBook(
                        title="Sword of Destiny",
                        series="The Witcher",
                        series_index=0.6999999,
                    ),
                    CalibreBook(
                        title="The Tower of the Swallow",
                        series="The Witcher",
                        series_index=4,
                    ),
                ],
                expected_output={
                    Book(
                        identifier=0,
                        title="Sword of Destiny",
                        series="The Witcher",
                        series_index=Decimal("0.6999999"),
                    ),
                    Book(
                        identifier=1,
                        title="The Tower of the Swallow",
                        series="The Witcher",
                        series_index=Decimal("4"),
                    ),
                },
            ),
            BookLookupTestData(
                series_name="The Wheel of Time",
                db_result=[
                    CalibreBook(
                        title="Eye of the World",
                        series="The Wheel of Time",
                        series_index=1,
                    ),
                    CalibreBook(
                        title="A Memory of Light",
                        series="The Wheel of Time",
                        series_index=14,
                    ),
                ],
                expected_output={
                    Book(
                        identifier=0,
                        title="Eye of the World",
                        series="The Wheel of Time",
                        series_index=Decimal("1"),
                    ),
                    Book(
                        identifier=1,
                        title="A Memory of Light",
                        series="The Wheel of Time",
                        series_index=Decimal("14"),
                    ),
                },
            ),
        ]
        for assertion in assertions:
            assert (
                get_books_in_series(
                    calibre_db=CalibreDB(search_result=assertion.db_result),
                    series_name=assertion.series_name,
                )
                == assertion.expected_output
            )

    def test_evaluate(self):
        assertions: list[EvaluateTestData] = [
            EvaluateTestData(
                book=CalibreBook(title="The Count of Monte Cristo"),
                search_results=[CalibreBook(title="The Count of Monte Cristo")],
                expected_result="",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="Eye of the World", series="The Wheel of Time", series_index=1
                ),
                search_results=[
                    CalibreBook(
                        title="Eye of the World",
                        series="The Wheel of Time",
                        series_index=1,
                    ),
                    CalibreBook(
                        title="A Memory of Light",
                        series="The Wheel of Time",
                        series_index=14,
                    ),
                ],
                expected_result="01",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="A Memory of Light",
                    series="The Wheel of Time",
                    series_index=14,
                ),
                search_results=[
                    CalibreBook(
                        title="Eye of the World",
                        series="The Wheel of Time",
                        series_index=1,
                    ),
                    CalibreBook(
                        title="A Memory of Light",
                        series="The Wheel of Time",
                        series_index=14,
                    ),
                ],
                expected_result="14",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="Sword of Destiny",
                    series="The Witcher",
                    series_index=0.6999999999,
                ),
                search_results=[
                    CalibreBook(
                        title="Sword of Destiny",
                        series="The Witcher",
                        series_index=0.6999999999,
                    ),
                    CalibreBook(
                        title="The Tower of the Swallow",
                        series="The Witcher",
                        series_index=4,
                    ),
                ],
                expected_result="0.7",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="The Pumpkin of Destiny",
                    series="The Pumpkin Chronicles",
                    series_index=0.75,
                ),
                search_results=[
                    CalibreBook(
                        title="The Pumpkin of Destiny",
                        series="The Pumpkin Chronicles",
                        series_index=0.75,
                    ),
                    CalibreBook(
                        title="The Seeds of Regret",
                        series="The Pumpkin Chronicles",
                        series_index=328,
                    ),
                ],
                expected_result="000.75",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="The Seeds of Regret",
                    series="The Pumpkin Chronicles",
                    series_index=328,
                ),
                search_results=[
                    CalibreBook(
                        title="The Pumpkin of Destiny",
                        series="The Pumpkin Chronicles",
                        series_index=0.75,
                    ),
                    CalibreBook(
                        title="The Seeds of Regret",
                        series="The Pumpkin Chronicles",
                        series_index=328,
                    ),
                ],
                expected_result="328",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="The Pumpkin of Destiny",
                    series="The Pumpkin Chronicles",
                    series_index=0.254,
                ),
                search_results=[
                    CalibreBook(
                        title="The Pumpkin of Destiny",
                        series="The Pumpkin Chronicles",
                        series_index=0.254,
                    ),
                ],
                expected_result="0.25",
            ),
        ]

        for assertion in assertions:
            assert (
                evaluate(
                    book=assertion.book,
                    context=CalibreContext(
                        arguments=[assertion.book.series_index or ""],
                        calibre_db=CalibreDB(search_result=assertion.search_results),
                    ),
                )
                == assertion.expected_result
            )

    def test_evaluate_without_arguments(self):
        assert (
            evaluate(
                book=CalibreBook(
                    title="Eye of the World",
                    series="The Wheel of Time",
                    series_index=1,
                ),
                context=CalibreContext(
                    calibre_db=CalibreDB(
                        search_result=[
                            CalibreBook(
                                title="Eye of the World",
                                series="The Wheel of Time",
                                series_index=1,
                            ),
                            CalibreBook(
                                title="A Memory of Light",
                                series="The Wheel of Time",
                                series_index=14,
                            ),
                        ]
                    )
                ),
            )
            == ""
        )

    def test_evaluate_without_series(self):
        assert (
            evaluate(
                book=CalibreBook(title="The Count of Monte Cristo"),
                context=CalibreContext(
                    arguments=["this doesn't belong here, but exists for testing"],
                    calibre_db=CalibreDB(
                        search_result=[
                            CalibreBook(title="The Count of Monte Cristo"),
                        ]
                    ),
                ),
            )
            == ""
        )
