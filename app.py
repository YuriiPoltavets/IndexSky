from flask import Flask

from services.metrics_cache import reset_cache_if_stale

from routes.index_routes import index_bp
from routes.fetch_routes import fetch_bp

app = Flask(__name__)

# Clear outdated metrics cache on startup
reset_cache_if_stale()

app.register_blueprint(index_bp)
app.register_blueprint(fetch_bp)

if __name__ == '__main__':
    app.run(debug=True)
