import os
from importlib import import_module

Flask = import_module("flask").Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello from Railway! Version 1"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))