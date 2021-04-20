from flask import Flask
from flask_admin import Admin

from .admin import MyAdminIndexView, UserView, admin, RestaurantView, IngredientsView, RecipesView, \
    RecipeIngredientView, MenuCardRecipesView, MenuCardView
from .models.model import User, Restaurant, Ingredients, Recipes, RecipeIngredient, MenuCard, MenuCardRecipes
from .config import Config
from .extensions import cors, db, ma, login_manager, migrate, api
from .models import *
# from app_v1.routes import main
# from app_v1.routes.main import LoginResource
# from app_v1.routes.main import main
from .commands import create_tables, drop_tables
from flask_migrate import MigrateCommand


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)
    cors.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app)
    api.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

    admin.init_app(app)
    admin.add_views(UserView(User, db.session), RestaurantView(Restaurant, db.session),
                    IngredientsView(Ingredients, db.session), RecipesView(Recipes, db.session),
                    RecipeIngredientView(RecipeIngredient, db.session), MenuCardView(MenuCard, db.session),
                    MenuCardRecipesView(MenuCardRecipes, db.session))
    #
    # app.register_blueprint(main)

    app.cli.add_command(create_tables)
    app.cli.add_command(drop_tables)
    app.cli.add_command("db", MigrateCommand)

    return app
