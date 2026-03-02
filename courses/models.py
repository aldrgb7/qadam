import re
from django.db import models
from django.conf import settings
import uuid # <-- НОВЫЙ ИМПОРТ ДЛЯ ТРЕК-НОМЕРОВ

# --- НОВАЯ МОДЕЛЬ ДЛЯ КАТЕГОРИЙ (Для правил алгоритма) ---
class Category(models.Model):
    name = models.CharField("Название категории", max_length=100)
    slug = models.SlugField("URL-метка", unique=True, blank=True)
    icon = models.CharField("Иконка (FontAwesome)", max_length=50, blank=True, default="fa-solid fa-code")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Course(models.Model):
    LEVEL_CHOICES = (
        ('Easy', 'Easy (Легкий)'),
        ('Medium', 'Medium (Средний)'),
        ('Hard', 'Hard (Сложный)'),
    )

    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('review', 'На проверке'),
        ('published', 'Опубликовано'),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Автор (Преподаватель)", 
        null=True, 
        blank=True
    )
    
    # СВЯЗЬ КУРСА С КАТЕГОРИЕЙ
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Категория",
        related_name='courses'
    )

    title = models.CharField("Название курса", max_length=200)
    description = models.TextField("Описание", max_length=500)
    
    image = models.ImageField(
        "Обложка курса", 
        upload_to='course_covers/', 
        null=True, 
        blank=True,
        help_text="Загрузите картинку (желательно 16:9)"
    )
    
    icon_class = models.CharField("Иконка (FontAwesome)", max_length=50, default='fa-solid fa-book')
    
    level = models.CharField("Сложность", max_length=10, choices=LEVEL_CHOICES, default='Easy')
    status = models.CharField("Статус", max_length=15, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Курс")
    title = models.CharField("Название урока", max_length=200)
    description = models.TextField("Описание урока", blank=True)
    video_url = models.URLField("Ссылка на видео (YouTube)", blank=True)
    order = models.PositiveIntegerField("Порядковый номер", default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def get_video_id(self):
        if not self.video_url:
            return None
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', self.video_url)
        if match:
            return match.group(1)
        return None

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['order'] 


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Студент")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Урок")
    is_completed = models.BooleanField(default=False, verbose_name="Пройдено")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата завершения")

    class Meta:
        verbose_name = "Прогресс урока"
        verbose_name_plural = "Прогресс уроков"
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} -> {self.lesson.title}"


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz', verbose_name="Урок")
    title = models.CharField("Название теста", max_length=200)
    description = models.TextField("Описание", blank=True)
    xp_reward = models.IntegerField("Награда за тест (XP)", default=50)

    def __str__(self):
        return f"Тест: {self.title}"

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name="Тест")
    text = models.CharField("Текст вопроса", max_length=500)
    order = models.IntegerField("Порядок", default=0)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name="Вопрос")
    text = models.CharField("Текст ответа", max_length=200)
    is_correct = models.BooleanField("Правильный ответ", default=False)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"
        
        
class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews', verbose_name="Курс")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Студент")
    
    RATING_CHOICES = [
        (1, '⭐ 1 - Очень плохо'),
        (2, '⭐⭐ 2 - Плохо'),
        (3, '⭐⭐⭐ 3 - Нормально'),
        (4, '⭐⭐⭐⭐ 4 - Хорошо'),
        (5, '⭐⭐⭐⭐⭐ 5 - Отлично'),
    ]
    rating = models.IntegerField("Оценка", choices=RATING_CHOICES, default=5)
    comment = models.TextField("Текст отзыва", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ('course', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.course} ({self.rating}★)"


# --- НОВАЯ МОДЕЛЬ ДЛЯ ТЕМЫ 28: ОЦЕНКА КАЧЕСТВА РЕКОМЕНДАЦИЙ ---
class RecommendationFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Студент")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Рекомендованный курс")
    is_helpful = models.BooleanField("Помогла ли рекомендация?", default=True) # True = Лайк, False = Дизлайк
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Оценка рекомендации"
        verbose_name_plural = "Оценки рекомендаций"
        unique_together = ('user', 'course') # Чтобы нельзя было лайкать один курс 100 раз

    def __str__(self):
        reaction = "👍" if self.is_helpful else "👎"
        return f"{self.user.username} -> {self.course.title} {reaction}"
    
    
# --- НОВАЯ МОДЕЛЬ ДЛЯ СЕРТИФИКАТОВ ---
class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Студент")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")
    
    # Автоматически создаем красивый уникальный ID (например: d3b07384...)
    track_number = models.UUIDField("Трек-номер", default=uuid.uuid4, editable=False, unique=True)
    issued_at = models.DateTimeField("Дата выдачи", auto_now_add=True)

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        # Один пользователь может получить только один сертификат за один конкретный курс
        unique_together = ('user', 'course')

    def get_short_track(self):
        # Делаем красивый короткий номер для дизайна (например: QADAM-D3B07)
        return f"QADAM-{str(self.track_number)[:5].upper()}"

    def __str__(self):
        return f"Сертификат: {self.user.username} - {self.course.title}"
    
    
# --- НОВАЯ МОДЕЛЬ: КОММЕНТАРИИ К УРОКУ ---
class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments', verbose_name="Урок")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    text = models.TextField("Текст комментария")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий к уроку"
        verbose_name_plural = "Комментарии к урокам"
        ordering = ['-created_at'] # Новые сверху

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"