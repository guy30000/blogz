from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):#needed that all to creat database and ability to enter 

    id = db.Column(db.Integer, primary_key=True)
    blg_title = db.Column(db.String(120))
    blg_body = db.Column(db.String(120)) #i dont know the max
    ##Part of blogz   keep off until ready
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blg_title, blg_body, owner):
        self.blg_title = blg_title
        self.blg_body = blg_body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def index():
    
    blog = Blog.query.all()
    id=request.args.get('id')
    if id:
        id=(int(id))

        sngl_post=Blog.query.filter(Blog.id==id).first()
        blg_title = sngl_post.blg_title
        blg_body = sngl_post.blg_body
        print(blg_title, blg_body)
        return render_template('blog.html', title=blg_title, blg_body=blg_body)

    return render_template('blog.html',title="Build a Blog", blog=blog)

@app.route('/singleuser', methods=['POST', 'GET'])
def singleuser():
    
    blog = Blog.query.all()
    id=request.args.get('id')
    owner = User.query.filter_by(email=session['email']).first()
    blog = Blog.query.filter_by(owner=owner).all()
    print(owner, owner )
    if id:
        id=(int(id))

        sngl_post=Blog.query.filter(Blog.id==id).first()
        blg_title = sngl_post.blg_title
        blg_body = sngl_post.blg_body
        print(blg_title, blg_body)
        return render_template('singleuser.html', title=blg_title, blg_body=blg_body)

    return render_template('singleuser.html',title="My Blogz", blog=blog)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(email=session['email']).first()



    if request.method == 'POST':
        blg_title = request.form['blg_title']
        blg_body = request.form['blg_body']
        if not blg_body or not blg_title:
            blg_fail =  "You need to fill out both things, guy."
            return render_template('newpost.html', blg_fail=blg_fail, blg_title=blg_title, blg_body=blg_body) 
        #Part of Blogz. Delete this next line when done with it
        #owner_id = ("?") #may als need to remove this v
        new_entry = Blog(blg_title, blg_body, owner)
        db.session.add(new_entry)
        db.session.commit()
        return render_template('blog_entry.html', blog=new_entry)

    return render_template('newpost.html')



##############################################
####################### For Blogz
###User stuff


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            #flash("Logged in")
            #return redirect('/blog')
            return redirect("/blog")#this works
        #else:
            #flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

### End User stuff
##signup
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/blog')
        else:
            # TODO - user better response messaging
            blg_fail = ("Email has already been registered")
            return render_template('signup.html', blg_fail=blg_fail)


    return render_template('signup.html')
##end signup

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()