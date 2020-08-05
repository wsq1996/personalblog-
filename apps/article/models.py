from datetime import datetime

from exts import db

class Article_type(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    type_name = db.Column(db.String(20),nullable=False)
    articles = db.relationship('Article',backref='article_type')

class Article(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(50),nullable=False)
    content = db.Column(db.BLOB,nullable=False)
    pdatetime = db.Column(db.DateTime,default=datetime.now )
    clickNum = db.Column(db.Integer,default=0)
    saveNum = db.Column(db.Integer,default=0)
    love = db.Column(db.Integer,default=0)
    userId = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    comments = db.relationship('Comment',backref='articles')
    type_id =db.Column(db.Integer,db.ForeignKey('article_type.id'))

class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    comment = db.Column(db.String(255),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    article = db.Column(db.Integer,db.ForeignKey('article.id'))
    cdatetime = db.Column(db.DateTime,default=datetime.now )

    def __str__(self):
        return self.comment