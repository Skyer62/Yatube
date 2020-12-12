from django.forms import ModelForm
from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["group", "text", "image"]
        help_texts = {"group": "Название существующей группы",
                      "text": "Не более 200 символов"}



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        help_texts = {"text": "Комментарий"}
