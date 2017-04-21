from hotpot import Hotpot, abort, redirect, url_for

app = Hotpot(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    print "[login]"
    abort(401)
    # ths is never executed

if __name__ == '__main__':
    app.run()
