from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import defaultdict
import jwt
from sqlalchemy.dialects.postgresql import ARRAY

from ..config import Config
from ..extensions import db


def generate_token(id_):
    return jwt.encode({"user_id": id_, "last_login": datetime.now().strftime("%d-%m-%Y %H:%M:%S")},
                      Config.SECRET_KEY).decode(
        "UTF_8")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), default="Test@123")
    token = db.Column(db.String(512), default="")
    admin = db.Column(db.Boolean(), default=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def is_admin(self):
        return not self.admin

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    def __repr__(self):
        return '<User : {}>'.format(self.username)

    def __init__(self, username="", password=None, email="", is_admin=False, **kwargs):
        db.Model.__init__(self, username=username, email=email, admin=is_admin, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.set_password("Test@123")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def verify_token(self, token):
        return self.token and token in self.token.split(",")

    def remove_token(self, token):
        tokens = self.token.split(",")
        if token in tokens:
            tokens.remove(token)
            self.token = ",".join(tokens)
            return True
        return False


class Restaurant(db.Model):
    restaurant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), index=True, unique=True, nullable=False)
    profile_image = db.Column(db.String(1024))
    address = db.Column(db.String(512), nullable=False)
    branch = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    zip_code = db.Column(db.String(16), nullable=False)
    landmark = db.Column(db.String(128))
    user = db.relationship("User", backref=db.backref("restaurant", cascade="all,delete"))

    def get_owner_id(self):
        return self.user_id

    # Required for administrative interface
    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Restaurant : {}>'.format(self.name)

    def __init__(self, user_id, name, address, landmark, profile_image, branch, city, zip_code, **kwargs):
        self.user_id = user_id
        self.name = name
        self.address = address
        self.landmark = landmark
        self.profile_image = profile_image
        self.branch = branch
        self.city = city
        self.zip_code = zip()


class Ingredients(db.Model):
    ingredient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), index=True, unique=True, nullable=False)
    quantity = db.Column(db.Float, default=0.0)
    calories = db.Column(db.Float, default=0.0)
    total_fat = db.Column(db.Float, default=0.0)
    saturated_fat = db.Column(db.Float, default=0.0)
    trans_fat = db.Column(db.Float, default=0.0)
    cholesterol = db.Column(db.Float, default=0.0)
    sodium = db.Column(db.Float, default=0.0)
    total_carbohydrate = db.Column(db.Float, default=0.0)
    dietary_fiber = db.Column(db.Float, default=0.0)
    total_sugars = db.Column(db.Float, default=0.0)
    protein = db.Column(db.Float, default=0.0)
    vitamin_d = db.Column(db.Float, default=0.0)
    calcium = db.Column(db.Float, default=0.0)
    iron = db.Column(db.Float, default=0.0)
    potassium = db.Column(db.Float, default=0.0)

    def get_ingredient_name(self):
        return self.name

    # Required for administrative interface
    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Ingredient : {}>'.format(self.name)

    def __init__(self, name, quantity, calories, total_fat, saturated_fat, trans_fat, cholesterol, sodium,
                 total_carbohydrate, dietary_fiber, total_sugars, protein, vitamin_d, calcium, iron, potassium,
                 **kwargs):
        self.name = name
        self.quantity = quantity
        self.calories = calories
        self.total_fat = total_fat
        self.saturated_fat = saturated_fat
        self.trans_fat = trans_fat
        self.cholesterol = cholesterol
        self.sodium = sodium
        self.total_carbohydrate = total_carbohydrate
        self.dietary_fiber = dietary_fiber
        self.total_sugars = total_sugars
        self.protein = protein
        self.vitamin_d = vitamin_d
        self.calcium = calcium
        self.iron = iron
        self.potassium = potassium


class Recipes(db.Model):
    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.restaurant_id'), nullable=False)
    name = db.Column(db.String(120), index=True, unique=True, nullable=False)
    image_string = db.Column(db.String(1024))
    # price = db.Column(db.Float, default=0.0)
    type = db.Column(db.String(120), index=True, nullable=False)

    serving_size = db.Column(db.Float, default=0.0)
    serving_unit = db.Column(db.String(120), nullable=False)
    cuisine = db.Column(db.String(120), nullable=False)
    allergy_tag = db.Column(
        db.ARRAY(db.String),
        server_default="{}"
    )

    quantity = db.Column(db.Float, default=0.0)
    calories = db.Column(db.Float, default=0.0)
    total_fat = db.Column(db.Float, default=0.0)
    saturated_fat = db.Column(db.Float, default=0.0)
    trans_fat = db.Column(db.Float, default=0.0)
    cholesterol = db.Column(db.Float, default=0.0)
    sodium = db.Column(db.Float, default=0.0)
    total_carbohydrate = db.Column(db.Float, default=0.0)
    dietary_fiber = db.Column(db.Float, default=0.0)
    total_sugars = db.Column(db.Float, default=0.0)
    protein = db.Column(db.Float, default=0.0)
    vitamin_d = db.Column(db.Float, default=0.0)
    calcium = db.Column(db.Float, default=0.0)
    iron = db.Column(db.Float, default=0.0)
    potassium = db.Column(db.Float, default=0.0)
    restaurant = db.relationship("Restaurant", backref=db.backref("recipes", cascade="all,delete"))

    def get_recipe_name(self):
        return self.name

    # Required for administrative interface
    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Recipes : {}>'.format(self.name)

    def __init__(self, name, quantity, calories, total_fat, saturated_fat, trans_fat, cholesterol, sodium,
                 total_carbohydrate, dietary_fiber, total_sugars, protein, vitamin_d, calcium, iron, potassium,
                 serving_size, serving_unit, cuisine, allergy_tag, **kwargs):
        self.name = name
        self.quantity = quantity
        self.calories = calories
        self.total_fat = total_fat
        self.saturated_fat = saturated_fat
        self.trans_fat = trans_fat
        self.cholesterol = cholesterol
        self.sodium = sodium
        self.total_carbohydrate = total_carbohydrate
        self.dietary_fiber = dietary_fiber
        self.total_sugars = total_sugars
        self.protein = protein
        self.vitamin_d = vitamin_d
        self.calcium = calcium
        self.iron = iron
        self.potassium = potassium
        self.serving_size = serving_size
        self.serving_unit = serving_unit
        self.cuisine = cuisine
        self.allergy_tag = allergy_tag


class RecipeIngredient(db.Model):
    recipe_ingredient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'), nullable=False)
    # name = db.Column(db.String(120), index=True, unique=True, nullable=False)

    # calories = db.Column(db.Float, default=0.0)
    # total_fat = db.Column(db.Float, default=0.0)
    # saturated_fat = db.Column(db.Float, default=0.0)
    # trans_fat = db.Column(db.Float, default=0.0)
    # cholesterol = db.Column(db.Float, default=0.0)
    # sodium = db.Column(db.Float, default=0.0)
    # total_carbohydrate = db.Column(db.Float, default=0.0)
    # dietary_fiber = db.Column(db.Float, default=0.0)
    # total_sugars = db.Column(db.Float, default=0.0)
    # protein = db.Column(db.Float, default=0.0)
    # vitamin_d = db.Column(db.Float, default=0.0)
    # calcium = db.Column(db.Float, default=0.0)
    # iron = db.Column(db.Float, default=0.0)
    # potassium = db.Column(db.Float, default=0.0)
    recipe = db.relationship("Recipes", backref=db.backref("recipe_ingredient", cascade="all,delete"))
    ingredient = db.relationship("Ingredients", backref=db.backref("recipe_ingredient", cascade="all,delete"))

    def get_recipe_name(self):
        return self.recipe.name

    # Required for administrative interface
    def __unicode__(self):
        return self.recipe.name

    def __repr__(self):
        return '<RecipeIngredient : {}>'.format(self.recipe.name)

    def __init__(self, recipe_id, ingredient_id,
                 # calories, total_fat, saturated_fat, trans_fat, cholesterol, sodium,
                 # total_carbohydrate, dietary_fiber, total_sugars, protein, vitamin_d, calcium, iron, potassium,
                 **kwargs):
        self.recipe_id = recipe_id
        self.ingredient_id = ingredient_id
        # self.calories = calories
        # self.total_fat = total_fat
        # self.saturated_fat = saturated_fat
        # self.trans_fat = trans_fat
        # self.cholesterol = cholesterol
        # self.sodium = sodium
        # self.total_carbohydrate = total_carbohydrate
        # self.dietary_fiber = dietary_fiber
        # self.total_sugars = total_sugars
        # self.protein = protein
        # self.vitamin_d = vitamin_d
        # self.calcium = calcium
        # self.iron = iron
        # self.potassium = potassium


class MenuCard(db.Model):
    menu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), index=True, unique=True, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.restaurant_id'), nullable=False)
    restaurant = db.relationship("Restaurant", backref=db.backref("menu_card", cascade="all,delete"))

    # Required for administrative interface
    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<MenuCard : {} - {}>'.format(self.restaurant.name, self.name)

    def __init__(self, name, restaurant_id, **kwargs):
        self.name = name
        self.restaurant_id = restaurant_id


class MenuCardRecipes(db.Model):
    menu_recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu_card.menu_id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
    recipe = db.relationship("Recipes", backref=db.backref("menu_card_recipes", cascade="all,delete"))
    menu_card = db.relationship("MenuCard", backref=db.backref("menu_card_recipes", cascade="all,delete"))

    def __init__(self, menu_id, recipe_id):
        self.menu_id = menu_id
        self.recipe_id = recipe_id
