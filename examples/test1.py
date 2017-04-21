from hotpot import Hotpot

app = Hotpot(__name__)

@app.route("/")
def hello():
    return "hello..."

if __name__ == "__main__":
    app.run()
