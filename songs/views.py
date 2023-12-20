from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from .models import Song, Category, SubscribedUsers
from .forms import NewsletterForm, SubscribedForm
from django.core.mail import send_mail, EmailMessage
from django.urls import reverse
from django.conf import settings
from django.db import IntegrityError
from utils import files, generate_patient_unique_code
from django.http import Http404
from django.views import generic
from leads.models import Contact
from leads.forms import ContactUsForm


def navigation(request):

    return render(request, 'songs/navigation.html')


class FooterView(LoginRequiredMixin, generic.CreateView):
    """ Handles mail subscription form request-response cycle.
    If the user had subscribed, it will give the user, a response message
    stating he/she had subscribed without throwing an IntegrityError message"""

    template_name = 'songs/footer.html'

    def post(self, *args, **kwargs):

        post_data = self.request.POST.copy()
        email = post_data.get("email", None)
        try:
            subscribedUsers = SubscribedUsers()
            subscribedUsers.email = email
            subscribedUsers.save()

            # send mail to the subscriber
            send_mail(
                subject="Newsletter Subscription",
                message=files('songs/mails/subscription.txt'),
                from_email=settings.FROM_EMAIL,
                recipient_list=[email, ],
                fail_silently=False
            )
            return redirect('landing-page')

        except IntegrityError as e:
            subject = 'NewsLetter Subscription'
            message = files('songs/mails/already-subscrribed.txt')
            email_from = settings.FROM_EMAIL
            recipient_list = [email, ]
            send_mail(
                subject,
                message,
                email_from,
                recipient_list,
                # settings.DEFAULT_FROM_EMAIL,
                # settings.EMAIL_HOST_USER,

            )
        return redirect('landing-page')


def newsletter(request):
    """ A httpResponseRedirect view to send multiple emails to our users who 
    subscribed to our newsletter instantly  """
    form = NewsletterForm(request.POST or None)
    try:
        if request.method == 'POST':
            if form.is_valid():
                subject = form.cleaned_data.get('subject')
                receivers = form.cleaned_data.get('receivers').split(',')
                email_message = form.cleaned_data.get('message')

                from_email = settings.FROM_EMAIL,
                mail = EmailMessage(
                    subject,
                    email_message,
                    from_email,
                    to=[receivers, ],
                    bcc=receivers)

                mail.content_subtype = 'html'

                if mail.send():

                    messages.info(
                        request, "The message was sent successfully.")

                else:
                    messages.error(request, "There was an error sending email")

            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
            return redirect('/')
        form.fields['receivers'].initial = ','.join(
            [active.email for active in SubscribedUsers.objects.all()])

        return render(request=request,
                      template_name='songs/newsletter.html',
                      context={'form': form})

    except Http404:
        return render(request, "songs/404-page.html")


def user_unsubscribed_newsletter(request):
    """ View to handle user unsubscribed request. """
    form = SubscribedForm(request.POST or None)
    context = {
        'form': form
    }
    if request.method == 'POST':
        if form.is_valid():
            email = email = form.cleaned_data.get('email')
            if SubscribedUsers.objects.filter(

                    email=form.cleaned_data.get('email')).exists():
                send_mail(
                    subject="Newsletter Subscription",
                    message=files('songs/mails/unsubscribed.txt'),
                    from_email=settings.FROM_EMAIL,
                    recipient_list=[email, ],
                    fail_silently=False
                )
                SubscribedUsers.objects.filter(
                    email=form.cleaned_data.get('email')).delete()
                return redirect("leads:home-page")

        else:
            return messages.info(request,
                                 'Sorry but we did not find your email address.')
        return redirect("leads:home-page")

    return render(request, 'unsubscribed.html', context)


class ContactView(LoginRequiredMixin, generic.CreateView):
    """ A view class that handles all the complaint/requests made by the user. """
    template_name = 'songs/contact.html'
    form_class = ContactUsForm
    queryset = Contact

    def get_success_url(self) -> str:
        return reverse('/')

    def form_valid(self, form):

        try:
            email = self.request.user.email
            # full_name = self.request.user.get_
            # assign and save user ticket/email to the database
            contact = form.save(commit=False)
            contact.email = email
            contact.user_ticket = generate_patient_unique_code()

            context = {
                'user': form.cleaned_data['full_name'],
                'ticket': contact.user_ticket
            }

            contact.save()

        # send email to the user
            send_mail(
                subject="CRM Customer Services",
                message=render_to_string('leads/complaint.html', context),
                recipient_list=[email, ],
                fail_silently=False

            )
            return super().form_valid(form)

        except IntegrityError:
            subject = 'NewsLetter Subscription'
            message = render_to_string('songs/has-subscribed.html', context)
            print(message)
            # email_from = settings.EMAIL_HOST_USER
            email_from = 'tests@gmail.com'
            recipient_list = [email, ]
            send_mail(
                subject,
                message,
                email_from,
                recipient_list,
                fail_silently=False
            )
            return redirect('/')


class CategoryListView(generic.ListView):
    model = Category
    template_name = 'songs/music_category_list.html'


class SongsByCategoryView(generic.ListView):
    ordering = 'id'
    paginate_by = 10
    # context_object_name = 'songs'
    template_name = 'songs/music_by_category.html'

    def get_queryset(self):

        # the following category will also be added to the context data
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Song.objects.filter(category=self.category)
        queryset = queryset.order_by(self.ordering)

        return queryset
       # return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
