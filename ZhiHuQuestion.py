from flask import Flask, render_template, request, redirect, session, url_for
import config
from exts import db
from models import User, Question, Comment
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by(Question.create_time.desc()).all()
    }
    return render_template('index.html', **context)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter_by(telephone=telephone, password=password).first()
        if user:
            session['user_id'] = user.id
            # session.permanent = True
            return redirect(url_for('index'))
        else:
            return '帐号或密码错误，请重新登陆！'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password')

        # 手机号码验证
        user = User.query.filter_by(telephone=telephone).first()
        if user:
            return '该手机号已经注册，请重新注册！'
        else:
            user = User(telephone=telephone, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/question', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title, content=content)
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>', methods=['GET', 'POST'])
def detail(question_id):
    question = Question.query.filter_by(id=question_id).first()
    return render_template('detail.html', question=question)

@app.route('/comment/<question_id>', methods=['POST'])
def comment(question_id):
    content = request.form.get('comment_content')
    comment = Comment(content=content)
    question = Question.query.filter_by(id=question_id).first()
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    comment.author = user
    comment.question = question
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        if user:
            return {'user': user}
    return {}

if __name__ == '__main__':
    app.run()
