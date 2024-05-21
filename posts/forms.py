from django.forms import Form, CharField

from posts.models import PostComment
from django_ckeditor_5.forms import CKEditor5Widget


class CreatePostCommentForm(Form()):
    text = CKEditor5Widget()

    class Meta:
        model = PostComment
        fields = (
            'text',
        )