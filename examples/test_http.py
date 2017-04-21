from hotpot import Hotpot, request

app = Hotpot(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return "posted it"
    else:
        return "got it"

if __name__ == '__main__':
    app.run()
