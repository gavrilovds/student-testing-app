from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseForbidden
from django.forms import formset_factory, inlineformset_factory
from .models import Subject, Test, Question, Choice, TestAttempt, Answer, SelectedChoice
from .forms import (
    SubjectForm, TestForm, QuestionForm, ChoiceForm, 
    TextAnswerForm, SingleChoiceAnswerForm, MultipleChoiceAnswerForm, BaseAnswerFormSet
)

def home_view(request):
    subjects = Subject.objects.all()
    tests = Test.objects.filter(is_active=True)
    
    context = {
        'subjects': subjects,
        'tests': tests,
    }
    return render(request, 'tests_app/home.html', context)

@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'tests_app/subject_list.html', {'subjects': subjects})

@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    tests = Test.objects.filter(subject=subject, is_active=True)
    
    context = {
        'subject': subject,
        'tests': tests,
    }
    return render(request, 'tests_app/subject_detail.html', context)

@login_required
def subject_create(request):
    if not request.user.profile.is_teacher:
        return HttpResponseForbidden("Только преподаватели могут создавать дисциплины")
    
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дисциплина успешно создана!')
            return redirect('subject_list')
    else:
        form = SubjectForm()
    
    return render(request, 'tests_app/subject_form.html', {'form': form})

@login_required
def test_list(request):
    if request.user.profile.is_teacher:
        tests = Test.objects.filter(created_by=request.user)
    else:
        tests = Test.objects.filter(is_active=True)
    
    context = {
        'tests': tests,
    }
    return render(request, 'tests_app/test_list.html', context)

@login_required
def test_detail(request, pk):
    test = get_object_or_404(Test, pk=pk)
    
    # Проверяем, может ли пользователь просматривать тест
    if not test.is_active and not request.user.profile.is_teacher and test.created_by != request.user:
        return HttpResponseForbidden("Этот тест недоступен")
    
    questions = test.questions.all().order_by('order')
    
    # Для преподавателя показываем детали теста
    if request.user.profile.is_teacher:
        context = {
            'test': test,
            'questions': questions,
        }
        return render(request, 'tests_app/test_detail_teacher.html', context)
    
    # Для студента проверяем, есть ли незавершенные попытки
    attempts = TestAttempt.objects.filter(test=test, student=request.user)
    active_attempt = attempts.filter(completed_at__isnull=True).first()
    
    context = {
        'test': test,
        'attempts': attempts,
        'active_attempt': active_attempt,
    }
    return render(request, 'tests_app/test_detail_student.html', context)

@login_required
def test_create(request):
    if not request.user.profile.is_teacher:
        return HttpResponseForbidden("Только преподаватели могут создавать тесты")
    
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.created_by = request.user
            test.save()
            messages.success(request, 'Тест успешно создан!')
            return redirect('test_detail', pk=test.pk)
    else:
        form = TestForm()
    
    return render(request, 'tests_app/test_form.html', {'form': form})

@login_required
def test_update(request, pk):
    test = get_object_or_404(Test, pk=pk)
    
    if not request.user.profile.is_teacher or test.created_by != request.user:
        return HttpResponseForbidden("У вас нет прав для редактирования этого теста")
    
    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тест успешно обновлен!')
            return redirect('test_detail', pk=test.pk)
    else:
        form = TestForm(instance=test)
    
    return render(request, 'tests_app/test_form.html', {'form': form, 'test': test})

@login_required
def question_create(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    
    if not request.user.profile.is_teacher or test.created_by != request.user:
        return HttpResponseForbidden("У вас нет прав для добавления вопросов к этому тесту")
    
    # Определяем порядок нового вопроса
    order = test.questions.count() + 1
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.test = test
            question.order = order
            question.save()
            
            # Если тип вопроса предполагает варианты ответов, перенаправляем на страницу добавления вариантов
            if question.question_type in ['single', 'multiple']:
                return redirect('choice_create', question_id=question.pk)
            
            messages.success(request, 'Вопрос успешно добавлен!')
            return redirect('test_detail', pk=test.pk)
    else:
        question_form = QuestionForm(initial={'order': order})
    
    context = {
        'question_form': question_form,
        'test': test,
    }
    return render(request, 'tests_app/question_form.html', context)

@login_required
def question_update(request, pk):
    question = get_object_or_404(Question, pk=pk)
    test = question.test
    
    if not request.user.profile.is_teacher or test.created_by != request.user:
        return HttpResponseForbidden("У вас нет прав для редактирования этого вопроса")
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вопрос успешно обновлен!')
            return redirect('test_detail', pk=test.pk)
    else:
        form = QuestionForm(instance=question)
    
    context = {
        'question_form': form,
        'test': test,
        'question': question,
    }
    return render(request, 'tests_app/question_form.html', context)

@login_required
def choice_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    test = question.test
    
    if not request.user.profile.is_teacher or test.created_by != request.user:
        return HttpResponseForbidden("У вас нет прав для добавления вариантов ответов к этому вопросу")
    
    # Создаем formset для вариантов ответов
    ChoiceFormSet = inlineformset_factory(
        Question, Choice, form=ChoiceForm, extra=4, can_delete=True
    )
    
    if request.method == 'POST':
        formset = ChoiceFormSet(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Варианты ответов успешно сохранены!')
            return redirect('test_detail', pk=test.pk)
    else:
        formset = ChoiceFormSet(instance=question)
    
    context = {
        'formset': formset,
        'question': question,
        'test': test,
    }
    return render(request, 'tests_app/choice_form.html', context)

@login_required
def start_test(request, test_id):
    if not request.user.profile.is_student:
        return HttpResponseForbidden("Только студенты могут проходить тесты")
    
    test = get_object_or_404(Test, pk=test_id, is_active=True)
    
    # Проверяем, есть ли уже активная попытка
    active_attempt = TestAttempt.objects.filter(
        test=test, student=request.user, completed_at__isnull=True
    ).first()
    
    if active_attempt:
        return redirect('take_test', attempt_id=active_attempt.pk)
    
    # Создаем новую попытку
    attempt = TestAttempt.objects.create(
        test=test,
        student=request.user,
        started_at=timezone.now(),
        max_score=sum(q.points for q in test.questions.all())
    )
    
    return redirect('take_test', attempt_id=attempt.pk)

@login_required
def take_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, pk=attempt_id)
    
    # Проверяем, что это попытка текущего пользователя
    if attempt.student != request.user:
        return HttpResponseForbidden("Это не ваша попытка прохождения теста")
    
    # Проверяем, не завершена ли уже попытка
    if attempt.is_completed:
        return redirect('test_results', attempt_id=attempt.pk)
    
    test = attempt.test
    questions = test.questions.all().order_by('order')
    
    # Получаем текущий вопрос (первый без ответа)
    answered_questions = Answer.objects.filter(attempt=attempt).values_list('question_id', flat=True)
    current_question = questions.exclude(id__in=answered_questions).first()
    
    # Если все вопросы отвечены, завершаем тест
    if not current_question:
        return complete_test(request, attempt.pk)
    
    # Создаем форму в зависимости от типа вопроса
    if current_question.question_type == 'text':
        form = TextAnswerForm()
    elif current_question.question_type == 'single':
        form = SingleChoiceAnswerForm(question=current_question)
    else:  # multiple
        form = MultipleChoiceAnswerForm(question=current_question)
    
    if request.method == 'POST':
        if current_question.question_type == 'text':
            form = TextAnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.attempt = attempt
                answer.question = current_question
                answer.save()
                return redirect('take_test', attempt_id=attempt.pk)
        
        elif current_question.question_type == 'single':
            form = SingleChoiceAnswerForm(current_question, request.POST)
            if form.is_valid():
                with transaction.atomic():
                    answer = Answer.objects.create(
                        attempt=attempt,
                        question=current_question
                    )
                    selected_choice = form.cleaned_data['choice']
                    SelectedChoice.objects.create(
                        answer=answer,
                        choice=selected_choice
                    )
                    
                    # Автоматически оцениваем ответ
                    if selected_choice.is_correct:
                        answer.score = current_question.points
                    else:
                        answer.score = 0
                    answer.save()
                
                return redirect('take_test', attempt_id=attempt.pk)
        
        else:  # multiple
            form = MultipleChoiceAnswerForm(current_question, request.POST)
            if form.is_valid():
                with transaction.atomic():
                    answer = Answer.objects.create(
                        attempt=attempt,
                        question=current_question
                    )
                    
                    selected_choices = form.cleaned_data['choices']
                    for choice in selected_choices:
                        SelectedChoice.objects.create(
                            answer=answer,
                            choice=choice
                        )
                    
                    # Автоматически оцениваем ответ
                    correct_choices = current_question.choices.filter(is_correct=True)
                    selected_correct = sum(1 for c in selected_choices if c.is_correct)
                    selected_incorrect = len(selected_choices) - selected_correct
                    
                    if selected_incorrect == 0 and selected_correct == correct_choices.count():
                        # Все правильные и только правильные
                        answer.score = current_question.points
                    elif selected_correct > 0 and selected_incorrect == 0:
                        # Частично правильный ответ
                        answer.score = (selected_correct / correct_choices.count()) * current_question.points
                    else:
                        # Есть неправильные ответы
                        answer.score = 0
                    
                    answer.save()
                
                return redirect('take_test', attempt_id=attempt.pk)
    
    # Вычисляем оставшееся время
    time_limit_seconds = test.time_limit * 60
    elapsed_seconds = (timezone.now() - attempt.started_at).total_seconds()
    remaining_seconds = max(0, time_limit_seconds - elapsed_seconds)
    
    context = {
        'attempt': attempt,
        'test': test,
        'current_question': current_question,
        'form': form,
        'remaining_seconds': remaining_seconds,
        'progress': (len(answered_questions) / questions.count()) * 100,
    }
    return render(request, 'tests_app/take_test.html', context)

@login_required
def complete_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, pk=attempt_id, student=request.user)
    
    if attempt.is_completed:
        return redirect('test_results', attempt_id=attempt.pk)
    
    # Вычисляем итоговый балл
    answers = Answer.objects.filter(attempt=attempt)
    total_score = sum(a.score or 0 for a in answers)
    
    # Завершаем попытку
    attempt.completed_at = timezone.now()
    attempt.score = total_score
    attempt.save()
    
    return redirect('test_results', attempt_id=attempt.pk)

@login_required
def test_results(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, pk=attempt_id)
    
    # Проверяем, что это попытка текущего пользователя или преподаватель, создавший тест
    if attempt.student != request.user and (not request.user.profile.is_teacher or attempt.test.created_by != request.user):
        return HttpResponseForbidden("У вас нет доступа к этим результатам")
    
    answers = Answer.objects.filter(attempt=attempt).order_by('question__order')
    
    context = {
        'attempt': attempt,
        'test': attempt.test,
        'answers': answers,
    }
    return render(request, 'tests_app/test_results.html', context)

@login_required
def student_attempts(request):
    if not request.user.profile.is_student:
        return HttpResponseForbidden("Эта страница доступна только для студентов")
    
    attempts = TestAttempt.objects.filter(student=request.user).order_by('-started_at')
    
    context = {
        'attempts': attempts,
    }
    return render(request, 'tests_app/student_attempts.html', context)

@login_required
def teacher_results(request):
    if not request.user.profile.is_teacher:
        return HttpResponseForbidden("Эта страница доступна только для преподавателей")
    
    tests = Test.objects.filter(created_by=request.user)
    test_id = request.GET.get('test_id')
    
    if test_id:
        attempts = TestAttempt.objects.filter(test_id=test_id, completed_at__isnull=False).order_by('-completed_at')
    else:
        attempts = TestAttempt.objects.filter(test__created_by=request.user, completed_at__isnull=False).order_by('-completed_at')
    
    context = {
        'tests': tests,
        'attempts': attempts,
        'selected_test_id': int(test_id) if test_id else None,
    }
    return render(request, 'tests_app/teacher_results.html', context)
