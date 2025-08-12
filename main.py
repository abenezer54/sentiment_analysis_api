import eventlet
eventlet.monkey_patch()

import os
from flask import Flask
from celery import Celery
from config import config


def create_celery(app):
    """Create and configure Celery instance"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Create Celery instance
    celery = create_celery(app)
    app.celery = celery
    
    return app

# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
