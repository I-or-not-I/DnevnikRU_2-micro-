
# DnevnikRU_2(micro)
Telegram бот для работы с сайтом dnevnik.ru (для учеников): просмотр оценок, дз и т.д.


## Важно
Проект написан с использованием микросервисной архитектуры.


## Ссылка на бота

[Dnevn1k_ru_bot](https://t.me/Dnevn1k_ru_bot)
(летом работать не будет :sob:)


## Авторы
- [@I-or-not-I](https://www.github.com/I-or-not-I)


## Инструкция по сборке проекта в Docker

### 1. Создание файлов окружения
Перед сборкой Docker-образа необходимо создать два файла с переменными окружения.

#### 1.1. `.env.tg_bot`
Содержит настройки для Telegram бота:
```bash
TOKEN="ваш_токен_бота"
```

#### 1.2. `.env.controller`
Содержит настройки для подключения к базе данных:
```bash
DB_DATA='{
"database": "название базы данных", 
"user": "имя пользователя", 
"password": "пароль", 
"host": "ваш хост (0.0.0.0)", 
"port": "ваш порт (5432)"
}'
```

### 2. Сборка и запуск контейнеров

#### 2.1. Соберите образы:
```bash
docker-compose build
```

#### 2.2. Запустите контейнеры:
```bash
docker-compose up -d
```

#### 2.3. Для остановки:
```bash
docker-compose down
```

### 3. Проверка работы

#### 3.1. Убедитесь, что контейнеры запущены:
```bash
docker-compose ps
```

#### 3.2. Просмотр логов:
```bash
docker-compose logs 'name' (controller, tg_bot, dnevnik_ru_pars)
```


## Ссылки
[![MIT License](https://img.shields.io/badge/tg-Ruslan_Ririchenko-0088cc.svg)](https://t.me/kirichenko_ruslan)

