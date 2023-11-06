from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ User model helps us gather users in our database and categorize
    their respective tasks in our organization. """
    is_organizer = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)


class Category(MPTTModel):
    name = models.CharField(
        max_length=settings.MUSIC_TITLE_MAX_LENGTH, unique=True)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(
        max_length=settings.MUSIC_TITLE_MAX_LENGTH, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        expected_value = self.name

        if self.slug:
            self.slug = slugify(expected_value, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("songs-by-category", args=[str(self.slug)])


class Song(models.Model):
    title = models.CharField(max_length=settings.MUSIC_TITLE_MAX_LENGTH)
    category = TreeForeignKey(
        'Category', on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=settings.MUSIC_TITLE_MAX_LENGTH)
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        kwargs = {'slug': self.slug}
        return reverse("song-detail", kwargs=kwargs)

    def save(self, *args, **kwargs):
        if self.slug:
            expected_value = self.title
            self.slug = slugify(expected_value, allow_unicode=True)
        super().save(*args, **kwargs)


class Subscribe(models.Model):
    email = models.EmailField(unique=True, max_length=50)
    date_subscribed = models.DateTimeField(auto_now_add=True)
   
    def __str__(self) -> str:
        return self.email
    
    