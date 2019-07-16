from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
import datetime

from .models import Question, Choice


def create_question(question_text, days):
    """
    Create question with the given question_text and published the number of days offset from now
    (negative for question published in the past, positive for question in the future)
    """
    time = timezone.now()+datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question: Question, choice_text, votes):
    return Choice.objects.create(choice_text=choice_text, votes=votes, question=question)

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() return False for question whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)
        
    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date = time)
        self.assertIs(old_question.was_published_recently(), False)
        
    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
        
class QuestionIndexViewTests(TestCase):
        
    def test_no_question(self):
        """
        If no questions exists, an appropriate message is displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
        
    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        create_question(question_text="Past question.", days=-30)
        response=self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
                response.context['latest_question_list'],
                ['<Question: Past question.>']
        )
    
    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
        
    def test_future_question_and_past_question(self):
        """
        The questions index page may display multiple questions
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        create_question(question_text="Future question.", days=10)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
                response.context['latest_question_list'],
                ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )
        
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        questions with a pub_date in the future can not be accessed 
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        """
        questions with a pub_date in the past can be accessed
        """
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionResultsViewTest(TestCase):
    def test_1_votes(self):
        """
        questions with 1 vote has only one vote
        """
        question = create_question(question_text="Question.", days=-1)
        choice = create_choice(question, "first choice", 1)
        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, choice.choice_text)
        self.assertContains(response, "1 vote")
    
    def test_different_votes(self):
        """
        questions with different number of votes
        """
        question = create_question(question_text="Question.", days=-1)
        choice1 = create_choice(question, "first choice", 0)
        choice2 = create_choice(question, "second choice", 1)
        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, choice1.choice_text)
        self.assertContains(response, choice2.choice_text)
        self.assertContains(response, "0 votes")
        self.assertContains(response, "1 vote")
    
    def test_future_question_not_show(self):
        """
        Can't see results for future questions
        """
        question = create_question(question_text="Question", days=1)
        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)