from dataclasses import dataclass

from starlette.datastructures import URL


@dataclass(slots=True)
class OffsetPagination:
    limit: int
    offset: int
    request_url: URL | None = None

    @property
    def is_first_page(self) -> bool:
        return self.offset == 0

    @property
    def is_cursor_pagination(self) -> bool:
        return False

    @property
    def is_offset_pagination(self) -> bool:
        return True

    def _get_page_uri(self, offset: int | None) -> str | None:
        if offset is None or offset < 0 or self.request_url is None:
            return None
        url = self.request_url.remove_query_params("offset")
        url = url.include_query_params(**{"offset": offset})  # noqa: PIE804
        page_uri = url.path + "?" + url.query
        return page_uri  # noqa: RET504

    def build_pages(self, next_offset: int | None) -> tuple[str | None, str | None]:
        next_page = self._get_page_uri(next_offset)
        previous_offset = self.offset - self.limit
        previous_page = self._get_page_uri(previous_offset)
        return previous_page, next_page
