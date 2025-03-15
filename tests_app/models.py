from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название дисциплины")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

class Test(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название теста")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="tests", verbose_name="Дисциплина")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tests", verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    time_limit = models.PositiveIntegerField(default=30, verbose_name="Ограничение времени (минуты)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'Текстовый ответ'),
        ('single', 'Единственный выбор'),
        ('multiple', 'Множественный выбор'),
    )
    
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions", verbose_name="Тест")
    text = models.TextField(verbose_name="Текст вопроса")
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, verbose_name="Тип вопроса")
    points = models.PositiveIntegerField(default=1, verbose_name="Баллы")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    correct_text_answer = models.TextField(blank=True, null=True, verbose_name="Правильный текстовый ответ")
    
    def __str__(self):
        return f"{self.test.title} - Вопрос {self.order}"
    
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['order']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices", verbose_name="Вопрос")
    text = models.CharField(max_length=255, verbose_name="Текст варианта")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    
    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

class TestAttempt(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts", verbose_name="Тест")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="test_attempts", verbose_name="Студент")
    started_at = models.DateTimeField(default=timezone.now, verbose_name="Время начала")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Время завершения")
    score = models.FloatField(null=True, blank=True, verbose_name="Набранные баллы")
    max_score = models.FloatField(null=True, blank=True, verbose_name="Максимальные баллы")
    
    def __str__(self):
        return f"{self.student.username} - {self.test.title}"
    
    @property
    def is_completed(self):
        return self.completed_at is not None
    
    @property
    def score_percentage(self):
        if self.score is not None and self.max_score:
            return (self.score / self.max_score) * 100
        return 0
    
    class Meta:
        verbose_name = "Попытка теста"
        verbose_name_plural = "Попытки тестов"

class Answer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers", verbose_name="Попытка")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Вопрос")
    text_answer = models.TextField(blank=True, null=True, verbose_name="Текстовый ответ")
    score = models.FloatField(null=True, blank=True, verbose_name="Баллы")
    
    def __str__(self):
        return f"Ответ на {self.question}"
    
    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

class SelectedChoice(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="selected_choices", verbose_name="Ответ")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, verbose_name="Выбранный вариант")
    
    def __str__(self):
        return f"{self.answer} - {self.choice.text}"
    
    class Meta:
        verbose_name = "Выбранный вариант"
        verbose_name_plural = "Выбранные варианты"
