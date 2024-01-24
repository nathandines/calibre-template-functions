from dataclasses import dataclass
from typing import List, Optional, Union

from calibre_template_functions.zero_pad_series import (
    CalibreBook,
    CalibreContext,
    CalibreDb,
    CalibreDbApi,
)


class Book(CalibreBook):
    title: str
    _series: Optional[str]
    _series_index: str

    def __init__(
        self,
        title: str,
        series: Optional[str] = None,
        series_index: str = "",
    ) -> None:
        self.title = title
        self._series = series
        self._series_index = series_index

    @property
    def series(self) -> Optional[str]:
        return self._series

    @property
    def series_index(self) -> str:
        return self._series_index


@dataclass
class DbApi(CalibreDbApi):
    search_result: List[Book]

    def search(self, _query: str) -> List[int]:
        return [i for i, _book in enumerate(self.search_result)]

    def field_for(
        self, field_name: str, book_id: int, default_return: Optional[str] = None
    ) -> Union[str, int, float, None]:
        return_val = getattr(self.search_result[book_id], field_name)
        if return_val:
            return str(return_val)
        return default_return


@dataclass
class Db(CalibreDb):
    db_api: DbApi

    @property
    def new_api(self) -> DbApi:
        return self.db_api


class Context(CalibreContext):
    calibre_db: DbApi
    _arguments: List[str]

    def __init__(
        self, calibre_db: DbApi, arguments: Optional[List[str]] = None
    ) -> None:
        self.calibre_db = calibre_db
        self._arguments = arguments or [""]

    @property
    def db(self) -> Db:
        return Db(db_api=self.calibre_db)

    @property
    def arguments(self) -> List[str]:
        return self._arguments
