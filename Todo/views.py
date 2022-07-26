from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login

from .models import *


from django.urls import reverse_lazy

# Create your views here.

#The login view (This logic allows registered users to login and redirect them back to the tasklist)
class PersonLoginView(LoginView):
    template_name = "Todo_templates/login.html" #The template design for the login page
    fields = "__all__" #The fields that shows django inbuilt username, password1 and password2
    redirect_authenticated_user = True # This attribute makes it possible for already login user (authenticated user) not to be able to view the login page again, once they are already logged in

    def get_success_url(self):
        return reverse_lazy("tasklist") #This function was created in order to redirect a user who logins with valid details back to the homepage which shows all the tasks

#The RegistrationPage()
class RegistrationPage(FormView):
    template_name = "Todo_templates/register.html" #The template design for the registrationpage
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("tasklist")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegistrationPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("tasklist")
        return super(RegistrationPage, self).get(*args, **kwargs)


#This is the Homepage view that would display all the task of a user
class TaskList(LoginRequiredMixin, ListView):
    model = TodoTaskModel
    template_name = "Todo_templates/tasklist.html"
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = context["tasks"].filter(person=self.request.user)
        context["counttask"] = context["tasks"].filter(complete=False).count()


        search_input = self.request.GET.get('search-area') or ""
        if search_input:
            context["tasks"] = context["tasks"].filter(title__icontains=search_input)

        context['search_input'] = search_input
        return context



# This is the detailpage view, that shows each task that has been created
class TaskDetail(LoginRequiredMixin, DetailView):
    model = TodoTaskModel
    template_name = "Todo_templates/taskdetails.html"
    context_object_name = "tasksdetails"


# This is the task creation view, that displays the task create page, once a user clicks on add tasks
class TaskCreate(LoginRequiredMixin, CreateView):
    model = TodoTaskModel
    template_name = "Todo_templates/taskcreate.html"
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasklist")

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super(TaskCreate, self).form_valid(form)


# This is the update view, whereby an already logged in user can update a specific task
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = TodoTaskModel
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasklist")
    template_name = "Todo_templates/taskcreate.html"


# This is the delete view, that displays the delete page, once a user try delete a task
class TaskDelete(DeleteView):
    model = TodoTaskModel
    template_name = "Todo_templates/taskdelete.html"
    context_object_name = "taskname"
    success_url = reverse_lazy("tasklist")
