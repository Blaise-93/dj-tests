from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from leads.models import UserProfile
from django.utils.text import slugify
from utils import slug_modifier, generate_patient_unique_code
from songs.models import User
from datetime import datetime, timedelta
from django.utils import timezone


class Attendance(models.Model):
    """ A model responsible for creating attendance table of an instance made in our db
    with relationship mapping of the organization and an assigned management."""

    full_name = models.CharField(max_length=30)
    sign_in_time = models.CharField(
        max_length=5,
        help_text='Enter the time you resumed for work in this format -> 8:00')
    date_added = models.CharField(
        max_length=10, help_text='Enter the date you resumed for work in this format -> 12/12/2023')
    staff_attendance_ref = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Staff Daily Attendance Ref ")

    sign_out_time = models.CharField(
        # allows us to collate managements based on the organization
        max_length=5,
        null=True, blank=True,
        help_text=f'Enter the time you closed for work in this format ->\
            8:00. Make sure you update this field and fill in the option \
                before you leave your workplace, not now please.')
    
    organization = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE)
    
    user = models.ForeignKey(
        'leads.ManagementProfile', on_delete=models.CASCADE)
    
    management = models.ForeignKey(
        "Management", on_delete=models.CASCADE, verbose_name='Management')
    date_sign_out_time = models.CharField(max_length=7, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField()

    class Meta:
        verbose_name_plural = "Attendance"
        ordering = ['id',]

    def __str__(self) -> str:
        return f'{self.full_name}'

    def get_west_african_time(self):
        """ converts the utc time to West African time for the user 
        on the frontend - however, the admin panel still maintained 
        UTC+0 time integrity."""

        """  date_time = datetime.strptime(
            str(self.date_created.date()), '%Y-%m-%d')
        lagos_time = date_time + timedelta(hours=2)
        print(lagos_time)
        return lagos_time """

        lagos_time = timezone.localtime(
            self.date_created, timezone.get_fixed_timezone(120))

        return lagos_time

    def get_fullname(self) -> str:
        """ validates full name input by the user """
        if self.full_name <= 8:
            return 'Kindly enter your full name'
        return self.full_name

    def get_sign_out_time(self):
        """ a helper function to accurately output when the staff signed out 
        from our register, and attached `am or pm in string` to the validated input
        required."""
        hours = datetime.now().hour

        if hours >= 4 and hours < 12:
            return f"{self.sign_in_time} AM"
        else:
            return f"{self.sign_in_time} PM"

    def get_sign_in_time(self):
        """ a helper function to accurately output when the staff signed out 
        from our register, and attached `am or pm string` to the validated input
        required."""
        hours = datetime.now().hour

        if hours >= 4 and hours < 12:
            return f"{self.sign_in_time} AM"
        else:
            return f"{self.sign_in_time} PM"

    def time_utc(self):
        """ a helper function to accurately output when attendance starts to 
        be recorded in our model when we enter a new day of the week."""

        hours = datetime.now().hour

        if hours >= 4 and hours < 12:
            return f"Today's attendance records starts by {self.date_created} this\
                {self.date_created.weekday()} morning. "

        elif hours >= 12 and hours < 17:
            return f"Today's attendance records starts by {self.date_created} this\
             {self.date_created.weekday()} afternoon. "
        elif hours >= 17 and hours < 20:
            return f"Today's attendance records starts by {self.date_created} this\
             {self.date_created.weekday()} evening. "
        else:
            return f'Good night {self.get_west_african_time()}'

    def save(self, *args, **kwargs):
        """ override the original save method to set the lead 
        according to if agent has phoned or not"""

        self.slug = slugify(
            f'{(self.full_name + slug_modifier())}', allow_unicode=False)

        self.staff_attendance_ref = generate_patient_unique_code()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("staff:staff-detail", kwargs={"slug": self.slug})


class Management(models.Model):
    """ Management of our models. Managements are assigned to each attendance
    made by our staff in our compnay
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    phone_number = models.CharField(max_length=12,
                                    validators=[MinValueValidator("010100000"),
                                                MaxValueValidator("099010100000")])
    email = models.EmailField(max_length=30, unique=True)
    slug = models.SlugField()
    organization = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.username

    def get_west_african_time_zone(self):
        """ converts the utc time to West African time for the user 
        on the frontend - however, the admin panel still maintained 
        UTC+0 time integrity."""
        date_time = datetime.strptime(
            str(self.date_joined.date()), '%Y-%m-%d')
        lagos_time = date_time + timedelta(hours=2)
        return lagos_time

    def save(self, *args, **kwargs):
        """ override the original save method to set the lead 
        according to if agent has phoned or not"""

        self.slug = slugify(
            f'{self.first_name + slug_modifier()}', allow_unicode=False)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('managements:managements-detail', kwargs={
            'slug': self.slug
        })
