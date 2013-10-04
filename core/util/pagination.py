import string

# number of pages in one row of pagination
ROW_LIMIT = 12

# number of pages for both sides near active page
# current value keeps active page in the middle of the pagination row
SIDE_LIMIT = round(ROW_LIMIT/2, 0) - 1

class AlphabeticalPagination(object):
    """
    Basic implementation of alphabetical pagination.
    Calculates pages beyond row limit that can be displayed for back and forth navigation.
    """
    
    all_pages = list(string.uppercase)
    
    def __init__(self, page):
        self.page = page
    
    @property
    def page_index(self):
        return self.all_pages.index(self.page)
    
    @property
    def start(self):
        if self.page_index - SIDE_LIMIT < 0:
            start = 0
        else:
            start = self.page_index - SIDE_LIMIT
        return int(start)

    @property
    def end(self):
        if self.start + ROW_LIMIT > len(self.all_pages):
            end = len(pages)
        else:
            end = self.start + ROW_LIMIT
        return int(end)
    
    @property
    def pages(self):
        return self.all_pages[self.start:self.end]
    
    @property
    def previous_page(self):
        previous_index = self.all_pages.index(self.page) - 1
        try:
            return self.all_pages[previous_index]
        except:
            return
    
    @property
    def next_page(self):
        next_index = self.all_pages.index(self.page) + 1
        try:
            return self.all_pages[next_index]
        except:
            return
    
    @property
    def previous_pages(self):
        """Pages beyond row limit, can be displayed to navigate back from active page."""
        
        if self.start > 0:
            return self.all_pages[0:self.start]
        return
    
    @property
    def next_pages(self):
        """Pages beyond row limit, can be displayed to navigate forward from active page."""
        
        if len(self.all_pages) - self.end > 0:
            return self.all_pages[self.end:]
        return