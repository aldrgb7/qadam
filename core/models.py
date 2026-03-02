from django.db import models
from django.utils import timezone

# Модель для Новостей
class News(models.Model):
    TAG_CHOICES = (
        ('update', 'Обновление'),
        ('platform', 'Платформа'),
        ('event', 'Событие'),
    )
    
    title = models.CharField("Заголовок", max_length=200)
    tag = models.CharField("Тэг", max_length=20, choices=TAG_CHOICES, default='platform')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at'] # Сначала свежие


# Модель для Событий (Вебинары, Дедлайны)
class Event(models.Model):
    title = models.CharField("Название", max_length=200)
    description = models.CharField("Описание (например: 18:00 • Онлайн)", max_length=200)
    date = models.DateTimeField("Дата и время события")
    
    # Цвет фона даты (для красоты: синий или красный)
    is_urgent = models.BooleanField("Срочное? (Красный цвет)", default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ['date'] # Сначала ближайшие