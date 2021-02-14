A Temperatura da sua Playlist
===========


O Projeto a seguir sugere playlists com base na temperatura de determinada cidade. Link do desafio: https://gist.github.com/ceolinrenato/f3a0357c9d9037f7dc9248c93d39859e


## Instalação

```bash
    $ virtualenv env                        # Crie um ambiente virtual
    $ source env/bin/activate               # Ative seu ambiente virtual
    (env) $ pip install -r requirements.txt # instale suas dependências
```

## No primeiro acesso

```bash
    (env) $ python manage.py makemigrations
    (env) $ python manage.py migrate
```

## Start

```bash
    (env) $ python manage.py runserver
```