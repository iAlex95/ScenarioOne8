from django.views.generic.list import ListView
from django.views.generic.edit import CreateView

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect


from toDoApp.models import List, Task
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


from .forms import newListForm, newTaskForm, UserForm, LoginForm 

def adduser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            return HttpResponseRedirect('/loginuser/')
    else:
        form = UserForm() 

    return render(request, 'toDoApp/adduser.html', {'form': form})

def loginuser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/user/')
            else:
                return HttpResponse("Invalid login")
    else:
        form = LoginForm()

    return render(request, 'toDoApp/loginuser.html', {'form': form})


def logoutuser(request):
    logout(request)
    return HttpResponseRedirect('/loginuser/')


class UserListView(ListView):
	model = List
	context_object_name = 'list_list'

	def get_context_data(self, **kwargs):
		context = super(UserListView, self).get_context_data(**kwargs)
		context['user'] = self.request.user
		return context

	def get_queryset(self):
		currentUser = self.request.user
		userLists = List.objects.filter(user = currentUser)
		return userLists

@login_required
def createList(request):
	if request.method == 'POST':
		form = newListForm(request.POST)
		if form.is_valid():
			newList = form.save(commit=False)
			newList.user = request.user
			newList.save()
			return HttpResponseRedirect('/user/')
	else:
		form = newListForm()

	return render(request, 'toDoApp/createList.html', {'form': form})
		

class TaskListView(ListView):
	template_name = "toDoApp/task_list.html"
	context_object_name = 'task_list'

	def get_context_data(self, **kwargs):
		context = super(TaskListView, self).get_context_data(**kwargs)
		if self.list.user == self.request.user:
			context['list'] = self.list
			return context

	def get_queryset(self):
		self.list = get_object_or_404(List, id=self.kwargs['listID'])
		if self.list.user == self.request.user: 
			return Task.objects.filter(theList_id = self.list.id)
		else:
			return HttpResponseRedirect('/loginuser/')


@login_required
def createTask(request, listID):
	if request.method == 'POST':
		form = newTaskForm(request.POST)
		if form.is_valid():
			newTask = form.save(commit=False)
			newTask.theList = List.objects.get(id=listID)
			newTask.completed = False
			newTask.save()
			
			url = reverse('task-list', args = (listID,))
			return HttpResponseRedirect(url)
	else:
		form = newTaskForm()
	return render(request, 'toDoApp/createTask.html', {'form': form})
		

def index(request):
	return render(request, 'toDoApp/index.html')


# Create your views here.

