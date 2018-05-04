
from sylver.position import Semigroup

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
        sg = Semigroup(req["l"], req["length"], find_gaps=req["find_gaps"])
        r = { 
            "error": None,
            **sg.to_json(),
        }
    except ValueError as e:
        r = {
            "error": str(e),
        }
    return jsonify(r)
