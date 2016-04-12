from math import ceil

from flask import request


MATCHES_PAGINATION_WINDOW_SIZE = 25


class Paginated(object):
    def __init__(self, query, step=MATCHES_PAGINATION_WINDOW_SIZE):
        self.current_page = self.get_current_page()
        self.step = step

        self.total_item_count = query.count()
        self.items = query.limit(step).offset((self.current_page - 1) * step)

    @property
    def is_first_page(self):
        return self.current_page <= 1

    @property
    def is_last_page(self):
        return self.current_page >= self.total_pages

    @property
    def total_pages(self):
        return int(ceil(self.total_item_count / float(self.step)))

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for page in range(1, self.total_pages + 1):
            if page <= left_edge or \
               (page > self.current_page - left_current - 1 and page < self.current_page + right_current) or \
               page > self.total_pages - right_edge:
                if last + 1 != page:
                    yield None
                yield page
                last = page

    @staticmethod
    def get_current_page():
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        return page

    def calculate_slice_range(self):
        return self.step*(self.current_page - 1), self.step * self.current_page


def paginate(query, step=MATCHES_PAGINATION_WINDOW_SIZE):
    return Paginated(query, step)
