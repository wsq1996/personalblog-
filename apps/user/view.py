import os

from flask import Blueprint, render_template, request, session, g, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from apps.article.models import Article, Article_type
from apps.user.models import User
from apps.utils.utils import user_type
from exts import db, cache
from settings import Config

user_bp = Blueprint('user', __name__, url_prefix='/user')
required_login_list = ['/user/center',
                       '/user/change',
                       '/article/publish',
                       '/article/add_comment', ]


# 钩子函数
@user_bp.before_app_request
def before_request():
    print('before_app_request', request.path)
    user, types = user_type()
    if request.path in required_login_list:
        id = session.get('uid')
        if not id:
            return render_template('user/login.html', user=user, types=types)
        else:
            user = User.query.get(id)
            g.user = user


# 自定义过滤器
@user_bp.app_template_filter('cdecodeindex')
def content_decode(content):
    content = content.decode('utf-8')
    return content[:100]


# 给首页缓存保留时间
@cache.cached(timeout=50)
@user_bp.route('/')
def index():
    # session 获取
    user, types = user_type()
    # 获取文章列表并分页
    page = int(request.args.get('page', 1))
    lastarticle = Article.query.order_by(-Article.pdatetime).first()

    popular_article = Article.query.order_by(-Article.clickNum).all()[:10]

    search = request.args.get('search', '')
    if search:
        pagination = Article.query.filter(Article.title.contains(search)).order_by(-Article.pdatetime).paginate(
            page=page, per_page=8)
    else:
        pagination = Article.query.order_by(-Article.pdatetime).paginate(page=page, per_page=8)
    params = {
        'user': user,
        'types': types,
        'pagination': pagination,
        'search': search,
        'lastarticle': lastarticle,
        'popular_article': popular_article,
    }

    return render_template('user/index.html', **params)


# 注册
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    user, types = user_type()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        email = request.form.get('email')
        if repassword == password:
            user = User()
            user.username = username
            user.password = generate_password_hash(password)
            user.phone = phone
            user.email = email
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('user.index'))
        else:
            return render_template('user/register.html', msg='两次密码不一致', types=types)
    return render_template('user/register.html', types=types)


# 登录
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    types = Article_type.query.all()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users = User.query.filter(User.email == email).all()

        for user in users:
            flag = check_password_hash(user.password, password)
            if flag:
                # 用session机制记录用户登录状态
                session['uid'] = user.id
                return redirect(url_for('user.index'))
        else:
            return render_template('user/login.html', types=types, msg='用户名或者密码有误！请重新输入')
    return render_template('user/login.html', types=types)


# 退出登录
@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.index'))


# 个人中心
@user_bp.route('/center', methods=['GET', 'POST'])
def user_center():
    types = Article_type.query.all()
    return render_template('user/user_center.html', user=g.user, types=types)


# 个人信息修改
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']


@user_bp.route('/change', methods=['GET', 'POST'])
def user_change():
    types = Article_type.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        icon = request.files.get('icon')

        icon_name = icon.filename
        suffix = icon_name.rsplit('.')[-1]
        if suffix in ALLOWED_EXTENSIONS:
            icon_name = secure_filename(icon_name)
            file_path = os.path.join(Config.UPLOAD_ICON_DIR, icon_name)
            icon.save(file_path)
            user = g.user
            user.username = username
            user.phone = phone
            user.email = email
            path = 'upload/icon'
            user.icon = os.path.join(path, icon_name)
            print('----------', user.icon)
            db.session.commit()
            return redirect(url_for('user.user_center', types=types))
        else:
            return render_template('user/user_center.html', types=types, user=g.user, msg='扩展格式有误！')

    return render_template('user/user_center.html', types=types, user=g.user)


# 个人简历
# @user_bp.route('/aboutme')
# def about_me():
#     return render_template('user/aboutme.html')
