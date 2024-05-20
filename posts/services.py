from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, SearchHeadline
from django.db.models import Model, Q

from posts.models import Post
from functools import reduce
from operator import and_
from uuid import uuid1
import os

start_sel = '<span style="background-color: yellow;">'
stop_sel = '</span>'


def get_image_path(instance: Model, filename):
    result = os.path.join('images', str(instance.pk), uuid1().hex)
    if '.' in filename:
        result = os.path.join(result, filename.split('.')[-1])
    return result


def q_search(query):
    """
    Пошук (від postgre)
    """
    if isinstance(query, str):
        vector = SearchVector('title')
        query = SearchQuery(query)

        result = (
            Post.objects
                .annotate(rank=SearchRank(vector, query))
                .filter(rank__gt=0)
                .order_by('-rank')
        )
        result = result.annotate(
            headline=SearchHeadline(
                'title',
                query,
                start_sel=start_sel,
                stop_sel=stop_sel,
            ))
        result = result.annotate(
            bodyline=SearchHeadline(
                'content',
                query,
                start_sel=start_sel,
                stop_sel=stop_sel,
            ))
        return result
