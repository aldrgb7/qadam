from django import forms
from .models import Review, Course, Lesson, LessonComment  # <-- Добавили импорт LessonComment

# Твоя старая форма (я её вообще не трогал)
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Что вам понравилось или не понравилось?'
            }),
        }
        labels = {
            'rating': 'Ваша оценка',
            'comment': 'Комментарий',
        }

# --- ФОРМА ДЛЯ ПРЕПОДАВАТЕЛЯ (СОЗДАНИЕ КУРСА) ---
class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'image', 'level']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Python с нуля до Junior'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Кратко опишите, чему научатся студенты...'}),
            'level': forms.Select(attrs={'class': 'form-input'}),
            'image': forms.FileInput(attrs={'class': 'form-input', 'style': 'padding: 10px;'}),
        }

# --- НОВАЯ ФОРМА ДЛЯ ПРЕПОДАВАТЕЛЯ (ДОБАВЛЕНИЕ УРОКА) ---
class LessonCreateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video_url', 'order']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Урок 1. Введение'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Текст урока или конспект...'}),
            'video_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Порядковый номер (1, 2, 3...)'}),
        }

# --- НОВАЯ ФОРМА ДЛЯ КОММЕНТАРИЕВ К УРОКУ ---
class LessonCommentForm(forms.ModelForm):
    class Meta:
        model = LessonComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': '3', 
                'placeholder': 'Задайте вопрос или поделитесь мыслями по уроку...'
            }),
        }
        labels = {
            'text': '', # Скрываем стандартный текст "Text:", чтобы было красивее
        }