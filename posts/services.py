from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, \
    SearchHeadline, TrigramSimilarity
from django.db.models import Model, Q

from posts.models import Post, PostPublishedManager
from uuid import uuid1
import os

start_sel = '<span style="background-color: yellow;">'
stop_sel = '</span>'


def get_image_path(instance: Model, filename):
    result = os.path.join('images', str(instance.pk), uuid1().hex)
    if '.' in filename:
        result = os.path.join(result, filename.split('.')[-1])
    return result


def add_search_headlines(query: str, results):
    results = results.annotate(
        headline=SearchHeadline(
            'title',
            query,
            start_sel=start_sel,
            stop_sel=stop_sel,
        ))
    results = results.annotate(
        bodyline=SearchHeadline(
            'content',
            query,
            start_sel=start_sel,
            stop_sel=stop_sel,
        ))
    return results


def post_search(query: str) -> PostPublishedManager:
    """
    Повнотекстовий пошук
    """
    search_vector = SearchVector('title', weight='A') + \
        SearchVector('content', weight='B')
    search_query = SearchQuery(query)

    results = (Post.published
               .annotate(
                   search=search_vector,
                   rank=SearchRank(search_vector, search_query))
               .filter(rank__gte=0.3)
               .order_by('-rank')
               )
    return add_search_headlines(query, results)


def post_trigram_search(query: str) -> PostPublishedManager:
    """
    Trigram пошук
    """
    results = (Post.published
               .annotate(similarity_title=TrigramSimilarity('title', query),
                         similarity_content=TrigramSimilarity('content', query))
               .filter(Q(similarity_title__gt=0.05) | Q(similarity_content__gt=0.05))
               .order_by('-similarity_title', '-similarity_content'))

    results = results.annotate(
        headline=SearchHeadline(
            'title',
            query,
            start_sel=start_sel,
            stop_sel=stop_sel,
        ))
    results = results.annotate(
        bodyline=SearchHeadline(
            'content',
            query,
            start_sel=start_sel,
            stop_sel=stop_sel,
        ))
    return add_search_headlines(query, results)
