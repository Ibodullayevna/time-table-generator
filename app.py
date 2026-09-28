"""Flask web server:  python app.py  ->  http://localhost:5000"""
import json, random
from flask import Flask, jsonify, request, send_from_directory
from scheduler import generate, ScheduleError

app = Flask(__name__, static_folder="static")


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/sample")
def sample():
    return jsonify(json.load(open("sample_input.json", encoding="utf-8")))


@app.post("/api/generate")
def api_generate():
    try:
        return jsonify(generate(request.get_json(force=True), seed=random.randint(1, 10**6)))
    except ScheduleError as e:
        return jsonify({"error": str(e)}), 422
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
