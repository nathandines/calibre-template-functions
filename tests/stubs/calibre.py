from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Book:
    title: str
    series: Optional[str] = None
    series_index: float = 1.0


@dataclass
class DbApi:
    search_result: List[Book]

    def search(self, query: str) -> List[int]:
        return [i for i, _book in enumerate(self.search_result)]

    def field_for(
        self, field_name: str, book_id: int, default_return: Optional[str] = None
    ) -> Optional[str]:
        return_val: Optional[str] = getattr(self.search_result[book_id], field_name)
        if return_val:
            return return_val
        return default_return


@dataclass
class Db:
    new_api: DbApi


@dataclass
class Context:
    calibre_db: DbApi
    arguments: List[str] = field(default_factory=lambda: [""])

    @property
    def db(self) -> Db:
        return Db(new_api=self.calibre_db)
