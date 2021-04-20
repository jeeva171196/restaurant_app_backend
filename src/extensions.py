from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
ma = Marshmallow()
login_manager = LoginManager()
migrate = Migrate(db=db)
cors = CORS(resources={r"/api/*": {"origins": "*"}})

api = Api()

ns_um = api.namespace('User Management', description='User Management operations', path="/api/user")
# ns_pm = api.namespace('Product Management', description='Product Management operations', path="/api/product")
# ns_sm = api.namespace('Sales History Management', description='Sales History Management operations', path="/api/sale")
# ns_report = api.namespace('Bill Management', description='Bill Management operations', path="/api/bill")
