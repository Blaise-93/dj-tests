from django.db import models
from django.db.models.signals import post_save, pre_save
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import View
from songs.models import User

class Lead(models.Model):
    SOURCE_CHOICES = (
        ("Youtube", "Youtube"),
        ("Facebook", "Facebook"),
        ("Newsletter", "Newsletter")
    )
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    age = models.IntegerField(default=0, verbose_name="client_age")
    # allows us to collate agents based on the organization
    organization = models.ForeignKey('UserProfile', on_delete=models.CASCADE, null=True)

    # the quotation mark "" on Agent tells Django that Agent is inside this file, Lead
    # agent -> foreign key allows us to set one agent to many leads assigned to an
    # agent. Foreign keys allows us to create many agents for one user.
    # we reassign the agent if the agent leads are deleted from db
    # related_name => to do relationship modeling
    
    agent = models.ForeignKey(
        "Agent", on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey("Category", related_name='leads', on_delete=models.SET_NULL, null=True, blank=True)

    social_media_accounts = models.CharField(
        choices=SOURCE_CHOICES, max_length=20, default="Facebook")
    phoned = models.BooleanField(default=False)

    files = models.FileField(blank=True, null=True,
                             upload_to="media/products/")
    
    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

""" Eg matt_agent = Agent.objects.get(user__username="blaise") 
    matt_agent => is the Agent instance set for the lead to 
    manage a given lead or leads. The __ helps to double filter the
    data from the user - foreignkey.
    
    Manager && Queryset
"""

class Agent(models.Model):
    """ Agent of our models """
    # Foreign (many-to-one) keys allow us to create many agents for one user
    # OneToOneField: one-to-one relationship - so no list of many agents of one user will be returned.
    #ManyToManyField: 
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1) # every agents has one user
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    date_joined = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.user.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.user.username
    
class Category(models.Model):
    """ model that categorized the leads based on the conversion/sales process. 
        Thus, every lead should be assigned to category model.
        
        Category Types: New, Converted, Unconverted?
    """

    name = models.CharField(max_length=30)
    organization = models.ForeignKey("Userprofile", on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['id']
    
    def __str__(self) -> str:
        return self.name
     


def post_user_created_signal(sender, instance, created, **kwargs):
    """ Listening to events using signals """
    # print(instance, created) # username get printed of the user
    
    if created:
        UserProfile.objects.create(user=instance)
    
post_save.connect(post_user_created_signal, sender=User)
