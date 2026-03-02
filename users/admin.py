from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PlatformAuthor # <--- Жаңа модельді импорттадық
from .models import BlogPost

class CustomUserAdmin(UserAdmin):
    """
    Админкада қолданушыларды басқаруды баптаймыз.
    Standard UserAdmin-ді мұрагерлікке аламыз, бірақ өзіміздің өрістерді қосамыз.
    """
    model = CustomUser
    
    # Тізімде (таблицада) көрінетін бағандар
    list_display = ('username', 'email', 'phone_number', 'role', 'xp', 'is_staff')
    
    # 🔥 СУПЕР-ФИШКА: Тізімнің өзінен рөлді ауыстыруға мүмкіндік береді!
    list_editable = ('role',)
    
    # Фильтрлер (оң жақтағы панель)
    list_filter = ('role', 'is_staff', 'is_active')
    
    # Іздеу өрістері (email, телефон және аты бойынша іздеу)
    search_fields = ('username', 'email', 'phone_number')
    
    # Реттеу (алдымен жаңалар)
    ordering = ('-date_joined',)

    # Қолданушыны өңдеу (редактирование) бетіндегі өрістер тобы
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Жеке деректер', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role')}),
        ('Прогресс (Геймификация)', {'fields': ('xp', 'level')}),
        ('Құқықтар', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Маңызды күндер', {'fields': ('last_login', 'date_joined')}),
    )

# Модельді тіркейміз
admin.site.register(CustomUser, CustomUserAdmin)


# ==========================================
# "О НАС" БЕТІНЕ АРНАЛҒАН АВТОР МОДЕЛІН ТІРКЕУ
# ==========================================
@admin.register(PlatformAuthor)
class PlatformAuthorAdmin(admin.ModelAdmin):
    """
    'О нас' бетіндегі автордың ақпаратын басқару.
    """
    list_display = ('name', 'role')
    
    # Тек 1 ғана жазба (автор) болуы үшін, егер базада мәлімет бар болса, "Қосу (Add)" түймесін жасырамыз
    def has_add_permission(self, request):
        if PlatformAuthor.objects.exists():
            return False
        return True
    
    
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'views')
    search_fields = ('title', 'content')
    list_filter = ('category', 'created_at')
    # Эта фишка автоматически заполняет ссылку (slug) на основе заголовка!
    prepopulated_fields = {'slug': ('title',)}