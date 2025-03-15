from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    
    # Маршруты для дисциплин
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    
    # Маршруты для тестов
    path('tests/', views.test_list, name='test_list'),
    path('tests/<int:pk>/', views.test_detail, name='test_detail'),
    path('tests/create/', views.test_create, name='test_create'),
    path('tests/<int:pk>/update/', views.test_update, name='test_update'),
    
    # Маршруты для вопросов и вариантов ответов
    path('tests/<int:test_id>/questions/create/', views.question_create, name='question_create'),
    path('questions/<int:pk>/update/', views.question_update, name='question_update'),
    path('questions/<int:question_id>/choices/', views.choice_create, name='choice_create'),
    
    # Маршруты для прохождения тестов
    path('tests/<int:test_id>/start/', views.start_test, name='start_test'),
    path('attempts/<int:attempt_id>/take/', views.take_test, name='take_test'),
    path('attempts/<int:attempt_id>/complete/', views.complete_test, name='complete_test'),
    path('attempts/<int:attempt_id>/results/', views.test_results, name='test_results'),
    
    # Маршруты для просмотра результатов
    path('my-attempts/', views.student_attempts, name='student_attempts'),
    path('results/', views.teacher_results, name='teacher_results'),
] 