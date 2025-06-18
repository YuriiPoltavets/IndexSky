from flask import Flask

from routes.index_routes import index_bp
from routes.fetch_routes import fetch_bp

app = Flask(__name__)

app.register_blueprint(index_bp)
app.register_blueprint(fetch_bp)

if __name__ == '__main__':
    app.run(debug=True)
