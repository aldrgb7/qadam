# QADAM - Интеллектуальная обучающая платформа

## Description
QADAM — это современная LMS-платформа, которая решает проблему потери мотивации у студентов. Проект использует искусственный интеллект для построения персональных образовательных траекторий и геймификацию (XP-систему) для поощрения активности пользователей.

## Features
- **AI-рекомендации:** Индивидуальный подбор курсов.
- **QADAM Store:** Внутренний магазин для обмена заработанных XP на реальный мерч.
- **Real-time Чат:** Общение студентов и преподавателей без задержек (WebSockets).
- **B2B Дашборд:** Глубокая аналитика успеваемости для университетов.

## Tech Stack
- **Backend:** Python (Django, Django Channels)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** PostgreSQL
- **Real-time:** WebSockets, Redis

## Installation
```bash
git clone [https://github.com/aldrgb7/qadam.git](https://github.com/adlrgb7/qadam.git)
cd qadam
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
