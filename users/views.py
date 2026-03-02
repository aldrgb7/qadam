import random
import re
from collections import Counter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse

# Импортируем все нужные модели курсов и сертификаты
from courses.models import LessonProgress, Course, Lesson, Certificate

from .forms import CustomUserCreationForm, EmailVerificationForm, UserUpdateForm
from .models import PlatformAuthor, CustomUser, BlogPost, Friendship, Message

User = get_user_model()

def index(request):
    """ Главная страница (Дашборд). """
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
        if total == 0: continue 
            
        completed = LessonProgress.objects.filter(
            user=user, lesson__course=course, is_completed=True
        ).count()
        
        percent = int((completed / total) * 100) if total > 0 else 0
        
        if percent == 100:
            completed_courses_count += 1
        else:
            active_courses_stats.append({
                'title': course.title,
                'icon_class': getattr(course, 'icon_class', 'fa-solid fa-code'), 
                'level': course.get_level_display() if hasattr(course, 'get_level_display') else 'Базовый',
                'description': course.description,
                'percent': percent,
                'total': total,
                'completed': completed,
                'id': course.id,
                'image': course.image if hasattr(course, 'image') and course.image else None
            })

    # 3. РЕКОМЕНДАЦИИ (ML)
    if started_courses.exists():
        history_text = " ".join([f"{c.title} {c.description}" for c in started_courses]).lower()
        words = re.findall(r'\w+', history_text)
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'это', 'как', 'курс', 'мы', 'о', 'об'}
        user_keywords = [w for w in words if w not in stop_words and len(w) > 3]
        user_profile = Counter(user_keywords)

        available_courses = Course.objects.filter(status='published').exclude(id__in=enrolled_course_ids)
        course_scores = []
        for course in available_courses:
            score = 0
            course_text = f"{course.title} {course.description}".lower()
            course_words = set(re.findall(r'\w+', course_text))
            for word, weight in user_profile.items():
                if word in course_words: score += weight
            course_scores.append((score, course))

        course_scores.sort(key=lambda x: x[0], reverse=True)
        recommended_courses = [c[1] for c in course_scores[:4]]
        
        if len(recommended_courses) < 4:
            needed = 4 - len(recommended_courses)
            extra = available_courses.exclude(id__in=[c.id for c in recommended_courses]).order_by('-created_at')[:needed]
            recommended_courses.extend(extra)
    else:
        recommended_courses = Course.objects.filter(status='published').order_by('-created_at')[:4]

    top_users = User.objects.order_by('-xp')[:5] if hasattr(User, 'xp') else []
    total_completed_lessons = LessonProgress.objects.filter(user=user, is_completed=True).count()

    context = {
        'rank_name': rank_name, 'current_xp': current_xp, 'max_xp': max_xp, 'xp_percent': xp_percent,
        'active_courses': active_courses_stats, 'courses': recommended_courses, 'top_users': top_users,
        'stats': {'completed_lessons': total_completed_lessons, 'completed_courses': completed_courses_count, 'hours': 12, 'streak': 1}
    }
    return render(request, 'index.html', context)


@login_required
def profile(request):
    """ Личный кабинет пользователя. """
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=user)

    # XP и Ранги
    max_xp = 10000
    current_xp = getattr(user, 'xp', 0)
    xp_percent = int((current_xp / max_xp) * 100) if max_xp > 0 else 100
    if xp_percent > 100: xp_percent = 100
    
    if current_xp < 500: rank_name = "Новичок (Intern)"
    elif current_xp < 2000: rank_name = "Младший (Junior)"
    elif current_xp < 5000: rank_name = "Средний (Middle)"
    else: rank_name = "Сеньор (Senior)"

    # Активные курсы
    enrolled_course_ids = LessonProgress.objects.filter(
        user=user
    ).values_list('lesson__course_id', flat=True).distinct()
    
    started_courses = Course.objects.filter(id__in=enrolled_course_ids)
    active_courses_stats = [] 

    for course in started_courses:
        total = course.lessons.count()
        completed = LessonProgress.objects.filter(user=user, lesson__course=course, is_completed=True).count()
        percent = int((completed / total) * 100) if total > 0 else 0
        
        if percent < 100:
            active_courses_stats.append({
                'title': course.title, 
                'icon': getattr(course, 'icon_class', 'fa-solid fa-code'), 
                'percent': percent, 
                'completed': completed,
                'total': total,
                'id': course.id
            })

    # Готовые СЕРТИФИКАТЫ
    completed_courses = Certificate.objects.filter(user=user).select_related('course').order_by('-issued_at')

    # Курсы ПРЕПОДАВАТЕЛЯ
    teacher_courses_raw = Course.objects.filter(author=user).order_by('-created_at')
    teacher_courses = []
    
    for c in teacher_courses_raw:
        lessons_count = c.lessons.count()
        students_count = LessonProgress.objects.filter(lesson__course=c).values('user').distinct().count()
        
        teacher_courses.append({
            'id': c.id,
            'title': c.title,
            'status': c.status,
            'total_lessons': lessons_count,
            'students_count': students_count
        })

    # Друзья
    friendships = Friendship.objects.filter(Q(from_user=user) | Q(to_user=user), status='accepted')
    friends, seen_ids = [], set()
    for f in friendships:
        friend_obj = f.to_user if f.from_user == user else f.from_user
        if friend_obj.id not in seen_ids:
            friends.append(friend_obj)
            seen_ids.add(friend_obj.id)

    context = {
        'form': form, 'xp_percent': round(xp_percent), 'max_xp': max_xp, 'current_xp': current_xp,
        'rank_name': rank_name, 
        'active_courses': active_courses_stats, 
        'completed_courses': completed_courses, 
        'teacher_courses': teacher_courses,
        'friends': friends, 
        
        'shop_items': [
            {'name': 'Худи QADAM', 'price': 10000, 'icon': 'fa-solid fa-shirt', 'color': '#10b981'},
            {'name': 'Рюкзак для ноутбука', 'price': 9500, 'icon': 'fa-solid fa-suitcase', 'color': '#333'},
            {'name': 'Наушники QADAM Pro', 'price': 9000, 'icon': 'fa-solid fa-headphones', 'color': '#3b82f6'},
            {'name': 'Powerbank 20k mAh', 'price': 7500, 'icon': 'fa-solid fa-battery-full', 'color': '#14b8a6'},
            {'name': 'Термос QADAM', 'price': 4000, 'icon': 'fa-solid fa-bottle-water', 'color': '#0d6efd'},
            {'name': 'Фирменная кружка', 'price': 2000, 'icon': 'fa-solid fa-mug-hot', 'color': '#ef4444'},
            {'name': 'Коврик для мыши', 'price': 1500, 'icon': 'fa-solid fa-computer-mouse', 'color': '#8b5cf6'},
            {'name': 'Набор стикеров', 'price': 500, 'icon': 'fa-solid fa-note-sticky', 'color': '#ec4899'},
        ]
    }
    return render(request, 'users/profile.html', context)

@login_required
def public_profile(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user: return redirect('profile')

    current_xp = getattr(target_user, 'xp', 0)
    rank_name = "Новичок" if current_xp < 500 else "Младший" if current_xp < 2000 else "Средний" if current_xp < 5000 else "Сеньор"

    friendship = Friendship.objects.filter(Q(from_user=request.user, to_user=target_user) | Q(from_user=target_user, to_user=request.user)).first()
    rel_status = 'none'
    if friendship:
        if friendship.status == 'accepted': rel_status = 'friends'
        elif friendship.from_user == request.user: rel_status = 'request_sent'
        else: rel_status = 'request_received'

    return render(request, 'users/public_profile.html', {'target_user': target_user, 'rank_name': rank_name, 'current_xp': current_xp, 'rel_status': rel_status})

@login_required
def friends_and_chat(request, username=None):
    search_query = request.GET.get('q', '').strip()
    search_results = User.objects.filter(Q(username__icontains=search_query) | Q(first_name__icontains=search_query)).exclude(id=request.user.id)[:10] if search_query else []

    friendships = Friendship.objects.filter(Q(from_user=request.user) | Q(to_user=request.user), status='accepted').select_related('from_user', 'to_user')
    friends, seen_ids = [], set()
    for f in friendships:
        friend_obj = f.to_user if f.from_user == request.user else f.from_user
        if friend_obj.id not in seen_ids:
            friends.append(friend_obj)
            seen_ids.add(friend_obj.id)

    incoming_requests = Friendship.objects.filter(to_user=request.user, status='pending').select_related('from_user')
    active_user, messages_list = None, []
    
    if username:
        active_user = get_object_or_404(User, username=username)
        if request.method == 'POST':
            text = request.POST.get('text', '').strip()
            if text: Message.objects.create(sender=request.user, receiver=active_user, text=text)
            return redirect('friends_chat', username=username)

        messages_list = Message.objects.filter((Q(sender=request.user) & Q(receiver=active_user)) | (Q(sender=active_user) & Q(receiver=request.user))).order_by('created_at')
        messages_list.filter(receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'users/friends_chat.html', {'friends': friends, 'incoming_requests': incoming_requests, 'search_results': search_results, 'search_query': search_query, 'active_user': active_user, 'messages_list': messages_list})

@login_required
def send_friend_request(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user != request.user:
        if not Friendship.objects.filter(Q(from_user=request.user, to_user=target_user) | Q(from_user=target_user, to_user=request.user)).exists():
            Friendship.objects.create(from_user=request.user, to_user=target_user, status='pending')
            messages.success(request, 'Заявка отправлена!')
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def accept_friend_request(request, username):
    target_user = get_object_or_404(User, username=username)
    req = Friendship.objects.filter(from_user=target_user, to_user=request.user, status='pending').first()
    if req:
        req.status = 'accepted'
        req.save()
        messages.success(request, f'Вы теперь друзья с {target_user.username}!')
    return redirect(request.META.get('HTTP_REFERER', 'friends_page'))

@login_required
def remove_friend(request, username):
    target_user = get_object_or_404(User, username=username)
    Friendship.objects.filter(Q(from_user=request.user, to_user=target_user) | Q(from_user=target_user, to_user=request.user)).delete()
    messages.success(request, 'Связь удалена.')
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def get_messages(request, username):
    other_user = get_object_or_404(User, username=username)
    msgs = Message.objects.filter((Q(sender=request.user) & Q(receiver=other_user)) | (Q(sender=other_user) & Q(receiver=request.user))).order_by('created_at')
    msgs.filter(receiver=request.user, is_read=False).update(is_read=True)
    results = [{'sender': m.sender.username, 'text': m.text, 'time': m.created_at.strftime("%H:%M"), 'is_me': m.sender == request.user} for m in msgs]
    return JsonResponse({'messages': results})

# ==========================================
# 🔥 НОВАЯ МГНОВЕННАЯ РЕГИСТРАЦИЯ 🔥
# ==========================================

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя, но пока не коммитим в базу
            user = form.save(commit=False)
            user.is_active = True  # Мгновенно активируем аккаунт!
            user.role = request.POST.get('role', 'student') # Устанавливаем роль (если она передается)
            user.save()
            
            # Автоматически логиним пользователя
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Перенаправляем сразу на дашборд (индексную страницу)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'users/register.html', {'form': form})

def verify_email(request):
    # Эта функция больше не нужна, но мы оставляем заглушку, 
    # чтобы сайт не сломался, если в urls.py остался путь к ней.
    # Если кто-то сюда попадет - его просто перекинет на главную.
    return redirect('index')

def logout_view(request):
    logout(request)
    return redirect('index')

def about(request):
    return render(request, 'about.html', {
        'total_users': User.objects.count(),
        'total_courses': Course.objects.filter(status='published').count(),
        'total_lessons': Lesson.objects.count(),  
        'author': PlatformAuthor.objects.first()
    })
    
def blog_list(request):
    return render(request, 'blog.html', {'posts': BlogPost.objects.all()})

def blog_detail(request, post_slug):
    post = get_object_or_404(BlogPost, slug=post_slug)
    post.views += 1
    post.save()
    return render(request, 'blog_detail.html', {'post': post})

@login_required
def support_ticket(request):
    if request.method == 'POST': 
        messages.success(request, '🚀 Заявка отправлена!')
    return redirect(request.META.get('HTTP_REFERER', 'index'))