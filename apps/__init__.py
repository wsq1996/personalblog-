from flask import Flask

from apps.article.view import article_bp
from apps.user.view import user_bp
from exts import db
from settings import DevelopmentConfig


def create_app():
    app = Flask(__name__,template_folder='../templates',static_folder='../static')
    app.config.from_object(DevelopmentConfig)
    db.init_app(app=app)
    app.register_blueprint(article_bp)
    app.register_blueprint(user_bp)
    return app