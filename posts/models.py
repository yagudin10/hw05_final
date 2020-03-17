from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published",
                                    auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="post_author")
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True, null=True)
    image = models.ImageField(upload_to='posts/',
                              blank=True, null=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.SET_NULL,
                             blank=True, null=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comment_author")
    text = models.TextField()
    created = models.DateTimeField("created", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE)
