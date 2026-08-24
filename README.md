# GameVerse

A personal game journal & catalog app — track games you've played, write reviews, save favorite quotes and characters, and build a personal showcase.

*Персональный дневник-каталог игр — отмечайте пройденные игры, пишите обзоры, сохраняйте любимые цитаты и персонажей, собирайте личную витрину.*

---

## 🇬🇧 English

### Tech Stack
- **Backend:** Django, PostgreSQL
- **Frontend:** Bootstrap, custom dark glassmorphism theme
- **Planned:** Django REST Framework, Docker

### Architecture
The project is split into two apps around a core design principle: **world data vs. personal data**.

- `catalog` — reference data that exists independently of any user: `Game`, `Genre`, `Character`, `Quest`
- `journal` — data tied to a specific user's experience: `UserExperience`, `Screenshot`, `FavoriteQuote`, `FavoriteCharacter`, `Comment`

### Features
- Full CRUD for journal entries, with class-based views and author-only permission mixins
- Screenshot and favorite-quote management via inline formsets with atomic saves
- Auto-generated slugs (`unidecode` + `slugify`) for all catalog entities
- Authentication: registration, login/logout, password change/reset (Gmail SMTP)
- Django admin with chained M2M dropdowns (`django-smart-selects`)
- Protected relations (`on_delete=PROTECT`) to preserve data integrity

### Status / Roadmap
✅ Catalog & journal CRUD, auth flow, admin UX, core templates
🚧 In progress: user profiles
📋 Planned (v2): social features (visibility, cross-user comments), automatic Metacritic fetch, search, showcase ordering, Docker/deploy

---

## 🇷🇺 Русский

### Стек
- **Backend:** Django, PostgreSQL
- **Frontend:** Bootstrap, кастомная тёмная glassmorphism-тема
- **В планах:** Django REST Framework, Docker

### Архитектура
Проект разделён на два приложения по принципу **мировые/справочные данные vs. персональные данные**.

- `catalog` — данные, существующие независимо от пользователя: `Game`, `Genre`, `Character`, `Quest`
- `journal` — данные, привязанные к опыту конкретного пользователя: `UserExperience`, `Screenshot`, `FavoriteQuote`, `FavoriteCharacter`, `Comment`

### Функционал
- Полный CRUD для записей дневника через class-based views с миксинами прав доступа
- Управление скриншотами и избранными цитатами через inline formsets с атомарным сохранением
- Автогенерация slug (`unidecode` + `slugify`) для всех сущностей каталога
- Аутентификация: регистрация, вход/выход, смена/сброс пароля (Gmail SMTP)
- Django admin с зависимыми M2M-полями (`django-smart-selects`)
- Защищённые связи (`on_delete=PROTECT`) для целостности данных

### Статус / Roadmap
✅ CRUD каталога и дневника, аутентификация, UX админки, базовые шаблоны
🚧 В процессе: профили пользователей
📋 Запланировано (v2): социальные функции (видимость постов, комментарии других пользователей), автоматическая подгрузка данных с Metacritic, поиск, сортировка витрины, Docker/деплой