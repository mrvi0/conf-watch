# ConfWatch 🔍

[English](../../README.md) | [Русский](README.md)

---

## Что такое ConfWatch?

ConfWatch — это мощный инструмент для мониторинга изменений в конфигурационных файлах системы, ведения истории версий и обеспечения простого отката к предыдущим версиям.

### 🚀 Быстрая установка

```bash
# Установка одной командой
curl -fsSL https://raw.githubusercontent.com/yourusername/conf-watch/main/install.sh | bash
```

Установщик автоматически определит вашу систему и установит подходящую версию:
- **Python версия** (если доступен Python 3.8+) - Полнофункциональная с веб-интерфейсом
- **Bash версия** (запасной вариант) - Легковесная, без зависимостей

### 🧠 Ключевые возможности

- **📁 Мониторинг файлов**: Автоматически отслеживает изменения в конфигурационных файлах (`.bashrc`, `/etc/nginx/nginx.conf`, `.env`, `~/.config/`, и т.д.)
- **💾 История версий**: Сохраняет каждую версию в SQLite или Git репозитории
- **🔍 Просмотр различий**: Показывает различия между версиями с подсветкой синтаксиса
- **↩️ Откат**: Легко вернуться к предыдущим версиям
- **🔔 Уведомления**: Опциональные оповещения через Telegram, email и другие каналы
- **🏷️ Тегирование версий**: Помечайте снапшоты осмысленными комментариями
- **🔒 Шифрование**: Безопасное хранение для чувствительных конфигурационных данных
- **🌐 Веб-интерфейс**: Красивый веб-интерфейс для управления конфигурациями
- **🔄 Синхронизация**: Синхронизация истории между несколькими машинами

### 🧪 Как это работает

#### 1. Сканирование
ConfWatch периодически сканирует указанные пути файлов на предмет изменений:

```yaml
watch:
  - ~/.bashrc
  - ~/.config/nvim/init.vim
  - /etc/nginx/nginx.conf
  - ~/projects/.env
```

#### 2. Обнаружение изменений
Каждый файл хешируется (SHA256) и сравнивается с предыдущей версией. Если хеш изменяется, сохраняется новая копия.

#### 3. Варианты хранения
- **Git репозиторий**: Простое сравнение, встроенная история, возможности синхронизации
- **SQLite база данных**: Простой встроенный формат, легкая веб-интеграция, поддержка сжатия

### 🚀 Быстрый старт

#### Установка

**Вариант 1: Установка одной командой (Рекомендуется)**
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/conf-watch/main/install.sh | bash
```

**Вариант 2: Ручная установка**
```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/conf-watch.git
cd conf-watch

# Запустить установщик
./install.sh
```

Установщик автоматически выберет лучшую версию для вашей системы:
- **Python версия**: Полнофункциональная с веб-интерфейсом, уведомлениями, шифрованием
- **Bash версия**: Легковесная, работает везде, без зависимостей

#### Базовое использование

```bash
# Создать начальный снапшот
confwatch snapshot

# Просмотр различий
confwatch diff ~/.bashrc

# Пометить версию тегом
confwatch tag ~/.bashrc "после установки nvm"

# Запустить демон мониторинга
confwatchd --config ~/confwatch.yml
```

### 📋 Конфигурация

Создайте `~/.confwatch/config.yml`:

```yaml
# Файлы для мониторинга
watch:
  - ~/.bashrc
  - ~/.zshrc
  - ~/.config/nvim/init.vim
  - /etc/nginx/nginx.conf
  - ~/projects/.env

# Настройки хранения
storage:
  type: "sqlite"  # или "git"
  path: "~/.confwatch/database.db"

# Настройки уведомлений
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"

# Настройки мониторинга
monitoring:
  interval: 300  # секунды
  auto_test:
    nginx: "nginx -t"
    apache: "apache2ctl configtest"
```

### 🔍 Примеры использования

#### Ручной режим
```bash
# Создать снапшот
confwatch snapshot

# Просмотр различий
confwatch diff /etc/hosts

# Список всех версий
confwatch history ~/.bashrc

# Откат к предыдущей версии
confwatch rollback ~/.bashrc --version 3
```

#### Режим демона
```bash
# Запустить демон мониторинга
confwatchd --config ~/confwatch.yml

# Проверить статус демона
confwatchd status

# Остановить демон
confwatchd stop
```

### 🎯 Продвинутые функции

#### Тегирование версий
```bash
# Пометить текущую версию
confwatch tag ~/.bashrc "после установки nodejs"

# Список тегов
confwatch tags ~/.bashrc

# Откат к помеченной версии
confwatch rollback ~/.bashrc --tag "после установки nodejs"
```

#### Автотестирование конфигураций
```bash
# Тест конфигурации nginx после изменений
confwatch auto-test nginx

# Тест конфигурации apache
confwatch auto-test apache
```

#### Шифрование
```bash
# Включить шифрование для чувствительных файлов
confwatch encrypt ~/.env

# Расшифровать для просмотра
confwatch decrypt ~/.env
```

### 🌐 Веб-интерфейс

**Bash версия:**
```bash
# Запустить веб-сервер
confwatch web
# Открыть в браузере: http://localhost:8080
```

**Python версия:**
```bash
confwatch web
# Открыть в браузере: http://localhost:5000
```

### 📦 Структура проекта

```
conf-watch/
├── python/                    # Python-версия (полная)
│   ├── confwatch/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── scanner.py
│   │   │   ├── storage.py
│   │   │   └── diff.py
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── daemon/
│   │   └── web/
│   ├── tests/
│   └── requirements.txt
├── bash/                      # Bash-версия (легкая)
│   ├── confwatch             # Основной скрипт
│   ├── confwatchd            # Демон
│   └── web/
│       ├── index.html        # Веб-интерфейс
│       └── webserver.sh      # Веб-сервер
├── docs/
│   ├── ru/
│   │   └── README.md
│   └── en/
├── install.sh                 # Умный установщик
├── uninstall.sh              # Скрипт удаления

├── LICENSE                    # Лицензия MIT
└── README.md
```

### 🔧 Установка вручную

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/conf-watch.git
cd conf-watch
./install.sh
```

### 📄 Лицензия

Проект распространяется под лицензией MIT — см. файл [LICENSE](../../LICENSE). 