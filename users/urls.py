from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import UserLoginForm

urlpatterns = [
    # 1. ГЛАВНАЯ СТРАНИЦА (Самое важное добавление!)
    # Если адрес пустой, запускаем функцию index (она решит: Лендинг или Профиль)
    path('', views.index, name='index'),

    # 2. Регистрация и выход
    path('register/', views.register, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('logout/', views.logout_view, name='logout'),

    # 3. Логин (вход)
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        authentication_form=UserLoginForm
    ), name='login'), 

    # 4. Профиль пользователя
    path('profile/', views.profile, name='profile'),
    
    path('about/', views.about, name='about'),
    
    path('blog/', views.blog_list, name='blog'),
    
    path('blog/<slug:post_slug>/', views.blog_detail, name='blog_detail'),
    
    path('support/', views.support_ticket, name='support_ticket'),
    
    # --- СОЦИАЛЬНАЯ СЕТЬ (ПРОФИЛИ, ДРУЗЬЯ И ЧАТ) ---
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    
    # Новые пути для заявок в друзья
    path('friend/request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('friend/accept/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend/remove/<str:username>/', views.remove_friend, name='remove_friend'),
    
    # Мессенджер
    path('friends/', views.friends_and_chat, name='friends_page'),
    path('friends/<str:username>/', views.friends_and_chat, name='friends_chat'),
    
    path('api/messages/<str:username>/', views.get_messages, name='get_messages_api'),
]