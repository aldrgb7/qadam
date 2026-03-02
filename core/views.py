from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count  # Обязательно добавляем Count для подсчета популярности
from courses.models import Course, LessonProgress

User = get_user_model()

def index(request):
    """ 
    Главная страница сайта (Дашборд).
    """
    if not request.user.is_authenticated:
        return render(request, 'landing.html')

    user = request.user
    
    # 1. РАСЧЕТ РАНГА И XP
    max_xp = 10000
    current_xp = getattr(user, 'xp', 0)
    xp_percent = int((current_xp / max_xp) * 100) if max_xp > 0 else 100
    if xp_percent > 100: xp_percent = 100
    
    if current_xp < 500: rank_name = "Новичок (Intern)"
    elif current_xp < 2000: rank_name = "Младший (Junior)"
    elif current_xp < 5000: rank_name = "Средний (Middle)"
    else: rank_name = "Сеньор (Senior)"

    # 2. АКТИВНЫЕ КУРСЫ
    enrolled_course_ids = LessonProgress.objects.filter(
        user=user
    ).values_list('lesson__course_id', flat=True).distinct()

    started_courses = Course.objects.filter(id__in=enrolled_course_ids)
    active_courses_stats = []
    completed_courses_count = 0

    for course in started_courses:
        total = course.lessons.count()
        if total == 0: 
            continue
            
        completed = LessonProgress.objects.filter(
            user=user, 
            lesson__course=course, 
            is_completed=True
        ).count()
        
        percent = int((completed / total) * 100) if total > 0 else 0
        
        course_data = {
            'title': course.title,
            'icon_class': getattr(course, 'icon_class', 'fa-solid fa-code'), 
            'level': course.get_level_display() if hasattr(course, 'get_level_display') else 'Базовый',
            'description': course.description,
            'percent': percent,
            'total': total,
            'completed': completed,
            'id': course.id,
            'image': course.image if hasattr(course, 'image') and course.image else None
        }

        if percent == 100:
            completed_courses_count += 1
            
        active_courses_stats.append(course_data)

    # ==========================================
    # 3. УМНЫЕ РЕКОМЕНДАЦИИ (ТЕМА 28: ML + ПРАВИЛА)
    # ==========================================
    recommended_courses = []
    
    # Шаг А: Собираем "Датасет" интересов пользователя (ID категорий пройденных курсов)
    history_categories = LessonProgress.objects.filter(
        user=user, 
        is_completed=True,
        lesson__course__category__isnull=False
    ).values_list('lesson__course__category_id', flat=True)

    # Шаг Б: Контентная фильтрация (Content-Based)
    if history_categories:
        recommended_courses = Course.objects.filter(
            status='published',
            category_id__in=history_categories
        ).exclude(
            id__in=enrolled_course_ids # Убираем те, что он уже проходит
        ).distinct()[:3]
    
    # Шаг В: Решение проблемы "Холодного старта" (Fallback Rule)
    # Если юзер новый (нет истории) или прошел всё в своих категориях
    if not recommended_courses:
        recommended_courses = Course.objects.filter(
            status='published'
        ).exclude(
            id__in=enrolled_course_ids
        ).annotate(
            # Считаем уникальных студентов в каждом курсе
            students_count=Count('lessons__lessonprogress__user', distinct=True)
        ).order_by('-students_count')[:3] # Рекомендуем топ самых популярных

    # Если база совсем пустая, берем просто последние добавленные
    if not recommended_courses:
         recommended_courses = Course.objects.filter(status='published').exclude(id__in=enrolled_course_ids).order_by('-created_at')[:3]

    # 4. ТОП-5 ЛИДЕРОВ
    top_users = User.objects.order_by('-xp')[:5] if hasattr(User, 'xp') else []

    # 5. СТАТИСТИКА
    total_completed_lessons = LessonProgress.objects.filter(user=user, is_completed=True).count()

    context = {
        'rank_name': rank_name,
        'current_xp': current_xp,
        'max_xp': max_xp,
        'xp_percent': xp_percent,
        
        'active_courses': active_courses_stats,
        
        # Передаем УМНЫЕ рекомендации вместо старых
        'courses': recommended_courses, 
        
        'top_users': top_users,
        'stats': {
            'completed_lessons': total_completed_lessons,
            'completed_courses': completed_courses_count,
            'hours': 12, 
            'streak': 1 
        }
    }
    return render(request, 'index.html', context)