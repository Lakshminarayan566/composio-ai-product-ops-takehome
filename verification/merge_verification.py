import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAIN = ROOT / "data" / "research_results.csv"
TARGETS = ROOT / "verification" / "verified_targets.csv"

FIELDS_TO_UPDATE = [
    "what_it_does",
    "auth_methods",
    "self_serve_or_gated",
    "api_surface",
    "api_breadth",
    "mcp",
    "buildability",
    "main_blocker",
    "evidence_url",
]

with MAIN.open(newline="", encoding="utf-8") as f:
    main_rows = list(csv.DictReader(f))

with TARGETS.open(newline="", encoding="utf-8") as f:
    target_rows = {
        row["id"]: row
        for row in csv.DictReader(f)
    }

for row in main_rows:
    app_id = row["id"]

    if app_id not in target_rows:
        continue

    target = target_rows[app_id]

    for field in FIELDS_TO_UPDATE:
        verified_field = f"verified_{field}"

        if verified_field in target:
            row[field] = target[verified_field]

    row["verification_status"] = (
        "Verified"
        if app_id != "84"
        else "Unresolved"
    )

    row["verification_notes"] = (
        "Manually/document verified against official source."
        if app_id != "84"
        else "Insufficient first-party evidence established."
    )

    row["agent_source"] = (
        target.get("verified_evidence_url", "")
    )

with MAIN.open(
    "w",
    newline="",
    encoding="utf-8",
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=main_rows[0].keys(),
    )

    writer.writeheader()
    writer.writerows(main_rows)

print("Verification merged successfully.")

verified = sum(
    1
    for r in main_rows
    if r.get("verification_status") == "Verified"
)

unresolved = sum(
    1
    for r in main_rows
    if r.get("verification_status") == "Unresolved"
)

unverified = sum(
    1
    for r in main_rows
    if r.get("verification_status") == "Unverified"
)

print("Verified:", verified)
print("Unresolved:", unresolved)
print("Still unverified:", unverified)