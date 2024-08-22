from django.http import Http404
from django.views.generic import ListView
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout


from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Choice, Question, PollUser


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes  += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def index(request):
    if request.user.is_authenticated:
        questions = Question.objects.order_by("-pub_date")[:5]
        context = {"latest_question_list": questions}
        return render(request, "polls/index.html", context)

    else:
        return HttpResponseRedirect("/polls/login")


def detail(request, question_id):
    if request.user.is_authenticated:
        q=get_object_or_404(Question, pk = question_id)
        return render(request, "polls/detail/html", {"question": q})
    else:
        return HttpResponseRedirect("/polls/login")

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

class IndexView(ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]
    
def get_queryset(self):
    """
    Return the last five published questions (not including those set to be
    published in the future).
    """
    return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
        :5
    ]

def register(request):
    if request.method == "GET":
        return render(request, "polls/register.html", {})
    firstname = request.POST['fname']
    lastname = request.POST['lname']
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    country = request.POST['country']

    user = User.objects.create_user(first_name = firstname,
                                    last_name = lastname,
                                    username = username,
                                    password = password,
                                    email = email)
    user.save()
    pu = PollUser(user = user, country = country)
    pu.save()
    return HttpResponseRedirect("/polls/login")
    
def newquestion(request):
    if request.method == "GET":
        return render(request, "polls/index.html", {})
    
    newquestion_text = request.POST['newquestion']
    newq = Question(question_text=newquestion_text, pub_date=timezone.now())
    newq.save()
    return HttpResponseRedirect("/polls/")

def login(request):
    if request.method == "GET":
        return render(request, "polls/login.html", {})
    
    usr = request.POST['username']
    pswd = request.POST['password']

    user = authenticate(username=usr, password=pswd)
    if user:
        auth_login(request, user)
        return HttpResponseRedirect("/polls/")
    
    return render(request, "polls/login.html", {"error": "username or password is wrong"})

def log_out(request):
    logout(request)
    return HttpResponseRedirect("/polls/login")