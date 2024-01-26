from dataclasses import dataclass
from typing import List, Set

from calibre_template_functions.zero_pad_series import (
    Book,
    count_decimal_places,
    count_whole_digits,
    evaluate,
    get_books_in_series,
    print_result,
)

from .stubs.calibre import Book as CalibreBook
from .stubs.calibre import Context as CalibreContext
from .stubs.calibre import DbApi as CalibreDB


@dataclass
class NumberTestData:
    dec: float
    expected_dec_places: int
    expected_whole_digits: int


@dataclass
class BookLookupTestData:
    series_name: str
    db_result: List[CalibreBook]
    expected_output: Set[Book]


@dataclass
class EvaluateTestData:
    book: CalibreBook
    search_results: List[CalibreBook]
    expected_result: str


number_input_list: List[NumberTestData] = [
    NumberTestData(dec=123.0, expected_whole_digits=3, expected_dec_places=0),
    NumberTestData(dec=0.0000, expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=0.70, expected_whole_digits=1, expected_dec_places=1),
    NumberTestData(dec=0.699, expected_whole_digits=1, expected_dec_places=1),
    NumberTestData(dec=0.69, expected_whole_digits=1, expected_dec_places=2),
    NumberTestData(dec=0.123000, expected_whole_digits=1, expected_dec_places=2),
    NumberTestData(dec=1.123000, expected_whole_digits=1, expected_dec_places=2),
    NumberTestData(dec=142.123000, expected_whole_digits=3, expected_dec_places=2),
    NumberTestData(dec=142.123, expected_whole_digits=3, expected_dec_places=2),
    NumberTestData(dec=142.0123, expected_whole_digits=3, expected_dec_places=2),
    NumberTestData(dec=142.0, expected_whole_digits=3, expected_dec_places=0),
    NumberTestData(dec=0.0, expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=000.0, expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=001.0, expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=7.0, expected_whole_digits=1, expected_dec_places=0),
    NumberTestData(dec=27.0, expected_whole_digits=2, expected_dec_places=0),
]


class TestZeroPadSeries:
    def test_count_decimal_places(self) -> None:
        for number in number_input_list:
            assert count_decimal_places(number.dec) == number.expected_dec_places

    def test_count_whole_digits(self) -> None:
        for number in number_input_list:
            assert count_whole_digits(number.dec) == number.expected_whole_digits

    def test_print_result(self) -> None:
        assert print_result(1.0, 2, 2) == "01"
        assert print_result(1.0, 1, 2) == "1"
        assert print_result(14.0, 0, 2) == "14"
        assert print_result(1.1234, 2, 2) == "01.12"
        assert print_result(14.1234, 2, 2) == "14.12"
        assert print_result(123.1234, 2, 2) == "123.12"
        assert print_result(1.1264, 2, 2) == "01.13"
        assert print_result(1.1264, 2, 4) == "01.1264"
        assert print_result(1.1264, 0, 4) == "1.1264"
        assert print_result(1.1264, 1, 4) == "1.1264"
        assert print_result(1.12, 1, 4) == "1.1200"

    def test_get_books_in_series(self) -> None:
        assertions: List[BookLookupTestData] = [
            BookLookupTestData(
                series_name="Harry Potter",
                db_result=[
                    CalibreBook(
                        title="Harry Potter and the Philosopher's Stone",
                        series="Harry Potter",
                        series_index=1.0,
                    ),
                    CalibreBook(
                        title="Harry Potter and the Chamber of Secrets",
                        series="Harry Potter",
                        series_index=2.0,
                    ),
                ],
                expected_output={
                    Book(
                        identifier=0,
                        title="Harry Potter and the Philosopher's Stone",
                        series="Harry Potter",
                        series_index=1.0,
                    ),
                    Book(
                        identifier=1,
                        title="Harry Potter and the Chamber of Secrets",
                        series="Harry Potter",
                        series_index=2.0,
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
                        series_index=4.0,
                    ),
                ],
                expected_output={
                    Book(
                        identifier=0,
                        title="Sword of Destiny",
                        series="The Witcher",
                        series_index=0.6999999,
                    ),
                    Book(
                        identifier=1,
                        title="The Tower of the Swallow",
                        series="The Witcher",
                        series_index=4.0,
                    ),
                },
            ),
            BookLookupTestData(
                series_name="The Wheel of Time",
                db_result=[
                    CalibreBook(
                        title="Eye of the World",
                        series="The Wheel of Time",
                        series_index=1.0,
                    ),
                    CalibreBook(
                        title="A Memory of Light",
                        series="The Wheel of Time",
                        series_index=14.0,
                    ),
                ],
                expected_output={
                    Book(
                        identifier=0,
                        title="Eye of the World",
                        series="The Wheel of Time",
                        series_index=1.0,
                    ),
                    Book(
                        identifier=1,
                        title="A Memory of Light",
                        series="The Wheel of Time",
                        series_index=14.0,
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

    def test_evaluate(self) -> None:
        assertions: List[EvaluateTestData] = [
            EvaluateTestData(
                book=CalibreBook(title="The Count of Monte Cristo"),
                search_results=[CalibreBook(title="The Count of Monte Cristo")],
                expected_result="",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="Eye of the World",
                    series="The Wheel of Time",
                    series_index=1.0,
                ),
                search_results=[
                    CalibreBook(
                        title="Eye of the World",
                        series="The Wheel of Time",
                        series_index=1.0,
                    ),
                    CalibreBook(
                        title="A Memory of Light",
                        series="The Wheel of Time",
                        series_index=14.0,
                    ),
                ],
                expected_result="01",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="A Memory of Light",
                    series="The Wheel of Time",
                    series_index=14.0,
                ),
                search_results=[
                    CalibreBook(
                        title="Eye of the World",
                        series="The Wheel of Time",
                        series_index=1.0,
                    ),
                    CalibreBook(
                        title="A Memory of Light",
                        series="The Wheel of Time",
                        series_index=14.0,
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
                        series_index=4.0,
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
                        series_index=328.0,
                    ),
                ],
                expected_result="000.75",
            ),
            EvaluateTestData(
                book=CalibreBook(
                    title="The Seeds of Regret",
                    series="The Pumpkin Chronicles",
                    series_index=328.0,
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
                        series_index=328.0,
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
                        arguments=[str(assertion.book.series_index) or ""],
                        calibre_db=CalibreDB(search_result=assertion.search_results),
                    ),
                )
                == assertion.expected_result
            )

    def test_evaluate_without_arguments(self) -> None:
        assert (
            evaluate(
                book=CalibreBook(
                    title="Eye of the World",
                    series="The Wheel of Time",
                    series_index=1.0,
                ),
                context=CalibreContext(
                    calibre_db=CalibreDB(
                        search_result=[
                            CalibreBook(
                                title="Eye of the World",
                                series="The Wheel of Time",
                                series_index=1.0,
                            ),
                            CalibreBook(
                                title="A Memory of Light",
                                series="The Wheel of Time",
                                series_index=14.0,
                            ),
                        ]
                    )
                ),
            )
            == ""
        )

    def test_evaluate_without_series(self) -> None:
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
