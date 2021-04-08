from django import forms
from django.forms.widgets import Textarea
from django.utils.translation import gettext_lazy as _

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text')
        labels = {
            "text": _("Напишите о чем ваш пост"),
            "group": _("Выбeрите группу из списка"),
        }
        widget = {
            "text": Textarea(
                attrs={
                    'placeholder': 'Введите текст'
                }
            )
        }
