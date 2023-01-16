from flaskr import create_app
from flask import request
from werkzeug.urls import url_encode

app = create_app()


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002', debug=True)

