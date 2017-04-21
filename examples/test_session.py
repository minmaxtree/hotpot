from hotpot import Hotpot, session, redirect, url_for, escape, request
import os

app = Hotpot(__name__)

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <body>
            <form method="post">
                <p><input type=text name=username>
                <p><input type=submit value=Login>
            </form>
        </body>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key. keep this really secret:

if __name__ == '__main__':
    app.secret_key = os.urandom(32)
    app.run()

