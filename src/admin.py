from wtforms import form, fields, validators, PasswordField
from flask_admin.contrib.sqla.fields import QuerySelectField
import flask_admin as admin
import flask_login as login
from flask_admin.contrib.sqla import ModelView
from flask import redirect, request, url_for
from flask_admin import helpers, expose, Admin

from src.models.model import *
import re


def get_user_options():
    return User.query.filter_by(id=login.current_user.id).all()


def get_options(class_name):
    return class_name.query.filter_by(user_id=login.current_user.id).all()


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    username = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_password(self, password):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password_hash, password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(username=self.username.data).first()


class RegistrationForm(form.Form):
    username = fields.StringField(validators=[validators.required()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.required(), validators.length(min=4, max=25,
                                                                                         message="Password length "
                                                                                                 "must be between 4 "
                                                                                                 "and 25 characters")])

    def validate_username(self, username):
        if db.session.query(User).filter_by(username=username.data).count() > 0:
            raise validators.ValidationError('Username already exists. Please provide different one.')

    def validate_email(self, email):
        if db.session.query(User).filter_by(email=email.data).count() > 0:
            raise validators.ValidationError('Email already exists. Please provide different one.')


# Create customized model view class
class MyUserView(ModelView):
    can_export = True
    can_set_page_size = True
    page_size = 20
    export_columns = None

    def is_accessible(self):
        return login.current_user.is_authenticated


class MyOwnerView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.is_admin()


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            if user:
                login.login_user(user)
            # else:
            # return login.user_unauthorized

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        # return super(MyAdminIndexView, self).index()
        return super(MyAdminIndexView, self).render("admin/login.html")

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password_hash = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        # return super(MyAdminIndexView, self).index()
        return super(MyAdminIndexView, self).render("admin/signup.html")

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


class UserView(MyOwnerView):
    can_create = True
    can_delete = True
    can_edit = True
    form_excluded_columns = ("password_hash", "token")

    form_extra_fields = {
        'password': PasswordField('Password')
    }

    form_columns = ("username", "email", "password", "admin")
    column_list = ("username", "email", "admin")

    def _handle_view(self, name, **kwargs):
        if not login.current_user.is_authenticated:
            return redirect(url_for("admin.login_view"))

    def on_model_change(self, form, User, is_created):
        if form.password.data is not None:
            User.set_password(form.password.data)


class RestaurantView(MyOwnerView):
    can_delete = can_create = can_edit = True
    column_editable_list = ("user", "name", "address", "landmark")

    form_excluded_columns = ("recipes", "menu_card")

    def _handle_view(self, name, **kwargs):
        if not login.current_user.is_authenticated:
            return redirect(url_for("admin.login_view"))


class IngredientsView(MyOwnerView):
    can_delete = can_create = can_edit = True

    # column_editable_list = ("user", "name", "address", "landmark")
    #
    form_excluded_columns = ("recipe_ingredient")

    def _handle_view(self, name, **kwargs):
        if not login.current_user.is_authenticated:
            return redirect(url_for("admin.login_view"))


class RecipesView(MyOwnerView):
    can_delete = can_create = can_edit = True

    # column_editable_list = ("user", "name", "address", "landmark")
    #
    form_excluded_columns = ("recipe_ingredient", "menu_card_recipes")

    def _handle_view(self, name, **kwargs):
        if not login.current_user.is_authenticated:
            return redirect(url_for("admin.login_view"))


class RecipeIngredientView(MyOwnerView):
    can_delete = can_create = can_edit = True

    # column_editable_list = ("user", "name", "address", "landmark")
    #
    # form_excluded_columns = ("recipes", "menu_card")

    def _handle_view(self, name, **kwargs):
        if not login.current_user.is_authenticated:
            return redirect(url_for("admin.login_view"))


class MenuCardView(MyOwnerView):
    can_delete = can_create = can_edit = True

    # column_editable_list = ("user", "name", "address", "landmark")
    #
    form_excluded_columns = ("menu_card_recipes")

    def _handle_view(self, name, **kwargs):
        if not login.current_user.is_authenticated:
            return redirect(url_for("admin.login_view"))


class MenuCardRecipesView(MyOwnerView):
    can_delete = can_create = can_edit = True

    # column_editable_list = ("user", "name", "address", "landmark")
    #
    # form_excluded_columns = ("recipes", "menu_card")

    def _handle_view(self, name, **kwargs):
        if not login.current_user.is_authenticated:
            return redirect(url_for("admin.login_view"))


admin = Admin(name='Restaurant', index_view=MyAdminIndexView(), base_template='my_master.html',
              template_mode='bootstrap3')
