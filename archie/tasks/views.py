from django.views.generic import ListView
from .models import Task


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/index.html'
