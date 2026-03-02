from .models import Message, Friendship

def unread_notifications(request):
    """
    Считает непрочитанные сообщения и заявки в друзья 
    для авторизованного пользователя и передает их во все HTML-шаблоны сайта.
    """
    if request.user.is_authenticated:
        # 1. Ищем непрочитанные сообщения
        unread_msgs = Message.objects.filter(
            receiver=request.user, 
            is_read=False
        ).select_related('sender').order_by('-created_at')
        
        # 2. Ищем входящие заявки в друзья
        pending_requests = Friendship.objects.filter(
            to_user=request.user,
            status='pending'
        ).select_related('from_user').order_by('-created_at')

        # Общее количество уведомлений (сообщения + заявки)
        total_count = unread_msgs.count() + pending_requests.count()
        
        return {
            'unread_count': total_count,
            'unread_messages': unread_msgs[:5], 
            'pending_requests': pending_requests[:5], # Передаем 5 последних заявок
        }
    
    # Для неавторизованных возвращаем нули
    return {
        'unread_count': 0, 
        'unread_messages': [],
        'pending_requests': []
    }