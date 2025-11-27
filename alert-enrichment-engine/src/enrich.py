from pathlib import Path
import json

INCIDENT_STORE = {}

base_dir = Path(__file__).resolve().parent.parent
alert_file = base_dir / "examples" / "alert_raw.json"

STORE_FILE = base_dir / "data" / "incident_store.json"

if STORE_FILE.exists():
    with open(STORE_FILE, "r") as f:
        INCIDENT_STORE = json.load(f)
else:
    INCIDENT_STORE = {}
    
with open(alert_file, "r") as f:
    alert = json.load(f)


severity_map = {
    "CRIT": "critical",
    "CRITICAL": "critical",
    "WARN": "major",
    "WARNING": "major",
    "INFO": "info"
}

raw_severity = alert.get("severity", "").upper()
normalized_severity = severity_map.get(raw_severity, "minor")

metric = alert.get("metric", "").lower()

if metric in ["latency", "jitter", "packet_loss"]:
    category = "performance"
elif metric in ["availability", "reachability"]:
    category = "reachability"
else:
    category = "other"

if normalized_severity == "critical":
    impact = "high"
elif normalized_severity == "major":
    impact = "medium"
else:
    impact = "low"

incident_candidate = {
    "source": alert.get("source"),
    "device": alert.get("device"),
    "normalized_severity": normalized_severity,
    "impact": impact,
    "category": category,
    "original_alert": alert
}

import hashlib

dedup_key = hashlib.md5(
    f"{alert.get('device')}-{alert.get('metric')}-{normalized_severity}".encode()
).hexdigest()

incident_candidate["dedup_key"] = dedup_key

alert_state = alert.get("state", "active").lower()

if alert_state == "clear":
    status = "resolved"
else:
    status = "active"

incident_candidate["status"] = status

dedup_key = incident_candidate["dedup_key"]

if dedup_key in INCIDENT_STORE:
    if status == "resolved":
        INCIDENT_STORE[dedup_key]["status"] = "resolved"
        action = "updated_existing_incident"
    else:
        # update last seen alert, but keep incident
        INCIDENT_STORE[dedup_key]["original_alert"] = alert
        action = "suppressed_duplicate_alert"
else:
    INCIDENT_STORE[dedup_key] = incident_candidate
    action = "created_new_incident"

incident_candidate["action_taken"] = action

with open(STORE_FILE, "w") as f:
    json.dump(INCIDENT_STORE, f, indent=2)

print("\nRaw Alert:")
print(json.dumps(alert, indent=2))
print("\nCurrent Incident Store:")
print(json.dumps(INCIDENT_STORE, indent=2))
print("\nFinished Incident:")
print(json.dumps(incident_candidate, indent=2))