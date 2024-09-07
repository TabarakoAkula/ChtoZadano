workers = 3
bind = "0.0.0.0:8000"
chdir = "/code/"
module = "chtozadano.wsgi:application"

accesslog = "/code/chtozadano/logs/gunicorn_access.log"
errorlog = "/code/chtozadano/logs/gunicorn_error.log"

loglevel = "info"
