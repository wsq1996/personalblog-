from flask import Blueprint, request, g, redirect, url_for, render_template, session, jsonify

from apps.article.models import Article, Comment, Article_type
from apps.user.models import User
from apps.utils.utils import user_type
from exts import db

article_bp = Blueprint('article',__name__,url_prefix='/article')


#自定义过滤器
@article_bp.app_template_filter('cdecodedetail')
def content_decode(content):
    content = content.decode('utf-8')
    return content

# 发布文章
@article_bp.route('/publish',methods=['GET','POST'])
def publish_article():
    if request.method == 'POST':
        title = request.form.get('title')
        type_id = request.form.get('type')
        content = request.form.get('content')
        article = Article()
        article.title = title
        article.type_id = type_id
        article.content = content.encode('utf-8')
        article.userId = g.user.id
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('user/user_center.html')

# 文章详情页
@article_bp.route('detail')
def article_detail():
    article_id = request.args.get('aid')
    article = Article.query.get(article_id)
    article.clickNum += 1
    db.session.commit()
    popular_article = Article.query.order_by(-Article.clickNum).all()[:10]
    type_ = Article_type.query.filter(Article_type.id == article.type_id).all()
    user , types = user_type()
    page = int(request.args.get('page', 1))
    comments = Comment.query.filter(Comment.article == article_id).order_by(-Comment.cdatetime).paginate(page=page,per_page=5)

    return render_template('article/detail.html',comments=comments,article=article,user=user,types=types,type=type_,popular_article=popular_article)


# 收藏
@article_bp.route('/save')
def article_save():
    article_id = request.args.get('aid')
    tag = request.args.get('tag')
    article = Article.query.get(article_id)

    if tag == '1':
        article.saveNum -= 1
        if article.saveNum <= 0:
            article.saveNum = 0
    else:
        article.saveNum += 1
    return jsonify(num=article.saveNum)

# 文章点赞
@article_bp.route('/love')
def article_love():
    article_id = request.args.get('aid')
    tag = request.args.get('tag')
    article = Article.query.get(article_id)

    if tag == '1':
        article.love -= 1
        if article.love <= 0:
            article.love = 0
    else:
        article.love += 1
    return jsonify(num=article.love)


# 文章评论
@article_bp.route('/add_comment',methods=['GET','POST'])
def article_comment():
    user, types = user_type()
    if request.method == 'POST':
        comment_content = request.form.get('comment')
        article_id = request.form.get('aid')
        comment = Comment()
        user_id = session.get('uid')
        comment.comment = comment_content
        comment.user_id = user_id
        comment.article = article_id
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('article.article_detail')+'?aid='+article_id)
    return redirect(url_for('user.index'))

# 文章类型显示
@article_bp.route('/article_type')
def articleType():
    tid = request.args.get('tid',1)
    types = Article_type.query.all()
    tagType = Article_type.query.get(tid)
    # 登录用户
    user = None
    user_id = session.get('uid', None)
    if user_id:
        user = User.query.get(user_id)
    #分页
    page = int(request.args.get('page',1))
    articles = Article.query.filter(Article.type_id == tid).paginate(page=page,per_page=8)
    popular_article = Article.query.order_by(-Article.clickNum).all()[:10]
    params = {
        'user' : user,
        'types' : types,
        'articles' : articles,
        'tid' : tid,
        'popular_article':popular_article,
        'tagType':tagType,
    }
    return render_template('article/article_type.html',**params)

