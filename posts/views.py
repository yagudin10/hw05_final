from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import datetime
from django.core.paginator import Paginator
from .models import Post, User, Group, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page


@cache_page(20)
def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    follow = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user).count:
            follow = True
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator, 'follow': follow})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(posts, 10)
    # переменная в URL с номером запрошенной страницы
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


def year(request):
    year = datetime.datetime.now().year
    return render(request, 'footer.html', {'year': year})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)

        if form.is_valid():
            group = form.cleaned_data['group']
            text = form.cleaned_data['text']
            image = request.FILES.get('image')
            Post.objects.create(
                text=text, author=request.user, group=group, image=image)
            return redirect('index')

        return render(request, 'new_post.html', {'form': form, 'title': 'Добавить запись',
                                                 'button': 'Добавить'})

    form = PostForm()

    return render(request, 'new_post.html', {'form': form, 'title': 'Добавить запись',
                                             'button': 'Добавить'})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=author).count():
            following = True
    post_list = Post.objects.filter(author=author).order_by("-pub_date").all()
    cnt_post = post_list.count()
    followings = Follow.objects.filter(author=author).count()
    follower = Follow.objects.filter(user=author).count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "profile.html", {"author": author, 'page': page, 'paginator': paginator,
                                            'following': following, 'cnt_post': cnt_post,
                                            'followings': followings, 'follower': follower})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    cnt = Post.objects.filter(author=author).count()
    followings = Follow.objects.filter(author=author).count()
    follower = Follow.objects.filter(user=author).count()
    post = Post.objects.get(author=author, id=post_id)
    form = CommentForm()
    items = Comment.objects.filter(post=post_id)
    return render(request, "post.html", {"form": form, "author": author, "post": post, "cnt": cnt,
                                         'items': items, 'followings': followings, 'follower': follower})


def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':

        if form.is_valid():
            post.group = form.cleaned_data['group']
            post.text = form.cleaned_data['text']
            post.image = request.FILES['image']
            post.save()
            return redirect('post', username=username, post_id=post_id)

        return render(request, 'new_post.html', {'form': form, 'post': post, 'title': 'Редактировать запись', 'button': 'Сохранить'})

    return render(request, "new_post.html",  {'form': form, 'post': post, 'title': 'Редактировать запись', 'button': 'Сохранить'})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            text = form.cleaned_data['text']
            Comment.objects.create(text=text, author=request.user, post=post)

            return redirect('post', username=post.author.username, post_id=post_id)

        return redirect('post', username=post.author.username, post_id=post_id)
    form = CommentForm()
    return redirect('post', username=post.author.username, post_id=post_id)


@login_required
def follow_index(request):
    follow = User.objects.get(username=request.user.username)
    post_list = Post.objects.filter(author__following__user=follow).select_related(
        'author').order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'paginator': paginator, 'page': page})


@login_required
def profile_follow(request, username):
    user = User.objects.get(username=request.user.username)
    author = User.objects.get(username=username)
    if request.user.username != username:
        if not Follow.objects.filter(user=user, author=author).count():
            Follow(user=user, author=author).save()
        return redirect('profile', username=username)
    return redirect('login')


@login_required
def profile_unfollow(request, username):
    user = User.objects.get(username=request.user.username)
    author = User.objects.get(username=username)
    Follow.objects.filter(user=user, author=author).all().delete()
    return redirect('profile', username=username)
