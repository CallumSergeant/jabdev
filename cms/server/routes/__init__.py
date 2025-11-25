from flask import Blueprint

def register_routes(app, db):
    """Register all route blueprints"""
    from .subjects import create_subjects_blueprint
    from .levels import create_levels_blueprint
    from .papers import create_papers_blueprint
    from .upload import create_upload_blueprint
    from .publish import create_publish_blueprint
    from .structure import create_structure_blueprint
    
    app.register_blueprint(create_subjects_blueprint(db))
    app.register_blueprint(create_levels_blueprint(db))
    app.register_blueprint(create_papers_blueprint(db))
    app.register_blueprint(create_upload_blueprint(db))
    app.register_blueprint(create_publish_blueprint(db))
    app.register_blueprint(create_structure_blueprint(db))
