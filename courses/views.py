from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.db.models import Q, Avg, Count
from django.contrib.auth import get_user_model
from .models import Course, Lesson, LessonProgress, Quiz, Question, Choice, Category, RecommendationFeedback, Certificate, LessonComment
from .forms import ReviewForm, CourseCreateForm, LessonCreateForm, LessonCommentForm
from django.urls import reverse


User = get_user_model()

# ==========================================
# 1. СПИСОК КУРСОВ (КАТАЛОГ)
# ==========================================
def course_list(request):
    # Берем только опубликованные курсы
    courses = Course.objects.filter(status='published').order_by('-created_at')
    
    # Загружаем все категории для вывода в фильтре
    categories = Category.objects.all()

    # 1. Поиск по названию
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # 2. Фильтр по сложности (один уровень)
    level_filter = request.GET.get('level')
    if level_filter:
        courses = courses.filter(level=level_filter)

    # 3. Фильтр по предметам (категориям) - массив чекбоксов
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        courses = courses.filter(category__id__in=selected_categories)

    # ПРОВЕРКА ЗАПИСЕЙ: Собираем ID курсов, где у юзера есть прогресс
    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = LessonProgress.objects.filter(
            user=request.user
        ).values_list('lesson__course_id', flat=True).distinct()

    # Топ пользователей для модального окна
    top_users = User.objects.annotate(
        completed_lessons_count=Count(
            'lessonprogress', 
            filter=Q(lessonprogress__is_completed=True)
        )
    ).filter(xp__gt=0).order_by('-xp')[:15]

    context = {
        'courses': courses,
        'categories': categories, # Передаем категории в HTML
        'selected_categories': [int(c) for c in selected_categories if c.isdigit()], # Для галочек
        'level_choices': Course.LEVEL_CHOICES,
        'selected_level': level_filter, # Для радио-кнопки
        'search_query': query,
        'top_users': top_users,
        'enrolled_course_ids': enrolled_course_ids,
    }
    return render(request, 'courses.html', context)


# ==========================================
# ФУНКЦИЯ ЗАПИСИ НА КУРС
# ==========================================
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    first_lesson = course.lessons.order_by('order').first()

    if not first_lesson:
        messages.error(request, "В этом курсе еще нет уроков.")
        return redirect('course_detail', course_id=course.id)

    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=first_lesson,
        defaults={'is_completed': False}
    )

    if created:
        messages.success(request, f"Вы успешно записались на курс: {course.title}!")
    else:
        messages.info(request, "Вы уже записаны на этот курс.")
        
    return redirect('course_detail', course_id=course.id)


# ==========================================
# 2. ДЕТАЛИ КУРСА
# ==========================================
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.status != 'published':
        if not request.user.is_authenticated or (request.user != course.author and not request.user.is_staff):
            raise Http404("Курс не найден.")

    lessons = course.lessons.all().order_by('order')
    reviews = course.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    form = ReviewForm()
    user_left_review = False
    is_enrolled = False

    if request.user.is_authenticated:
        user_left_review = course.reviews.filter(user=request.user).exists()
        is_enrolled = LessonProgress.objects.filter(user=request.user, lesson__course=course).exists()

        if request.method == 'POST':
            if user_left_review:
                messages.warning(request, 'Вы уже оставили отзыв.')
            else:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.save(commit=False)
                    review.course = course
                    review.user = request.user
                    review.save()
                    messages.success(request, 'Отзыв добавлен!')
                    return redirect('course_detail', course_id=course.id)

    context = {
        'course': course,
        'lessons': lessons,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_form': form,
        'user_left_review': user_left_review,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'course_detail.html', context)


# Не забудь добавить импорт новых моделей и формы в начале файла!
# from .models import ..., LessonComment
# from .forms import ..., LessonCommentForm

# ==========================================
# 3. ПРОСМОТР УРОКА (ТЕОРИЯ + ВИДЕО + КОММЕНТАРИИ)
# ==========================================
@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Получаем прогресс
    progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    is_completed = progress.is_completed if progress else False

    # ИЩЕМ СЛЕДУЮЩИЙ И ПРЕДЫДУЩИЙ УРОК ДЛЯ НАВИГАЦИИ
    next_lesson = course.lessons.filter(order__gt=lesson.order).order_by('order').first()
    prev_lesson = course.lessons.filter(order__lt=lesson.order).order_by('-order').first()

    questions = None
    has_quiz = hasattr(lesson, 'quiz')
    if has_quiz:
        questions = lesson.quiz.questions.all()

    # --- ЛОГИКА КОММЕНТАРИЕВ ---
    comments = lesson.comments.all() # Берем все комменты урока
    
    if request.method == 'POST':
        comment_form = LessonCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.lesson = lesson
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('lesson_detail', course_id=course.id, lesson_id=lesson.id)
    else:
        comment_form = LessonCommentForm()

    context = {
        'course': course,
        'lesson': lesson,
        'is_completed': is_completed, 
        'questions': questions,
        'has_quiz': has_quiz,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
        'comments': comments,          # Передаем комменты
        'comment_form': comment_form,  # Передаем форму
    }
    return render(request, 'lesson_detail.html', context)


# ==========================================
# 4. ЗАВЕРШЕНИЕ УРОКА
# ==========================================
@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    progress, created = LessonProgress.objects.get_or_create(
        user=request.user, 
        lesson=lesson,
        defaults={'is_completed': True}
    )

    if created or not progress.is_completed:
        progress.is_completed = True
        progress.save()
        
        xp_gain = 20
        request.user.xp += xp_gain
        request.user.save()
        messages.success(request, f'Урок завершен! +{xp_gain} XP')
        
        # --- ЛОГИКА ВЫДАЧИ СЕРТИФИКАТА ---
        total_lessons = course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=request.user, 
            lesson__course=course, 
            is_completed=True
        ).count()
        
        if total_lessons > 0 and completed_lessons == total_lessons:
            # Студент прошел все уроки! Проверяем, нет ли уже сертификата
            cert, cert_created = Certificate.objects.get_or_create(
                user=request.user,
                course=course
            )
            if cert_created:
                messages.success(request, f'🎉 ПОЗДРАВЛЯЕМ! Вы прошли курс и получили сертификат!')
    else:
        messages.info(request, 'Урок уже был пройден.')

    return redirect('lesson_detail', course_id=course.id, lesson_id=lesson.id)


# ==========================================
# 5. ТЕСТЫ
# ==========================================
@login_required
def take_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    if not hasattr(lesson, 'quiz'):
        return redirect('lesson_detail', course_id=course.id, lesson_id=lesson.id)

    quiz = lesson.quiz
    if request.method == 'POST':
        score = 0
        total = quiz.questions.count()
        for q in quiz.questions.all():
            ans = request.POST.get(f'question_{q.id}')
            if ans and Choice.objects.get(id=ans).is_correct:
                score += 1
        
        # Если студент набрал хотя бы половину баллов (прошел тест)
        if total > 0 and score >= (total / 2):
            
            # --- Засчитываем урок как пройденный ---
            progress, created = LessonProgress.objects.get_or_create(
                user=request.user, lesson=lesson, defaults={'is_completed': True}
            )
            if not progress.is_completed:
                progress.is_completed = True
                progress.save()
                
            request.user.xp += quiz.xp_reward
            request.user.save()
            messages.success(request, f"Тест пройден! {score}/{total}. +{quiz.xp_reward} XP")
            
            # --- ЛОГИКА ВЫДАЧИ СЕРТИФИКАТА ---
            total_lessons = course.lessons.count()
            completed_lessons = LessonProgress.objects.filter(
                user=request.user, 
                lesson__course=course, 
                is_completed=True
            ).count()
            
            if total_lessons > 0 and completed_lessons == total_lessons:
                cert, cert_created = Certificate.objects.get_or_create(
                    user=request.user, course=course
                )
                if cert_created:
                    messages.success(request, f'🎉 ПОЗДРАВЛЯЕМ! Вы прошли курс и получили сертификат!')
        else:
            messages.warning(request, f"Попробуйте еще раз. Результат: {score}/{total}")
            
        return redirect('lesson_detail', course_id=course.id, lesson_id=lesson.id)

    return render(request, 'quiz.html', {'lesson': lesson, 'quiz': quiz})

# ==========================================
# 6. РЕЙТИНГ
# ==========================================
def leaderboard(request):
    User = get_user_model()
    courses = Course.objects.filter(status='published')
    cid = request.GET.get('course')

    if cid:
        selected_course = get_object_or_404(Course, id=cid)
        top_users = User.objects.annotate(
            completed_in_course=Count(
                'lessonprogress', 
                filter=Q(lessonprogress__lesson__course=selected_course, lessonprogress__is_completed=True)
            )
        ).filter(completed_in_course__gt=0).order_by('-completed_in_course')[:50]
        context_type = 'course'
    else:
        selected_course = None
        top_users = User.objects.filter(xp__gt=0).order_by('-xp')[:50]
        context_type = 'overall'

    context = {
        'top_users': top_users,
        'courses': courses,
        'selected_course': selected_course,
        'context_type': context_type,
    }
    return render(request, 'leaderboard.html', context)


# ==========================================
# 7. СОЗДАНИЕ КУРСА ПРЕПОДАВАТЕЛЕМ
# ==========================================
@login_required
def create_course(request):
    if not request.user.is_teacher:
        messages.error(request, "Только преподаватели могут создавать курсы!")
        return redirect('profile') 

    if request.method == 'POST':
        form = CourseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user 
            course.status = 'review'     
            course.save()
            messages.success(request, "Обложка курса создана! Теперь добавьте уроки.")
            return redirect('add_lesson', course_id=course.id) 
    else:
        form = CourseCreateForm()

    return render(request, 'create_course.html', {'form': form})


# ==========================================
# 8. КОНСТРУКТОР: ДОБАВЛЕНИЕ УРОКА
# ==========================================
@login_required
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.author != request.user:
        messages.error(request, "Вы не можете редактировать чужой курс!")
        return redirect('profile')

    if request.method == 'POST':
        form = LessonCreateForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f"Урок «{lesson.title}» успешно добавлен!")
            return redirect('add_lesson', course_id=course.id)
    else:
        next_order = course.lessons.count() + 1
        form = LessonCreateForm(initial={'order': next_order})

    lessons = course.lessons.all().order_by('order')
    return render(request, 'add_lesson.html', {'form': form, 'course': course, 'lessons': lessons})

# ==========================================
# 9. ОЦЕНКА КАЧЕСТВА РЕКОМЕНДАЦИИ
# ==========================================
@login_required
def rate_recommendation(request, course_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        course = get_object_or_404(Course, id=course_id)
        is_helpful = True if action == 'like' else False
        
        feedback, created = RecommendationFeedback.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={'is_helpful': is_helpful}
        )
        return JsonResponse({'status': 'ok', 'action': action})
    
    return JsonResponse({'status': 'error'}, status=400)


# ==========================================
# 10. УМНЫЙ ПОИСК (API ДЛЯ AJAX)
# ==========================================
def api_search_courses(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) >= 2: # Ищем только если введено 2 и более символа
        courses = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            status='published'
        )[:5] # Берем только топ-5 совпадений для красоты
        
        results = []
        for c in courses:
            results.append({
                'id': c.id,
                'title': c.title,
                'author': c.author.username if c.author else 'QADAM',
                'url': reverse('course_detail', kwargs={'course_id': c.id}), # Генерируем ссылку
                'image': c.image.url if c.image else None,
                'icon': getattr(c, 'icon_class', 'fa-solid fa-book')
            })
        return JsonResponse({'results': results})
        
    return JsonResponse({'results': []})

# ==========================================
# 11. ПРОСМОТР СЕРТИФИКАТА
# ==========================================
def view_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id)
    return render(request, 'certificate.html', {'certificate': cert})


@login_required
def lesson_builder(request, lesson_id):
    """ Фронтенд-конструктор тестов для урока """
    lesson = get_object_or_404(Lesson, id=lesson_id, course__author=request.user)
    
    quiz, created = Quiz.objects.get_or_create(
        lesson=lesson, 
        defaults={'title': f'Тест к уроку: {lesson.title}', 'xp_reward': 50}
    )

    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        
        if question_text:
            question = Question.objects.create(
                quiz=quiz, text=question_text, order=quiz.questions.count() + 1
            )
            correct_choice = request.POST.get('is_correct')

            for i in range(1, 5):
                choice_text = request.POST.get(f'choice_{i}')
                if choice_text:
                    is_correct = str(i) == correct_choice
                    Choice.objects.create(
                        question=question, text=choice_text, is_correct=is_correct
                    )
            
            messages.success(request, 'Вопрос успешно сохранен!')
            
            # 🔥 МАГИЯ ДВУХ КНОПОК 🔥
            action = request.POST.get('action')
            if action == 'save_exit':
                # Если нажали "Сохранить и выйти", кидаем обратно в управление уроками
                return redirect('add_lesson', course_id=lesson.course.id)
            else:
                # Если нажали "Сохранить и добавить еще", перезагружаем эту же страницу
                return redirect('lesson_builder', lesson_id=lesson.id)

    questions = quiz.questions.all().prefetch_related('choices')

    context = {
        'lesson': lesson,
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'courses/lesson_builder.html', context)