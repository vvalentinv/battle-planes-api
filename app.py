from flask import Flask

from controller.user import uc

if __name__ == '__main__':
    app = Flask(__name__)

    app.register_blueprint(uc)

    app.run(port=5000, debug=True)
