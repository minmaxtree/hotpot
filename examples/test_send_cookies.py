from hotpot import Hotpot, make_response, render_template

app = Hotpot(__name__)

@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    resp.set_cookie('username', 'namenamenn')
    return resp

if __name__ == '__main__':
    app.run()
