# Tg Test Bot

Telegram бот, выполененный в качестве тестового задания.
Ознакомиться можно [тут](https://t.me/testask321_bot) (uptime='По возможности')

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Новости

В качестве источника новостей используется сайт [Rambler](https://news.rambler.ru/rss/).

## Погода

В качестве источника погоды используется [Open Weather Map API](https://openweathermap.org/api).
API key указывается в config.json файле.

## Шутки

Источник шуток сайт [Rzhunemogu](http://rzhunemogu.ru/RandJSON.aspx?CType=1)
Некоторые шутки могут неккоректо обрабатываться из-за некорректного формирования json на стороне сайта
Такие исключения обрабатываются и отправляется новый запрос.


## БД
В качестве ORM используется SQLAlchemy. В качестве адаптера используется asyncpg.
Ссылка для соедениения указывается в config.json файле:

```bash
postgresql+asyncpg://username:password@ip:port/database
```

В базе данных сохраняются данные о пользователе:
* Telegram ID
* Telegram username
* Текущая комманда пользователя
* Город для погоды
    * И/ИЛИ
* Координаты для погоды
