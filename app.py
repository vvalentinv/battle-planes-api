from flask import Flask

from controller.user import uc
from controller.plane import pc

if __name__ == '__main__':
    app = Flask(__name__)

    app.register_blueprint(uc)
    app.register_blueprint(pc)

    app.run(port=5000, debug=True)
