from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpRequest, HttpResponseNotFound, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count

from .models import *
from .forms import *


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.select_related('topic', 'host').filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(host__username__icontains=q) |
                                Q(description__icontains=q)).prefetch_related('participants')

    room_all = Room.objects.all().count()
    topics = Topic.objects.all()[:5].values('name', room_count=Count('room'))
    # topics = Topic.objects.all()[:5].values('name').annotate(room_count=Count('room'))
    room_messages = Message.objects.select_related('user', 'room').filter(room__topic__name__icontains=q).order_by('-created')[:6]

    paginator = Paginator(rooms, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'title': 'Главная страница',
               'topics': topics, 
               'room_messages':room_messages,
               'room_all': room_all,
                'page_obj': page_obj, }

    return render(request, 'main/home.html', context)


def room(request, pk):
    room = Room.objects.select_related('host', 'topic').prefetch_related('moderator', 'participants').get(pk=pk)

    if request.method == 'POST':
        if request.user.is_authenticated:
            message = Message(
                user=request.user,
                room=room,
                body=request.POST.get('body')
            )
            if len((message.body).strip())>0:
                message.save()
                room.participants.add(request.user)
            return redirect('room', pk=room.pk)
        else:
            messages.error(request, 'At first, you need to be logged in to write messages!')
            return redirect('login')

    context = {'title': 'Room страница', 'room': room}
    return render(request, 'main/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(pk=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()[:5]
    room_all = Room.objects.all().count()

    paginator = Paginator(rooms, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages[:7],
               'topics': topics, 'room_all': room_all,
               'page_obj': page_obj}

    return render(request, 'main/profile.html', context)


class CreateRoom(LoginRequiredMixin, CreateView):
    form_class = RoomCreationForm
    success_url = reverse_lazy('home')
    template_name = 'main/room_form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        topics = Topic.objects.all()
        c_def = {'topics': topics, }
        return context | c_def

    # def post(self, request, *args, **kwargs):
    #     form.save()
    #     topic_name = form.cleaned_data['topic']
    #     topic, created = Topic.objects.get_or_create(name=topic_name)
    #     Room.objects.create(
    #         host=self.request.user,
    #         topic=topic,
    #         name=form.cleaned_data['name'],
    #         description=form.cleaned_data['description'],
    #     )

    def get(self, request, *args, **kwargs):
        form = RoomCreationForm()
        topics = Topic.objects.all()
        return render(request, 'main/room_form.html', {'form':form, "topics":topics})

    def post(self, request, *args, **kwargs):
        form = RoomCreationForm(request.POST, request.FILES)
        if form.is_valid():
            topic_name = request.POST.get('topic')
            topic, created = Topic.objects.get_or_create(name=topic_name)
            room = Room.objects.create(
                host=request.user,
                topic=topic,
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                image=request.POST.get('image'),
            )
            room.participants.add(request.user)

            return redirect('home')


class RegisterUser(CreateView):
    form_class = MyUserCreationForm
    template_name = 'main/login_register.html'

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return redirect('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy('home')

    # def post(self, *args, **kwargs):
    #     name = self.request.POST.get('name')
    #     username = self.request.POST.get('username')
    #     email = self.request.POST.get('email')
    #     password = self.request.POST.get('password')
    #
    #
    #     user = User.objects.create(name=name,username=username,email=email)
    #     user.set_password(password)
    #     user.save()
    #
    #     send_action_email(user, self.request)

    # def form_valid(self, form):
    #     user = form.save(commit=False)
    #     user.is_active = False
    #     user.save()
    #     send_action_email(self.request)


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'main/login_register.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


    # def post(self, *args, **kwargs):
    #     username = self.request.POST.get('username')
    #     password = self.request.POST.get('password')
    #     user = authenticate(self.request, username=username, password=password)
    #
    #     if not user.is_email_verified:
    #         messages.add_message(self.request, messages.ERROR,
    #                              'Email is not verified, please check your email inbox')
    #         return render(self.request, 'main/login_register.html')
    #
    #     login(self.request, user)
    #     messages.add_message(self.request, messages.SUCCESS, f'Welcome {user.username}')

    def get_success_url(self):
        user = self.request.user
        user.is_online = True
        user.save()
        return reverse_lazy('home')


def logout_user(request):
    user = request.user
    user.is_online = False
    user.save()
    logout(request)
    messages.error(request, 'You logged out!')
    return redirect('login')


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.select_related('topic', 'host').get(pk=pk)
    form = RoomCreationForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        form = RoomCreationForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            topic_name = request.POST.get('topic')
            topic, created = Topic.objects.get_or_create(name=topic_name)
            room.topic = topic
            room.save()
            form.save()
            messages.info(request, 'Room was successfully updated!')

            return redirect('room', pk=pk)

    context = {'title': 'Updating room', 'form': form, 'topics':topics, 'room': room}
    return render(request, 'main/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.select_related('host').get(pk=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        messages.error(request, 'Room was successfully deleted!')
        return redirect('home')
    return render(request, 'main/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(pk=pk)
    room = Room.objects.get(pk=message.room.pk)
    moderators = room.moderator.all()

    if request.user == room.host:
        if request.method == 'POST':
            message.delete()
            return redirect('room', pk=message.room.pk)

    elif request.user in moderators:
        if message.user != room.host or message.user not in moderators:
            if request.method == 'POST':
                message.delete()
                return redirect('room', pk=message.room.pk)

    elif request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    return render(request, 'main/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=request.user)
    password_form = PasswordConfirmation()
    if request.method == 'POST':
        password_form = PasswordConfirmation(request.POST)
        password = request.POST['password']
        if user.check_password(password):
            form = UserForm(request.POST, request.FILES, instance=user)
            if form.is_valid() and password_form.is_valid():
                form.save()
                messages.success(request, 'User was successfully updated!')
                return redirect('user-profile', pk=user.pk)
    return render(request, 'main/update-user.html', {'form': form, 'password_form': password_form, })


@login_required(login_url='login')
def userAction(request, id, pk):
    room = Room.objects.get(pk=id)
    user = User.objects.get(pk=pk)
    moderators = room.moderator.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        if request.POST.get('delete'):
            room.participants.remove(user)
            body = str(request.user.username + " REMOVED " + 'user ' + user.username)
            Message.objects.create(room=room, body=body, user=request.user)
            room.save()

        elif request.POST.get('promote'):
            room.moderator.add(user)
            body = str(request.user.username + " PROMOTED to moderator " + 'user ' + user.username)
            Message.objects.create(room=room, body=body, user=request.user)
            room.save()

        elif request.POST.get('demote'):
            room.moderator.remove(user)
            body = str(request.user.username + " DEMOTED " + 'user ' + user.username)
            Message.objects.create(room=room, body=body, user=request.user)
            room.save()

        return redirect('room', pk=id)

    return render(request, 'main/room_action.html', {'obj': user, 'room': room, 'moderators': moderators })


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q).values('name', room_count=Count('room')).order_by("id")
    # topics = Topic.objects.filter(name__icontains=q).order_by("id")
    room_count = Room.objects.all().count()

    paginator = Paginator(topics, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'topics': topics, 'room_count': room_count, 'page_obj': page_obj}
    return render(request, 'main/topics.html', context)


def activityPage(request):
    topics = Topic.objects.all()
    room_messages = Message.objects.all().select_related('user', 'room').order_by('-created')

    paginator = Paginator(room_messages, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'topics': topics, 'room_messages':room_messages, "page_obj":page_obj}
    return render(request, 'main/activity.html', context)


def participantsPage(request, id):
    room = Room.objects.get(pk=id)
    participants = room.participants.all()
    moderators = room.moderator.all()

    paginator = Paginator(participants, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {"room": room, 'participants': participants, 'page_obj': page_obj, 'moderators': moderators}
    return render(request, 'main/participants.html', context)


def pageNotFound(response,exception):
    return HttpResponseNotFound("<h1>Страница не была найдена. Попробуйте другой адрес!</h1>")


def pageForbidden(response,exception):
    return HttpResponseForbidden("<h1>Ошибка доступа. Ошибка 403!</h1>")


def pageServerError(response):
    return HttpResponseServerError("<h1>Технические неполадки.</h1>")