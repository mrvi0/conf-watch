# ConfWatch Web Server

## Запуск веб-сервера

После установки ConfWatch у вас есть несколько вариантов запуска веб-сервера:

### 1. Python3 HTTP Server (рекомендуется)
```bash
cd ~/.confwatch/web
./test_server.sh
```
Этот вариант использует встроенный HTTP сервер Python3 и работает наиболее стабильно.

### 2. Bash API Server
```bash
cd ~/.confwatch/web
./api.sh
```
Полнофункциональный Bash-сервер с API для работы с ConfWatch.

### 3. Простой Bash Server
```bash
cd ~/.confwatch/web
./simple_api.sh
```
Упрощенная версия Bash-сервера.

### 4. Минимальный Bash Server
```bash
cd ~/.confwatch/web
./minimal_api.sh
```
Минимальная версия для тестирования.

## Доступ к веб-интерфейсу

После запуска сервера откройте в браузере:
- http://localhost:8080

## API Endpoints

- `GET /` - Веб-интерфейс
- `GET /api/files` - Список отслеживаемых файлов
- `GET /api/diff?file=~/.bashrc` - Показать различия для файла
- `GET /api/history?file=~/.bashrc` - История изменений файла
- `POST /api/snapshot` - Создать снимок файла

## Устранение проблем

Если порт 8080 занят, измените порт:
```bash
PORT=8081 ./test_server.sh
```

Если netcat не работает, используйте Python3 версию:
```bash
./test_server.sh
``` 