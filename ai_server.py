from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import math
import sys
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SAMPLES_FILE = DATA_DIR / "asl_samples.json"
VALID_HANDSHAPES = {"ONE", "TWO", "THREE", "FOUR", "FIVE", "W", "Y"}
MAX_DISTANCE = 0.5


def load_samples():
    if not SAMPLES_FILE.exists():
        return []
    try:
        data = json.loads(SAMPLES_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return [
            sample
            for sample in data
            if isinstance(sample, dict)
            and sample.get("l") in VALID_HANDSHAPES
            and isinstance(sample.get("v"), list)
            and len(sample["v"]) == 42
        ]
    except (json.JSONDecodeError, OSError):
        return []


def save_samples(samples):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLES_FILE.write_text(json.dumps(samples), encoding="utf-8")


def predict(vector, allowed):
    if len(vector) != 42:
        raise ValueError("vector must contain 42 values")
    if any(not isinstance(value, (int, float)) for value in vector):
        raise ValueError("vector values must be numeric")

    pool = [
        sample
        for sample in load_samples()
        if sample["l"] in allowed
    ]
    if len(pool) < 10:
        return None

    nearest = []
    for sample in pool:
        distance_squared = sum(
            (sample_value - vector_value) ** 2
            for sample_value, vector_value in zip(sample["v"], vector)
        )
        nearest.append({
            "l": sample["l"],
            "d": math.sqrt(distance_squared / 21),
        })

    nearest.sort(key=lambda item: item["d"])
    nearest = nearest[:5]
    votes = {}
    distances = {}
    for item in nearest:
        label = item["l"]
        votes[label] = votes.get(label, 0) + 1
        distances.setdefault(label, []).append(item["d"])

    label, confidence_count = max(votes.items(), key=lambda item: item[1])
    label_distances = distances[label]
    result = {
        "label": label,
        "conf": confidence_count / 5,
        "dist": sum(label_distances) / len(label_distances),
    }
    if result["dist"] > MAX_DISTANCE:
        result = None
    return result


class ASLTalkHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 10_000_000:
            raise ValueError("invalid request body size")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self.send_json(200, {"ok": True, "language": "python"})
        if path == "/api/config":
            return self.send_json(200, {
                "language": "python",
                "classifier": "nearest-neighbor",
                "model_scope": "seven-contextual-handshapes",
                "video_uploaded": False,
            })
        if path == "/api/samples":
            return self.send_json(200, {"samples": load_samples()})

        relative = "index.html" if path in ("", "/") else path.lstrip("/")
        file_path = (ROOT / relative).resolve()
        if ROOT not in file_path.parents:
            return self.send_json(403, {"error": "forbidden"})
        if not file_path.is_file():
            return self.send_json(404, {"error": "not found"})

        content_type = {
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".webmanifest": "application/manifest+json; charset=utf-8",
        }.get(file_path.suffix.lower(), "application/octet-stream")
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self.read_json()
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            return self.send_json(400, {"error": str(error)})

        if path == "/api/samples":
            samples = body.get("samples") if isinstance(body, dict) else None
            if not isinstance(samples, list):
                return self.send_json(400, {"error": "samples must be a list"})
            valid_samples = [
                sample for sample in samples
                if isinstance(sample, dict)
                and sample.get("l") in VALID_HANDSHAPES
                and isinstance(sample.get("v"), list)
                and len(sample["v"]) == 42
            ]
            save_samples(valid_samples)
            return self.send_json(200, {"saved": len(valid_samples)})

        if path == "/api/sample":
            sample = body
            if (
                not isinstance(sample, dict)
                or sample.get("l") not in VALID_HANDSHAPES
                or not isinstance(sample.get("v"), list)
                or len(sample["v"]) != 42
            ):
                return self.send_json(400, {"error": "invalid sample"})
            samples = load_samples()
            samples.append(sample)
            save_samples(samples)
            return self.send_json(200, {"saved": len(samples)})

        if path == "/api/predict":
            vector = body.get("vector") if isinstance(body, dict) else None
            allowed = body.get("allowed") if isinstance(body, dict) else None
            if not isinstance(vector, list) or not isinstance(allowed, list):
                return self.send_json(400, {"error": "vector and allowed are required"})
            try:
                result = predict(vector, set(allowed))
            except ValueError as error:
                return self.send_json(400, {"error": str(error)})
            return self.send_json(200, {"prediction": result})

        return self.send_json(404, {"error": "not found"})

    def do_DELETE(self):
        if urlparse(self.path).path == "/api/samples":
            save_samples([])
            return self.send_json(200, {"saved": 0})
        return self.send_json(404, {"error": "not found"})

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args), file=sys.stderr)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), ASLTalkHandler)
    print("ASLTalk Python AI server running at http://127.0.0.1:%d" % port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
