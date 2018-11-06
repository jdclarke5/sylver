
import sys
sys.path.insert(0, "C:\\Users\\Jackson\\Documents\\GitHub\\sylver")

from sylver.position import Position

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)
app = Flask(__name__)

@app.route("/")
def sylver():
    return app.send_static_file("sylver.html")

@app.route("/get_details", methods=["POST"])
def get_details():
    req = request.json
    print("Request received: ", req)
    try:
        p = Position(req["l"], req["length"])
        r = { 
            "error": None,
            **p.asdict(),
        }
    except ValueError as e:
        r = {
            "error": str(e),
        }
    return jsonify(r)
