# Bot for a car rental company
Django + python-telegram-bot + Celery + Redis + Postgres + Dokku + GitHub Actions. Telegram bot with database, admin panel and a bunch of useful built-in methods.

## Features

* Database: Postgres
* Admin panel (thanks to [Django](https://docs.djangoproject.com/en/3.1/intro/tutorial01/))
* Background jobs using [Celery](https://docs.celeryproject.org/en/stable/)
* Deployment using [Dokku](https://dokku.com)
* Telegram API usage in pooling or [webhook mode](https://core.telegram.org/bots/api#setwebhook)
