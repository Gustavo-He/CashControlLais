from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/cashcontrol'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    telefone = db.Column(db.String(20))
    rg = db.Column(db.String(20))
    cpf = db.Column(db.String(14))
    banco = db.Column(db.String(50))
    agencia = db.Column(db.String(10))
    conta = db.Column(db.String(20))
    senha = db.Column(db.String(30), nullable=False)

@app.route('/')
def index():
    return render_template('Home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Usuario.query.filter_by(email=email, senha=password).first()
        if user:
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            error = 'Credenciais inválidas'
            return render_template('Login.html', error=error)
    return render_template('Login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        telefone = request.form['telefone']
        rg = request.form['rg']
        cpf = request.form['cpf']
        banco = request.form['banco']
        agencia = request.form['agencia']
        conta = request.form['conta']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not (
                username and email and telefone and rg and cpf and banco and agencia and conta and password and confirm_password):
            error = 'Todos os campos são obrigatórios'
            return render_template('Register.html', error=error)

        if password != confirm_password:
            error = 'As senhas não coincidem'
            return render_template('Register.html', error=error)

        new_user = Usuario(nome=username, email=email, telefone=telefone, rg=rg, cpf=cpf, banco=banco, agencia=agencia, conta=conta, senha=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            session['email'] = new_user.email
            return redirect('/dashboard')
        except IntegrityError:
            db.session.rollback()
            error = 'Email já está sendo utilizado'
            return render_template('Register.html', error=error)
    return render_template('Register.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return render_template('Dashboard.html', email=session['email'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/receitas')
def receitas():
    return render_template('Revenues.html')

@app.route('/adicionar_receita', methods=['POST'])
def adicionar_receita():
    if 'email' in session:
        if request.method == 'POST':
            nome = request.form['nome']
            data = request.form['data']
            preco = request.form['preco']
            nova_receita = Receita(nome=nome, data_emissao=data, valor_receitas=preco)
            db.session.add(nova_receita)
            db.session.commit()
            return redirect(url_for('receitas'))
    else:
        return redirect(url_for('login'))

@app.route('/despesas')
def despesas():
    return render_template('Expenses.html')


@app.route('/adicionar_despesa', methods=['POST'])
def adicionar_despesa():
    if 'email' in session:
        if request.method == 'POST':
            nome = request.form['nome']
            data = request.form['data']
            preco = request.form['preco']
            nova_despesa = Despesa(nome=nome, data_emissao=data, valor_despesas=preco)
            db.session.add(nova_despesa)
            db.session.commit()
            return redirect(url_for('despesas'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
