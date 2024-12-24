from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128), unique=True, nullable=False)
    model_used = db.Column(db.String(128), nullable=False)
    # Other fields...

    def __init__(self, session_id, model_used):
        self.session_id = session_id
        self.model_used = model_used