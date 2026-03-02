from django.contrib import admin
from .models import (
    Course, Lesson, LessonProgress, Quiz, Question, Choice, 
    Review, Category, RecommendationFeedback, Certificate, LessonComment
)

# --- 1. КАТЕГОРИИ ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'slug')
    prepopulated_fields = {'slug': ('name',)} 
    search_fields = ('name',)

# --- 2. ВАРИАНТЫ ОТВЕТОВ (Внутри вопроса) ---
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3 
    fields = ('text', 'is_correct')

# --- 3. ВОПРОСЫ И ОТВЕТЫ ВНУТРИ ТЕСТА (Объединяем!) ---
# Мы оставляем инлайн вопросов для Теста, 
# но саму регистрацию Вопросов как отдельной страницы убираем из главного меню,
# чтобы не путаться.
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    # Это позволит редактировать вопросы прямо в тесте
    show_change_link = True 

# --- 4. ТЕСТ ВНУТРИ УРОКА ---
class QuizInline(admin.StackedInline):
    model = Quiz
    extra = 1
    max_num = 1 
    show_change_link = True

# --- 5. УРОКИ ВНУТРИ КУРСА ---
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('order', 'title', 'video_url') 
    show_change_link = True

# --- ОСНОВНАЯ РЕГИСТРАЦИЯ ---

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'level', 'created_at')
    list_filter = ('status', 'level', 'category', 'author')
    search_fields = ('title', 'description')
    inlines = [LessonInline] # Из курса прыгаем в уроки

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'course')
    list_filter = ('course',)
    search_fields = ('title',)
    inlines = [QuizInline] # Из урока прыгаем в тест

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'xp_reward')
    # Самое важное: теперь вопросы создаются ПРЯМО ТУТ
    inlines = [QuestionInline] 

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Мы регистрируем вопросы, чтобы работали ChoiceInline, 
    но в главном списке админки Jazzmin их можно скрыть, 
    если они тебе мешают.
    """
    list_display = ('text', 'quiz', 'order')
    inlines = [ChoiceInline] # В вопросе сразу видим ответы

# --- ОСТАЛЬНОЕ ---
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'rating', 'created_at')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'track_number', 'issued_at')

@admin.register(LessonComment)
class LessonCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'created_at')

@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'is_helpful')