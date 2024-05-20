from django.utils.html import format_html
from django.contrib import admin

from posts.models import PostType, PostTag, PostTopic, Post, PostComment


@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'color', 'name_plural', 'slug']
    list_editable = ['slug', 'color']


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug', 'description']


@admin.register(PostTopic)
class PostTopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug', 'description']


# class PostForm(ModelForm):
#     content = CharField(widget=CKEditorWidget())

#     class Meta:
#         model = Post
#         fields = '__all__'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'display_image', 'type', 'is_publicated']
    list_editable = ['type', 'is_publicated']
    search_fields = ['title', 'content', 'slug', 'meta_description']
    list_filter = ['type', 'is_publicated', 'is_edited']
    filter_horizontal = ('topics', 'tags')
    # form = PostForm
    list_display_links = ['title']
    fields = [
        ('user', 'type'),
        ('title', 'slug'),
        'content',
        'meta_description',
        ('image', 'detail_image'),
        'topics',
        'tags',
        'is_publicated',
    ]

    def display_image(self, obj: Post):
        if obj.image and obj.image.url:
            return format_html(
                f'''
                <a href="{obj.get_absolute_url()}" 
                    title="Дивитися на сайті">
                    <img src="{obj.image.url}" width="50" height="50" />
                </a>''')
        return None

    display_image.short_description = 'Icon'


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'post', 'is_edited', 'created_date']
    list_filter = ['post', 'parent']
    search_fields = ['text']
