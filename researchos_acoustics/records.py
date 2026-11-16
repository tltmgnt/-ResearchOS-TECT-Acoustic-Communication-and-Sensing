"""Acoustic experiment records and strict JSON handling."""
import hashlib
import json
import math
import re
from pathlib import Path


class ValidationError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ValidationError(message)


def dumps(value):
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def parse_json(data):
    def constant(value):
        raise ValidationError(f"non-finite JSON constant: {value}")
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, f"duplicate JSON key: {k}")
            result[k] = v
        return result
    return json.loads(data, parse_constant=constant, object_pairs_hook=unique)


def read_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text(v, name):
    require(isinstance(v, str) and bool(v.strip()), f"{name} must be a nonempty string")


def integer(v, name, minimum=0, maximum=10**12):
    require(type(v) is int and minimum <= v <= maximum, f"{name} must be an integer in [{minimum}, {maximum}]")


def number(v, name, positive=False):
    require(type(v) in (int, float), f"{name} must be numeric")
    try:
        finite = math.isfinite(v)
    except OverflowError:
        finite = False
    require(finite and (v > 0 if positive else v >= 0), f"{name} must be finite and {'positive' if positive else 'nonnegative'}")


def safe_path(value):
    text(value, "evidence path")
    require(not Path(value).is_absolute() and "\\" not in value and not re.match(r"^[A-Za-z]:", value)
            and not any(p in (".", "..") for p in value.split("/")), "evidence path must be relative without traversal")
    return Path(value)


def evidence_bytes(root, path):
    root = Path(root).resolve()
    dest = (root / safe_path(path)).resolve()
    require(dest.is_relative_to(root), "evidence resolves outside record directory")
    return dest.read_bytes()


def validate(r):
    require(isinstance(r, dict), "experiment must be an object")
    require(type(r.get("schema_version")) is int and r["schema_version"] == 1, "schema_version must be integer 1")
    require(isinstance(r.get("id"), str) and bool(re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", r["id"])), "invalid experiment id")
    for k in ("title", "owner", "hypothesis", "protocol_reference", "differentiation"):
        text(r.get(k), k)
    require(r.get("data_kind") in ("synthetic", "simulation", "experimental"), "invalid input basis")
    integer(r.get("seed"), "seed", 0, 2**32-1)
    link = r.get("link")
    require(isinstance(link, dict), "link must be an object")
    for k in ("reference_distance_m", "sound_speed_m_s", "bit_rate_bps"):
        number(link.get(k), k, True)
    value = link.get("reference_ebn0_db")
    require(type(value) in (int,float) and -60 <= value <= 60, "reference Eb/N0 must be between -60 and 60 dB")
    number(link.get("absorption_db_km"), "absorption_db_km")
    integer(link.get("bits"), "bits", 1, 100000)
    ds = link.get("distances_m")
    require(isinstance(ds, list) and 1 <= len(ds) <= 30, "distances_m needs 1–30 distances")
    for d in ds:
        number(d, "distance_m", True)
        require(link["reference_distance_m"] <= d <= 1e6, "distances must be >= reference and <= 1e6 m")
    require(len(ds)*link["bits"] <= 1000000, "link simulation exceeds one million bits across distances")
    text(link.get("assumption_reference"), "link assumption_reference")
    sensing = r.get("ranging")
    require(isinstance(sensing, dict), "ranging must be an object")
    integer(sensing.get("sample_rate_hz"), "sample_rate_hz", 100, 192000)
    integer(sensing.get("pulse_samples"), "pulse_samples", 8, 256)
    integer(sensing.get("max_delay_samples"), "max_delay_samples", 1, 4096)
    integer(sensing.get("injected_delay_samples"), "injected_delay_samples", 0, sensing["max_delay_samples"])
    for k in ("echo_gain", "noise_std"):
        number(sensing.get(k), k)
        require(sensing[k] <= 10, f"{k} must be <= 10")
    text(sensing.get("assumption_reference"), "ranging assumption_reference")
    evidence = r.get("evidence")
    require(isinstance(evidence, list), "evidence must be an array")
    refs, paths = set(), set()
    for e in evidence:
        require(isinstance(e, dict), "evidence entries must be objects")
        text(e.get("id"), "evidence id")
        text(e.get("description"), "evidence description")
        safe_path(e.get("path"))
        require(e["id"] not in refs and e["path"] not in paths, "duplicate evidence id/path")
        refs.add(e["id"])
        paths.add(e["path"])
        require(isinstance(e.get("sha256"), str) and bool(re.fullmatch(r"[a-f0-9]{64}", e["sha256"])), "invalid evidence sha256")
    measurements = r.get("measurements")
    require(isinstance(measurements, list), "measurements must be an array")
    for m in measurements:
        require(isinstance(m, dict), "measurement must be an object")
        for k in ("metric", "unit", "method"):
            text(m.get(k), k)
        number(m.get("value"), "measurement value")
        number(m.get("uncertainty"), "measurement uncertainty")
        ids = m.get("evidence_ids")
        require(isinstance(ids, list) and all(isinstance(x,str) and x in refs for x in ids), "unknown measurement evidence reference")
        require(r["data_kind"] != "experimental" or bool(ids), "experimental measurements require evidence references")
    require(r["data_kind"] != "experimental" or bool(evidence) and bool(measurements), "experimental records require evidence and measurements")
    return r
