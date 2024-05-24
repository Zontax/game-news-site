from django.forms import Form, CharField, ValidationError

from django_ckeditor_5.widgets import CKEditor5Widget


class CreatePostCommentForm(Form):        
    text = CharField(required=True, widget=CKEditor5Widget(
        attrs={'class': 'django_ckeditor_5 comment-editor'}, 
        config_name='comments'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].required = False
    
    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise ValidationError('Коментар не може бути пустим')
        return data
