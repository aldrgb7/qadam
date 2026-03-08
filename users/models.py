from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # ... твои старые поля (role, phone_number, avatar, xp, level) ...

    # 🔥 НОВЫЕ ПОЛЯ ДЛЯ СТАТУСА 🔥
    is_online = models.BooleanField(default=False, verbose_name='В сети')
    last_seen = models.DateTimeField(blank=True, null=True, verbose_name='Был(а) в сети')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    # Роли пользователя
    ROLE_CHOICES = (
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    )
    
    # Основные поля
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='student', 
        verbose_name='Роль'
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name='Номер телефона'
    )

    # --- НОВОЕ ПОЛЕ: АВАТАРКА ---
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name='Аватарка'
    )
    
    # Поля для геймификации (только для студентов)
    xp = models.IntegerField(default=0, verbose_name='Опыт (XP)')
    level = models.CharField(max_length=50, default='Junior', verbose_name='Уровень')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # Простые проверки
    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    
# users/models.py (ВСТАВИТЬ В КОНЕЦ)

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Студент")
    item_name = models.CharField(max_length=100, verbose_name="Товар")
    price = models.IntegerField(verbose_name="Цена (XP)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата покупки")
    is_delivered = models.BooleanField(default=False, verbose_name="Выдано?")

    def __str__(self):
        return f"{self.user.username} - {self.item_name}"

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки в магазине"
        
        
class PlatformAuthor(models.Model):
    """Модель для хранения информации об авторе на странице 'О нас'"""
    name = models.CharField(max_length=100, verbose_name="Имя автора", default="Aldiyar")
    role = models.CharField(max_length=100, verbose_name="Роль/Должность", default="Founder & Lead Developer")
    # Вот это поле позволит загружать картинку:
    avatar = models.ImageField(upload_to='author_avatars/', verbose_name="Фото автора", blank=True, null=True)
    bio = models.TextField(verbose_name="Биография")
    
    # Ссылки на соцсети (необязательные)
    github_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на GitHub")
    telegram_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на Telegram")
    instagram_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на Instagram")

    class Meta:
        verbose_name = "Информация об авторе"
        verbose_name_plural = "Информация об авторе"

    def __str__(self):
        return f"Автор: {self.name}"

    # Этот трюк гарантирует, что будет существовать только ОДНА запись об авторе.
    # Если попытаться создать вторую, она перезапишет первую.
    def save(self, *args, **kwargs):
        if not self.pk and PlatformAuthor.objects.exists():
            # Если объект еще не сохранен, но в базе уже что-то есть,
            # мы удаляем старое перед сохранением нового.
            PlatformAuthor.objects.all().delete()
        super(PlatformAuthor, self).save(*args, **kwargs)
        
        
class BlogPost(models.Model):
    """Модель для статей в Блоге"""
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    # Slug нужен для красивых ссылок (например: /blog/how-to-learn-python/)
    slug = models.SlugField(unique=True, verbose_name="URL (ссылка)")
    category = models.CharField(max_length=50, verbose_name="Категория", default="IT-новости")
    image = models.ImageField(upload_to='blog_images/', verbose_name="Обложка статьи", blank=True, null=True)
    content = models.TextField(verbose_name="Текст статьи")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Блог (Статьи)"
        ordering = ['-created_at'] # Свежие статьи будут сверху

    def __str__(self):
        return self.title
    
    
# ==========================================
# СОЦИАЛЬНАЯ СЕТЬ (ДРУЗЬЯ И СООБЩЕНИЯ)
# ==========================================

class Friendship(models.Model):
    """Модель для добавления в друзья (заявки и взаимная дружба)"""
    
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'В друзьях'),
    )
    
    from_user = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE, verbose_name='Кто отправил')
    to_user = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE, verbose_name='Кому отправили')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        verbose_name = 'Заявка/Друг'
        verbose_name_plural = 'Друзья (Заявки и связи)'

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.get_status_display()})"


class Message(models.Model):
    """Модель для личных сообщений (Чата)"""
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Сообщения сортируются по времени
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f"От {self.sender.username} к {self.receiver.username}"