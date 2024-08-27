from db import db


class TokenBlockListModel(db.Model):
    __tablename__ = 'token_block_list'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
