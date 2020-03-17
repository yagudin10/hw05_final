from django.forms import ModelForm
from .models import Post, Comment, Follow


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        required = {'group': False, 'text': True,}
        labels = {'group': 'Группа', 'text': 'Текст', 'image': 'Изображение'}


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
