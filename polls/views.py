from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import Choice, Question
from django.utils import timezone

class IndexView(generic.ListView):
    template_name= 'polls/index.html'
    context_object_name = 'latest_question_list'
    
    def get_queryset(self):
        return Question.objects.filter(
                pub_date__lte = timezone.now()
                ).order_by('-pub_date')[:5]
    
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/questions.html'

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'
    
#def index(request):
#    latest_question_list = Question.objects.order_by('-pub_date')[:5]
#    template = loader.get_template('polls/index.html')
#    context = {
#            'latest_question_list': latest_question_list,
#    }
#    return HttpResponse(template.render(context, request))
#
#def detail(request, question_id):
#    try:
#        question = Question.objects.get(pk=question_id)
#    except Question.DoesNotExist:
#        raise Http404("Question does not exist")
#    context = {'question': question}
#    return render(request, 'polls/questions.html', context)
#
#def results(request, question_id):
#    question = get_object_or_404(Question, pk=question_id)
#    return render(request, 'polls/results.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/questions.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
                })
        
    selected_choice.votes +=1
    selected_choice.save()
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))