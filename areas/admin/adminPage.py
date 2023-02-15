from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app
from flask_security import roles_accepted, auth_required, hash_password
from flask_login import current_user

from model import Role, User
from forms import new_user_form

adminBluePrint = Blueprint('admin', __name__)

@adminBluePrint.route("/adminpage", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin")
def adminpage():
    listOfUsers = [u for u in User.query.all() if u.email != current_user.email]
    if request.method == 'POST':
        current_app.security.datastore.delete_user(current_app.security.datastore.find_user(email=request.form['user']))
        current_app.security.datastore.db.session.commit()
        flash('User Deleted')
        return redirect(url_for('admin.adminpage'))
    return render_template("admin/adminpage.html", listOfUsers=listOfUsers)

@adminBluePrint.route("/register", methods=['GET', 'POST'])
@auth_required()
@roles_accepted("Admin")
def register():
    form = new_user_form()
    roles = Role.query.all()
    form.role.choices = [(r.name, r.name) for r in roles]
    if form.validate_on_submit():
        if not current_app.security.datastore.find_user(email=form.email.data):
            current_app.security.datastore.create_user(email=form.email.data, password=hash_password(form.password.data), roles=[form.role.data])
            current_app.security.datastore.db.session.commit()
            flash('User Registered')
            return redirect(url_for('admin.adminpage'))
        else:
            form.email.errors += ('Email is already in use',)
    return render_template("admin/new_user.html", form=form)