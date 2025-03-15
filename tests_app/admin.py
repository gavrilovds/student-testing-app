from django.contrib import admin
from .models import Subject, Test, Question, Choice, TestAttempt, Answer, SelectedChoice

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'question_type', 'points', 'order')
    list_filter = ('test', 'question_type')
    search_fields = ('text', 'test__title')
    inlines = [ChoiceInline]

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created_by', 'created_at', 'time_limit', 'is_active')
    list_filter = ('subject', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    date_hierarchy = 'created_at'

class SelectedChoiceInline(admin.TabularInline):
    model = SelectedChoice
    extra = 0

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'attempt', 'score')
    list_filter = ('attempt__test',)
    search_fields = ('question__text', 'text_answer')
    inlines = [SelectedChoiceInline]

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('test', 'student', 'started_at', 'completed_at', 'score', 'max_score')
    list_filter = ('test', 'completed_at')
    search_fields = ('test__title', 'student__username')
    date_hierarchy = 'started_at'

admin.site.register(Choice)
admin.site.register(SelectedChoice)
