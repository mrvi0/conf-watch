# ConfWatch 🔍

[English](../../README.md) | [Русский](README.md)

---

## Что такое ConfWatch?

ConfWatch — это инструмент для мониторинга изменений в конфигурационных файлах, ведения истории версий и быстрого отката.

### 🚀 Быстрая установка

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/conf-watch/main/install.sh | bash
```

Установщик автоматически определит подходящую версию:
- **Python-версия** (если есть Python 3.8+) — с web-интерфейсом и расширенными возможностями
- **Bash-версия** (если Python не найден) — легковесная, без зависимостей

### 🧠 Основные возможности

- Мониторинг любых файлов (например, `.bashrc`, `.env`, `/etc/nginx/nginx.conf`)
- Хранение истории изменений (Git или SQLite)
- Просмотр diff между версиями
- Откат к любой версии
- Уведомления (Telegram, email)
- Веб-интерфейс для визуализации изменений
- Теги версий, автотесты, шифрование

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
│       └── api.sh            # API сервер
├── docs/
│   ├── ru/
│   │   └── README.md
│   └── en/
├── install.sh                 # Умный установщик
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

### 🖥️ Web-интерфейс

**Bash-версия:**
```bash
cd ~/.confwatch/web
./api.sh
# Открыть в браузере: http://localhost:8080
```

**Python-версия:**
```bash
confwatch web
# Открыть в браузере: http://localhost:5000
```

### 🔍 Примеры команд

```bash
confwatch snapshot ~/.bashrc      # Снять снапшот файла
confwatch diff ~/.bashrc          # Показать различия
confwatch history ~/.bashrc       # История изменений
confwatch rollback ~/.bashrc 2    # Откат к версии
confwatchd start                  # Запустить демон
```

### 📄 Лицензия

Проект распространяется под лицензией MIT — см. файл [LICENSE](../../LICENSE). 