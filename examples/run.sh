fname=$1
echo $fname
uwsgi/uwsgi --http :7777 --wsgi-file $fname --callable app
