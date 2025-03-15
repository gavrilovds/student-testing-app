from django import forms
from .models import Subject, Test, Question, Choice, Answer, TestAttempt

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'subject', 'description', 'time_limit', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points', 'order', 'correct_text_answer']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'correct_text_answer': forms.Textarea(attrs={'rows': 2}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']

class TextAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text_answer']
        widgets = {
            'text_answer': forms.Textarea(attrs={'rows': 3}),
        }

class SingleChoiceAnswerForm(forms.Form):
    choice = forms.ModelChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.RadioSelect,
        required=True,
        empty_label=None
    )
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choice'].queryset = question.choices.all()

class MultipleChoiceAnswerForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choices'].queryset = question.choices.all()

class BaseAnswerFormSet(forms.BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['question'] = self.questions[index]
        return kwargs 