from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import User, Group, Post


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'new_post.html', {
            'form': form,
            'edit': False
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    paginator = Paginator(author_posts, 3)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html',
                  {'author': author,
                   'page': page,})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post.html',
                  {'author': author,
                   'post': post})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('post', username, post_id)
    form = PostForm(
        request.POST or None,
        instance=post
    )
    if not form.is_valid():
        return render(
            request,
            'new_post.html',
            {
                'form': form,
                'post': post,
                'edit': True
            }
        )
    edited_post = form.save(commit=False)
    edited_post.author = request.user
    edited_post.save()
    return redirect('post', username, post_id)
