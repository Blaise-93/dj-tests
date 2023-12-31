from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.text import slugify
from utils import slug_modifier
from django.core.exceptions import ObjectDoesNotExist
from django_countries.fields import CountryField



class Lead(models.Model):
    """ Model for our business lead collation and data manipulations"""

    SOURCE_CHOICES = (
        ("Youtube", "Youtube"),
        ("Facebook", "Facebook"),
        ("Twitter", "Twitter"),
        ("Instagram", "Instagram"),
        ("Reddit", "Reddit"),
        ("Discord", "Discord"),
        ("Github", "Github"),
        ("LinkedIn", "LinkedIn"),
        ("Tik Tok", "Tik Tok"),
        ("Others", "Others"),
        ("Snapchat", "Snapchat"),

    )

    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    age = models.IntegerField(default=0, verbose_name="client Age")

    organization = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    agent = models.ForeignKey(
        "Agent", on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Agent')
    category = models.ForeignKey("Category", related_name='leads',
                                 on_delete=models.SET_NULL, null=True, blank=True)

    social_media_accounts = models.CharField(
        choices=SOURCE_CHOICES, max_length=20, null=True, blank=True)
    phoned = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=12)
    description = models.TextField()
    email = models.EmailField(
        unique=True, max_length=100, null=True, blank=True)
    address = models.CharField(max_length=50,  null=True, blank=True)
    files = models.FileField(blank=True, null=True,
                             upload_to="media/products/")
    date_added = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()

    class Meta:
        ordering = ['id', 'phone_number']

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def get_email(self):
        if self.email is not None:
            return self.email
        return 'No email provided'

    def get_phone_number(self):
        if self.phone_number:
            return self.phone_number
        return 'No phone number provided'

    def get_description(self):
        if self.description:
            return self.description
        return 'No description provided'

    def get_social_media_account(self):
        if self.social_media_accounts:
            return self.social_media_accounts
        return 'Social account not provided'

    def get_file(self):
        if self.files:
            return self.files
        return 'File not provided'

    def get_address(self):
        if self.address:
            return self.address
        return 'Address not provided'

    def save(self, *args, **kwargs):
        """ override the original save method to set the lead 
        according to if agent has phoned or not"""

        self.slug = slugify(
            f'{(self.first_name + slug_modifier())}', allow_unicode=False)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("leads:lead-detail", kwargs={"slug": self.slug})

    def get_lead_category_update_url(self):
        return reverse('leads:category-update', kwargs={
            'slug': self.slug
        })


""" Eg matt_agent = Agent.objects.get(user__username="blaise") 
    matt_agent => is the Agent instance set for the lead to 
    manage a given lead or leads. The __ helps to double filter the
    data from the user - foreignkey.
    
    Manager && Queryset
"""


class Agent(models.Model):
    """ Agent of our models. Agents are assigned to each leads or to our patients. """

    user = models.OneToOneField('songs.User', on_delete=models.CASCADE, default=1)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    date_joined = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=30, unique=True)
    slug = models.SlugField()
    organization = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username

    def get_email(self):
        if self.email is not None:
            return self.email
        return 'Not email provided'

    def get_full_name(self):
        if self.email is not None:
            return f'{self.first_name} {self.last_name}'
        return 'Not yet provided'

    def save(self, *args, **kwargs):
        """ override the original save method to set the lead 
        according to if agent has phoned or not"""

        self.slug = slugify(
            f'{self.first_name + slug_modifier()}', allow_unicode=False)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('agents:agent-detail', kwargs={
            'slug': self.slug
        })

    def get_category_absolute_url(self):
        return reverse("leads:category-update", kwargs={"slug": self.slug})


class UserProfile(models.Model):
    """ model that create user one to one field for the organization """
    user = models.OneToOneField('songs.User', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username


class PharmacistProfile(models.Model):
    """ model that create user one to one field  for the pharmacist"""
    user = models.OneToOneField('songs.User', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username


class ManagementProfile(models.Model):
    """ model that create user one to one field  for the management"""
    user = models.OneToOneField('songs.User', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username


class Category(models.Model):
    """ model that categorized the leads based on the conversion/sales process. 
        Thus, every lead should be assigned to category model.

        Category Types: New, Converted, Unconverted?
    """

    name = models.CharField(max_length=30)
    organization = models.ForeignKey("UserProfile", on_delete=models.CASCADE)
    slug = models.SlugField(help_text="Enter the category's name")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['id']

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        """ override the original save method to set the lead 
        according to if agent has phoned or not"""

        self.slug = slugify(
            f'{self.name + slug_modifier()}', allow_unicode=False)

        super().save(*args, **kwargs)

    def get_category_absolute_url(self):
        return reverse("leads:category-update", kwargs={"slug": self.slug})


def post_user_created_signal(sender, instance, created, **kwargs):
    """ Listening to events using signals """
    # print(instance, created) # username get printed of the user
    user = instance
    try:
        if created:
            if sender.is_organizer:
                UserProfile.objects.create(user=user)
            elif sender.is_pharmacist:
                PharmacistProfile.objects.create(user=user)
            elif sender.is_management:
                ManagementProfile.objects.create(user=user)

    except ObjectDoesNotExist:
        UserProfile.objects.create(user=user)


post_save.connect(post_user_created_signal, sender='songs.User')


class Contact(models.Model):
    """ Contact us model to handle user's related complaints  """
    full_name = models.CharField(
        max_length=30, help_text='Enter your full name')
    email = models.EmailField(help_text='Input your Email', unique=True)
    country = CountryField(blank_label="--Select a Country-- *",
                           null=False, blank=False)
    subject = models.CharField(
        max_length=100, help_text='Kindly enter your request subject...')
    message = models.TextField(help_text="Kindly express your words to us...")
    user_ticket = models.CharField(max_length=60)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
