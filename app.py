from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from osirisvalidator.string import not_blank, is_alnum_space
from osirisvalidator.internet import valid_email
from osirisvalidator.intl.br import valid_cpf
from osirisvalidator.exceptions import ValidationException

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/example.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)

    def __init__(self, json):
        if json is None:
            return

        self.username = json['username'] if 'username' in json else None
        self.email = json['email'] if 'email' in json else None
        self.cpf = json['cpf'] if 'cpf' in json else None

    @validates('username')
    @not_blank(field='username')
    @is_alnum_space(field='username')
    def validate_username(self, key, username):
        return username

    @validates('email')
    @not_blank(field='email')
    @valid_email(field='email', message='email deve ser válido!')
    def validate_email(self, key, email):
        return email

    @validates('cpf')
    @not_blank(field='cpf')
    @valid_cpf(field='cpf', message='cpf deve ser válido')
    def validate_cpf(self, key, cpf):
        return cpf

    def __repr__(self):
        return '<User %r>' % self.username


db.drop_all()
db.create_all()


@app.route('/api/User', methods=['POST'])
def saveuser():
    try:
        user = User(request.get_json())
        db.session.add(user)
        db.session.commit()
    except ValidationException as ve:
        return jsonify({"status": 400, "message": "erro de validação!", "errors": ve.errors}), 400

    return jsonify(user)


if __name__ == '__main__':
    app.run()
