from flask import Flask, render_template, request, url_for, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
import os
import io
from sqlalchemy_utils import get_class_by_table
import copy
from sqlalchemy.orm.session import make_transient

# notre serveur flask
app = Flask(__name__,
            static_url_path='',
            static_folder='.',
            template_folder='.'
            )
# lien serveur <-> base de donnees
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

# notre login manager
login_manager = LoginManager()
login_manager.init_app(app)

# notre base de données
db = SQLAlchemy()
db.init_app(app)

# notre classe pour nos utilisateurs
class User(UserMixin, db.Model):
    #__tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    preferedcity = db.Column(db.String(250), nullable=True)
    lastitinerary = db.Column(db.String(250), nullable=True)

# necessaire pour cette base créée "à la volée"
with app.app_context() as context:
    db.create_all()

# indispensable sinon la base ne peut pas être utilisée en consultation
@login_manager.user_loader
def loader_user(user_id):
    return db.session.get(User, user_id) #User.query.get(user_id)

# un exemple de fonction qui demande tous les utilisateurs
def load_all_users():
    return db.session.query(User).all()

# un exemple fictif de route qui ajoute un utilisateur et ensuite les montre tous dans un html
@app.route("/admin/")
def admin():
    user = User(username="rene"+os.urandom(12).hex(),password="coty", preferedcity = "test", lastitinerary="test")
    db.session.add(user)
    db.session.commit()
    users = load_all_users()
    return render_template("admin.html", userlist=users)

# on lance notre serveur
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=80)


### Deplacer, décommenter et appeler (à la main ou sur une route specifique) si besoin de supprimer du contenu
# def delete_all_users():
#     meta = db.metadata
#     for table in reversed(meta.sorted_tables):
#         print ('Clear table %s', table)
#         db.session.execute(table.delete())
#         db.session.commit()
#
#
# def delete_all_tables():
#     db.drop_all()
#     db.session.commit()
