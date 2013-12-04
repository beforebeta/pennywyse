from haystack.query import SearchQuerySet
from haystack.backends.solr_backend import SolrSearchQuery, SolrEngine

class FuzzySearchQuerySet(SearchQuerySet):
    """Custom queryset for performing fuzzy search."""
    
    def combined_filter(self, *args, **kwargs):
        """Simple filter method, which joins direct match query and fuzzy search query."""
        
        content = kwargs.get('content', None)
        results = self.filter_or(*args, **kwargs)
        if content:
            kwargs['content'] = content + '~'
            results = results.filter_or(*args, **kwargs)
        return results

class FuzzySolrSearchQuery(SolrSearchQuery):
    
    def clean(self, query_fragment):
        # removing tilde from forbidden characters for making fuzzy search queries
        if query_fragment.endswith('~') and '~' in self.backend.RESERVED_CHARACTERS:
            reserved_characters = list(self.backend.RESERVED_CHARACTERS)
            reserved_characters.remove('~')
            self.backend.RESERVED_CHARACTERS = reserved_characters
        return super(FuzzySolrSearchQuery, self).clean(query_fragment)


class CustomSolrEngine(SolrEngine):
    query = FuzzySolrSearchQuery