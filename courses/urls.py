from django.urls import path
from . import views

urlpatterns = [
    # Список курсов
    path('', views.course_list, name='course_list'),

    # Страница курса
    path('<int:course_id>/', views.course_detail, name='course_detail'),

    # ЗАПИСЬ НА КУРС (НОВОЕ)
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),

    # Страница урока
    path('<int:course_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),

    # Завершить урок
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),

    # Тест
    path('lesson/<int:lesson_id>/quiz/', views.take_quiz, name='take_quiz'),
    
    # Рейтинг
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    path('create-course/', views.create_course, name='create_course'),
    
    path('course/<int:course_id>/add-lesson/', views.add_lesson, name='add_lesson'),
    
    # ВОТ ЗДЕСЬ НЕ ХВАТАЛО ЗАПЯТОЙ В КОНЦЕ 👇
    path('rate-rec/<int:course_id>/', views.rate_recommendation, name='rate_recommendation'),
    
    path('api/search/', views.api_search_courses, name='api_search_courses'),
    
    path('certificate/<int:certificate_id>/', views.view_certificate, name='view_certificate'),
    
    # 🔥 НОВЫЙ ПУТЬ: Конструктор тестов для конкретного урока (НА САЙТЕ)
    path('lesson/<int:lesson_id>/builder/', views.lesson_builder, name='lesson_builder'),
]