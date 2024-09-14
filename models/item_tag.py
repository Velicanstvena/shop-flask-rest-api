from db import db

class ItemTagModel(db.Model):
    __tablename__ = 'item_tag'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))