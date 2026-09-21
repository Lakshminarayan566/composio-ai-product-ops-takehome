import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "research_results.csv"
OUTPUT_MD = ROOT / "analysis" / "patterns_report.md"
OUTPUT_JSON = ROOT / "analysis" / "patterns.json"


def split_values(value):
    if not value:
        return []

    if value.strip().lower() == "unknown":
        return []

    return [
        x.strip()
        for x in value.split(",")
        if x.strip()
    ]


def pct(n, total):
    if total == 0:
        return 0.0
    return round((n / total) * 100, 1)


def count_field(rows, field):
    return Counter(
        (r.get(field) or "Unknown").strip()
        for r in rows
    )


def count_multivalue(rows, field):
    counter = Counter()

    for row in rows:
        for value in split_values(row.get(field, "")):
            counter[value] += 1

    return counter


def top_items(counter, limit=10):
    return [
        {"value": k, "count": v}
        for k, v in counter.most_common(limit)
    ]


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing dataset: {INPUT}"
        )

    with INPUT.open(
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    total = len(rows)

    # ---------------------------------------------------------
    # BASIC COUNTS
    # ---------------------------------------------------------

    category_counts = count_field(rows, "category")
    access_counts = count_field(
        rows,
        "self_serve_or_gated",
    )
    breadth_counts = count_field(
        rows,
        "api_breadth",
    )
    mcp_counts = count_field(
        rows,
        "mcp",
    )
    buildability_counts = count_field(
        rows,
        "buildability",
    )
    confidence_counts = count_field(
        rows,
        "confidence",
    )

    auth_counts = count_multivalue(
        rows,
        "auth_methods",
    )

    api_counts = count_multivalue(
        rows,
        "api_surface",
    )

    blocker_counts = count_field(
        rows,
        "main_blocker",
    )

    # ---------------------------------------------------------
    # EASY WINS / OUTREACH
    # ---------------------------------------------------------

    easy_wins = []

    for row in rows:
        build = row.get("buildability", "").strip()
        access = row.get(
            "self_serve_or_gated",
            "",
        ).strip()

        if (
            build == "Yes"
            and access in {
                "Self-serve",
                "Trial",
            }
        ):
            easy_wins.append(row["app"])

    outreach = []

    for row in rows:
        build = row.get(
            "buildability",
            "",
        ).strip()

        access = row.get(
            "self_serve_or_gated",
            "",
        ).strip()

        if (
            build in {
                "Partial",
                "No",
            }
            or access in {
                "Paid-plan required",
                "Admin approval",
                "Partner/Sales gated",
            }
        ):
            outreach.append(row["app"])

    # ---------------------------------------------------------
    # UNKNOWN / DATA QUALITY
    # ---------------------------------------------------------

    unknown_rates = {}

    for field in [
        "auth_methods",
        "self_serve_or_gated",
        "api_surface",
        "api_breadth",
        "mcp",
        "buildability",
        "main_blocker",
        "evidence_url",
    ]:
        unknown = 0

        for row in rows:
            value = (
                row.get(field)
                or ""
            ).strip()

            if (
                not value
                or value.lower() == "unknown"
            ):
                unknown += 1

        unknown_rates[field] = {
            "unknown_count": unknown,
            "unknown_percent": pct(
                unknown,
                total,
            ),
        }

    # ---------------------------------------------------------
    # VERIFICATION
    # ---------------------------------------------------------

    verification_status = count_field(
        rows,
        "verification_status",
    )

    # ---------------------------------------------------------
    # CATEGORY × BUILDABILITY
    # ---------------------------------------------------------

    category_build = defaultdict(
        Counter
    )

    for row in rows:
        category_build[
            row["category"]
        ][
            row.get(
                "buildability",
                "Unknown",
            )
        ] += 1

    # ---------------------------------------------------------
    # CATEGORY × ACCESS
    # ---------------------------------------------------------

    category_access = defaultdict(
        Counter
    )

    for row in rows:
        category_access[
            row["category"]
        ][
            row.get(
                "self_serve_or_gated",
                "Unknown",
            )
        ] += 1

    # ---------------------------------------------------------
    # JSON OUTPUT
    # ---------------------------------------------------------

    analysis = {
        "total_apps": total,

        "category_distribution":
            top_items(
                category_counts,
                20,
            ),

        "authentication":
            top_items(
                auth_counts,
                20,
            ),

        "api_surface":
            top_items(
                api_counts,
                20,
            ),

        "credential_access":
            top_items(
                access_counts,
                20,
            ),

        "api_breadth":
            top_items(
                breadth_counts,
                10,
            ),

        "mcp":
            top_items(
                mcp_counts,
                10,
            ),

        "buildability":
            top_items(
                buildability_counts,
                10,
            ),

        "confidence":
            top_items(
                confidence_counts,
                10,
            ),

        "main_blockers":
            top_items(
                blocker_counts,
                15,
            ),

        "easy_wins": {
            "count": len(easy_wins),
            "apps": easy_wins,
        },

        "outreach_candidates": {
            "count": len(outreach),
            "apps": outreach,
        },

        "unknown_rates":
            unknown_rates,

        "verification":
            dict(
                verification_status
            ),

        "category_buildability": {
            k: dict(v)
            for k, v
            in category_build.items()
        },

        "category_access": {
            k: dict(v)
            for k, v
            in category_access.items()
        },
    }

    OUTPUT_JSON.write_text(
        json.dumps(
            analysis,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # MARKDOWN REPORT
    # ---------------------------------------------------------

    lines = []

    lines.append(
        "# 100-App Pattern Analysis"
    )
    lines.append("")
    lines.append(
        f"Dataset size: **{total} apps**"
    )
    lines.append("")

    # -----------------------------------------------------
    # HEADLINE FINDINGS
    # -----------------------------------------------------

    self_serve = access_counts.get(
        "Self-serve",
        0,
    )

    gated = sum(
        access_counts.get(x, 0)
        for x in [
            "Paid-plan required",
            "Admin approval",
            "Partner/Sales gated",
        ]
    )

    build_yes = buildability_counts.get(
        "Yes",
        0,
    )

    build_partial = buildability_counts.get(
        "Partial",
        0,
    )

    build_no = buildability_counts.get(
        "No",
        0,
    )

    mcp_yes = mcp_counts.get(
        "Yes",
        0,
    )

    lines.append("## Headline findings")
    lines.append("")

    lines.append(
        f"- **{build_yes}/{total} ({pct(build_yes,total)}%)** "
        "are classified as directly buildable."
    )

    lines.append(
        f"- **{build_partial}/{total} ({pct(build_partial,total)}%)** "
        "are partially buildable because of meaningful restrictions."
    )

    lines.append(
        f"- **{build_no}/{total} ({pct(build_no,total)}%)** "
        "are currently classified as not buildable."
    )

    lines.append(
        f"- **{self_serve}/{total} ({pct(self_serve,total)}%)** "
        "have self-serve credential access."
    )

    lines.append(
        f"- **{gated}/{total} ({pct(gated,total)}%)** "
        "have a paid/admin/partner gate."
    )

    lines.append(
        f"- **{mcp_yes}/{total} ({pct(mcp_yes,total)}%)** "
        "have MCP marked Yes by the research agent."
    )

    lines.append("")

    # -----------------------------------------------------
    # AUTH
    # -----------------------------------------------------

    lines.append("## Authentication")
    lines.append("")
    lines.append("| Method | Apps | % |")
    lines.append("|---|---:|---:|")

    for item in auth_counts.most_common():
        lines.append(
            f"| {item[0]} | {item[1]} | "
            f"{pct(item[1], total)}% |"
        )

    lines.append("")

    # -----------------------------------------------------
    # ACCESS
    # -----------------------------------------------------

    lines.append(
        "## Self-serve vs gated access"
    )
    lines.append("")
    lines.append("| Access type | Apps | % |")
    lines.append("|---|---:|---:|")

    for item in access_counts.most_common():
        lines.append(
            f"| {item[0]} | {item[1]} | "
            f"{pct(item[1], total)}% |"
        )

    lines.append("")

    # -----------------------------------------------------
    # API
    # -----------------------------------------------------

    lines.append(
        "## API surface"
    )
    lines.append("")
    lines.append("| Surface | Apps | % |")
    lines.append("|---|---:|---:|")

    for item in api_counts.most_common():
        lines.append(
            f"| {item[0]} | {item[1]} | "
            f"{pct(item[1], total)}% |"
        )

    lines.append("")

    # -----------------------------------------------------
    # MCP
    # -----------------------------------------------------

    lines.append(
        "## MCP support"
    )
    lines.append("")
    lines.append("| MCP | Apps | % |")
    lines.append("|---|---:|---:|")

    for item in mcp_counts.most_common():
        lines.append(
            f"| {item[0]} | {item[1]} | "
            f"{pct(item[1], total)}% |"
        )

    lines.append("")

    # -----------------------------------------------------
    # BUILDABILITY
    # -----------------------------------------------------

    lines.append(
        "## Buildability"
    )
    lines.append("")
    lines.append("| Verdict | Apps | % |")
    lines.append("|---|---:|---:|")

    for item in buildability_counts.most_common():
        lines.append(
            f"| {item[0]} | {item[1]} | "
            f"{pct(item[1], total)}% |"
        )

    lines.append("")

    # -----------------------------------------------------
    # BLOCKERS
    # -----------------------------------------------------

    lines.append(
        "## Most common blockers"
    )
    lines.append("")

    for blocker, count in blocker_counts.most_common(10):
        lines.append(
            f"- **{blocker}** — {count} apps "
            f"({pct(count,total)}%)"
        )

    lines.append("")

    # -----------------------------------------------------
    # EASY WINS
    # -----------------------------------------------------

    lines.append(
        "## Easy-win candidates"
    )
    lines.append("")

    lines.append(
        f"**{len(easy_wins)} apps** are both "
        "self-serve/trial and classified as buildable."
    )

    lines.append("")

    lines.append(
        ", ".join(easy_wins[:40])
    )

    lines.append("")

    # -----------------------------------------------------
    # OUTREACH
    # -----------------------------------------------------

    lines.append(
        "## Outreach / high-friction candidates"
    )
    lines.append("")

    lines.append(
        f"**{len(outreach)} apps** have a partial/no "
        "buildability verdict or an explicit access gate."
    )

    lines.append("")

    lines.append(
        ", ".join(outreach[:40])
    )

    lines.append("")

    # -----------------------------------------------------
    # UNKNOWN RATES
    # -----------------------------------------------------

    lines.append(
        "## Evidence / uncertainty"
    )
    lines.append("")

    lines.append(
        "| Field | Unknown | % |"
    )
    lines.append(
        "|---|---:|---:|"
    )

    for field, info in unknown_rates.items():
        lines.append(
            f"| {field} | "
            f"{info['unknown_count']} | "
            f"{info['unknown_percent']}% |"
        )

    lines.append("")

    # -----------------------------------------------------
    # CATEGORY MATRIX
    # -----------------------------------------------------

    lines.append(
        "## Category × buildability"
    )
    lines.append("")

    for category, counts in category_build.items():

        formatted = ", ".join(
            f"{k}: {v}"
            for k, v
            in counts.items()
        )

        lines.append(
            f"- **{category}** → {formatted}"
        )

    lines.append("")

    lines.append(
        "## Category × credential access"
    )
    lines.append("")

    for category, counts in category_access.items():

        formatted = ", ".join(
            f"{k}: {v}"
            for k, v
            in counts.items()
        )

        lines.append(
            f"- **{category}** → {formatted}"
        )

    lines.append("")

    # -----------------------------------------------------
    # VERIFICATION
    # -----------------------------------------------------

    lines.append(
        "## Verification status in dataset"
    )
    lines.append("")

    for status, count in verification_status.items():
        lines.append(
            f"- **{status}** — {count}"
        )

    lines.append("")

    lines.append(
        "Generated automatically from "
        "`data/research_results.csv`."
    )

    OUTPUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        f"Created: {OUTPUT_MD}"
    )

    print(
        f"Created: {OUTPUT_JSON}"
    )

    print()
    print(
        f"Apps analyzed: {total}"
    )

    print(
        f"Easy wins: {len(easy_wins)}"
    )

    print(
        f"Outreach candidates: {len(outreach)}"
    )


if __name__ == "__main__":
    main()