from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


@cache_page(20)
def index(request):
    posts = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all().order_by('-pub_date')[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'posts': posts,
                                          'page': page,
                                          'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = profile.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = profile.following.all()
    follows = profile.follower.count()
    followers = profile.following.count()
    context = {'page': page,
               'paginator': paginator,
               'post': posts,
               'profile': profile,
               'followers': followers,
               'following': following,
               'follows': follows,
               }
    return render(request, 'includes/profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    name = post.author
    if username != name.username:
        return redirect('post', username=name.username, post_id=post_id)
    comments = post.comments.all().order_by('-created')
    form = CommentForm()

    return render(request, "post.html", {"post": post,
                                         "profile": name,
                                         "comments": comments,
                                         "form": form})


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    name = post.author
    if request.user != post.author:
        return redirect('post', username=name, post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=name, post_id=post_id)
    context = {'post': post,
               'profile': name,
               'form': form,
               }
    return render(request, 'new.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'includes/comments.html',
                      {'form': form,
                       'author': author,
                       'post': post})
    form.instance.author = request.user
    form.instance.post = post
    form.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if not follow and author != request.user:
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username)



@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if follow:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
