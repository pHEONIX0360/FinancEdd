# forms.py
from django import forms
from django import forms
# from .models import Post, Comment

class QueryForm(forms.Form):
    query = forms.CharField(label='Your query', max_length=100)


# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = ['content']  # replace 'content' with the actual fields of your Post model

# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['content']  # replace 'content' with the actual fields of your Comment model    