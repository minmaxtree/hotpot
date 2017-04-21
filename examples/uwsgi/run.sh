./uwsgi --http :9888 --wsgi-file main.py

./uwsgi --http :7777 --wsgi-file app.py --callable app -H UWSGI

