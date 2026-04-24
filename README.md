# QADAM - Интеллектуалды оқу платформасы

## Сипаттамасы (Description)
QADAM — студенттердің оқуға деген ынтасын арттыру мәселесін шешетін заманауи LMS-платформа. Жоба дербес оқу жоспарын құру үшін жасанды интеллектті (AI) және пайдаланушылардың белсенділігін арттыру үшін геймификацияны (XP жүйесін) пайдаланады.

## Мүмкіндіктері (Features)
- **AI-ұсыныстар:** Студенттерге арналған жеке курстар мен сабақтарды таңдау.
- **QADAM Store:** Жиналған XP ұпайларын нақты сыйлықтарға (мерч) алмастыруға арналған ішкі дүкен.
- **Real-time Чат:** Студенттер мен оқытушылар арасындағы кедергісіз, жылдам байланыс (WebSockets).
- **B2B Дашборд:** Оқу орындарына арналған студенттер үлгерімінің терең аналитикасы.

## Технологиялық стек (Tech Stack)
- **Backend:** Python (Django, Django Channels)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** PostgreSQL
- **Real-time:** WebSockets, Redis

## Орнату (Installation)
```bash
git clone [https://github.com/aldrgb7/qadam.git](https://github.com/aldrgb7/qadam.git)
cd qadam
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
