from hotpot import Hotpot, request, make_response

app = Hotpot(__name__)

@app.route('/')
def index():
    return '''
    <html>
        <body>
            <form action="/setcookie" method="POST">
                <p><h3>Enter userID</h3></p>
                <p><input type='text' name='nm' /></p>
                <p><input type='submit' value='Login' /></p>
            </form>
        </body>
    </html>
    '''

@app.route('/setcookie', methods=['POST', 'GET'])
def setcookie():
    if request.method == 'POST':
        user = request.form['nm']
        resp = make_response('''
            <html>
            <h1>Cookie 'userID' is set</h1>
            <a href='/getcookie'>Click here to read cookie</a>
            </html>
        ''')
        resp.set_cookie('userID', user, max_age=3600)
        return resp

@app.route('/getcookie')
def getcookie():
    print "request.cookies is:", request.cookies
    name = request.cookies.get('userID')
    return '<h1>welcom ' + name + '</h1>'

if __name__ == '__main__':
    app.run()
