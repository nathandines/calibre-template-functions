from dataclasses import dataclass
from types import SimpleNamespace


@dataclass
class Book:
    title: str
    series: str | None = None
    series_index: int | float | str = ""


@dataclass
class DB:
    search_result: list[Book]

    def search(self, *args, **kwargs):
        return [i for i, _book in enumerate(self.search_result)]

    def field_for(
        self, field_name: str, book_id: int, default_return: str | None = None
    ):
        return_val = getattr(self.search_result[book_id], field_name)
        if return_val:
            return str(return_val)
        return default_return


class Context:
    def __init__(self, calibre_db: DB, arguments: list[str] | None = None):
        self.db = SimpleNamespace(new_api=calibre_db)
        self.arguments = arguments or [""]
