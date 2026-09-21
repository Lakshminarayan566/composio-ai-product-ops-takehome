import csv
import json
import html
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

DATASET = ROOT / "data" / "research_results.csv"
PATTERNS = ROOT / "analysis" / "patterns.json"
OUTPUT = ROOT / "output" / "case-study.html"


def esc(value):
    return html.escape(str(value or ""))


def load_csv():
    with DATASET.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_patterns():
    if PATTERNS.exists():
        with PATTERNS.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def pct(n, total):
    return f"{(n / total * 100):.1f}%" if total else "0.0%"


def bar_rows(counter, total):
    rows = []

    for key, value in counter.most_common():
        width = min(100, (value / total) * 100 if total else 0)

        rows.append(
            f"""
            <div class="bar-row">
                <div class="bar-label">
                    <span>{esc(key)}</span>
                    <strong>{value}</strong>
                </div>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{width:.1f}%"></div>
                </div>
                <div class="bar-pct">{pct(value,total)}</div>
            </div>
            """
        )

    return "".join(rows)


def main():
    rows = load_csv()
    patterns = load_patterns()

    total = len(rows)

    auth = Counter(
        (r.get("auth_methods") or "Unknown").strip()
        for r in rows
    )

    access = Counter(
        (r.get("self_serve_or_gated") or "Unknown").strip()
        for r in rows
    )

    api = Counter(
        (r.get("api_surface") or "Unknown").strip()
        for r in rows
    )

    mcp = Counter(
        (r.get("mcp") or "Unknown").strip()
        for r in rows
    )

    build = Counter(
        (r.get("buildability") or "Unknown").strip()
        for r in rows
    )

    blockers = Counter(
        (r.get("main_blocker") or "Unknown").strip()
        for r in rows
    )

    verification = Counter(
        (r.get("verification_status") or "Unverified").strip()
        for r in rows
    )

    easy_wins = sum(
        1
        for r in rows
        if r.get("buildability") in {"Yes"}
        and r.get("self_serve_or_gated") in {
            "Self-serve",
            "Trial",
        }
    )

    outreach = sum(
        1
        for r in rows
        if r.get("buildability") in {"Partial", "No"}
        or r.get("self_serve_or_gated") in {
            "Paid-plan required",
            "Admin approval",
            "Partner/Sales gated",
        }
    )

    # Verification numbers from the completed targeted sample.
    verified_count = verification.get("Verified", 0)
    unresolved_count = verification.get("Unresolved", 0)
    unverified_count = verification.get("Unverified", 0)

    html_rows = []

    for r in rows:
        status = r.get("verification_status", "Unverified")

        html_rows.append(
            f"""
            <tr data-status="{esc(status)}"
                data-category="{esc(r.get('category'))}"
                data-build="{esc(r.get('buildability'))}">
                <td>{esc(r.get('id'))}</td>
                <td><strong>{esc(r.get('app'))}</strong></td>
                <td>{esc(r.get('category'))}</td>
                <td>{esc(r.get('auth_methods'))}</td>
                <td>{esc(r.get('self_serve_or_gated'))}</td>
                <td>{esc(r.get('api_surface'))}</td>
                <td>{esc(r.get('mcp'))}</td>
                <td>{esc(r.get('buildability'))}</td>
                <td>{esc(r.get('main_blocker'))}</td>
                <td>
                    {
                        '<a href="' + esc(r.get('evidence_url'))
                        + '" target="_blank">Source</a>'
                        if r.get("evidence_url")
                        and r.get("evidence_url") != "Unknown"
                        else "—"
                    }
                </td>
            </tr>
            """
        )

    table_html = "".join(html_rows)

    headline_build = build.get("Yes", 0)
    headline_partial = build.get("Partial", 0)
    headline_no = build.get("No", 0)

    headline_self = access.get("Self-serve", 0)

    top_blockers = blockers.most_common(6)

    blocker_html = "".join(
        f"""
        <div class="mini-row">
            <span>{esc(k)}</span>
            <strong>{v}</strong>
        </div>
        """
        for k, v in top_blockers
    )

    html_doc = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AI Product Ops — 100 App Research</title>

<style>
:root {{
    --bg: #f6f7f9;
    --card: #ffffff;
    --text: #111827;
    --muted: #667085;
    --border: #e4e7ec;
    --dark: #182230;
    --accent: #7f56d9;
    --accent2: #6941c6;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
    background: var(--bg);
    color: var(--text);
}}

.container {{
    max-width: 1400px;
    margin: auto;
    padding: 32px 28px 80px;
}}

.hero {{
    background: var(--dark);
    color: white;
    padding: 46px;
    border-radius: 24px;
    margin-bottom: 24px;
}}

.kicker {{
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: .12em;
    opacity: .7;
    margin-bottom: 12px;
}}

h1 {{
    font-size: 46px;
    line-height: 1.05;
    margin: 0 0 16px;
}}

.hero p {{
    max-width: 860px;
    font-size: 18px;
    line-height: 1.6;
    color: #d0d5dd;
    margin: 0;
}}

.grid {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}}

.card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
}}

.metric {{
    font-size: 34px;
    font-weight: 800;
}}

.metric-label {{
    color: var(--muted);
    margin-top: 4px;
}}

.section {{
    background: white;
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 28px;
    margin-bottom: 24px;
}}

h2 {{
    margin-top: 0;
    font-size: 27px;
}}

h3 {{
    margin-top: 28px;
}}

.muted {{
    color: var(--muted);
    line-height: 1.6;
}}

.insight-grid {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
}}

.insight {{
    background: #f9fafb;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
}}

.insight strong {{
    display: block;
    font-size: 20px;
    margin-bottom: 7px;
}}

.bar-row {{
    display: grid;
    grid-template-columns: 240px 1fr 70px;
    gap: 12px;
    align-items: center;
    margin: 11px 0;
}}

.bar-label {{
    display: flex;
    justify-content: space-between;
    gap: 12px;
}}

.bar-track {{
    height: 10px;
    background: #eaecf0;
    border-radius: 999px;
    overflow: hidden;
}}

.bar-fill {{
    height: 100%;
    background: var(--accent);
    border-radius: 999px;
}}

.bar-pct {{
    text-align: right;
    color: var(--muted);
}}

.workflow {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
    align-items: center;
}}

.step {{
    border: 1px solid var(--border);
    padding: 18px;
    border-radius: 14px;
    background: #fafafa;
    text-align: center;
    font-weight: 700;
}}

.arrow {{
    text-align: center;
    color: var(--muted);
    font-size: 22px;
}}

.controls {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 16px;
}}

input, select {{
    padding: 11px 13px;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: white;
    font-size: 14px;
}}

.table-wrap {{
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 14px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    min-width: 1200px;
}}

th, td {{
    padding: 12px 13px;
    border-bottom: 1px solid var(--border);
    text-align: left;
    vertical-align: top;
    font-size: 13px;
}}

th {{
    background: #f9fafb;
    position: sticky;
    top: 0;
    z-index: 2;
}}

a {{
    color: var(--accent2);
    text-decoration: none;
    font-weight: 700;
}}

.mini-row {{
    display: flex;
    justify-content: space-between;
    gap: 20px;
    padding: 11px 0;
    border-bottom: 1px solid var(--border);
}}

.verify-box {{
    background: #fff8ed;
    border: 1px solid #fedf89;
    border-radius: 16px;
    padding: 18px;
}}

footer {{
    color: var(--muted);
    text-align: center;
    font-size: 13px;
    padding-top: 10px;
}}

@media (max-width: 800px) {{
    .hero {{
        padding: 30px;
    }}

    h1 {{
        font-size: 35px;
    }}

    .bar-row {{
        grid-template-columns: 1fr;
    }}

    .bar-pct {{
        text-align: left;
    }}
</style>
</head>

<body>

<div class="container">

<section class="hero">
    <div class="kicker">AI Product Ops Take-home</div>
    <h1>100-app API & Agent-Buildability Research</h1>
    <p>
        An automated research pipeline that evaluates authentication,
        credential access, API surface, MCP availability and practical
        agent-toolkit buildability across 100 applications.
    </p>
</section>


<section class="grid">

    <div class="card">
        <div class="metric">{total}</div>
        <div class="metric-label">Apps researched</div>
    </div>

    <div class="card">
        <div class="metric">{easy_wins}</div>
        <div class="metric-label">Agent-classified easy wins</div>
    </div>

    <div class="card">
        <div class="metric">{outreach}</div>
        <div class="metric-label">Agent-classified high-friction / outreach</div>
    </div>

    <div class="card">
        <div class="metric">{verified_count}</div>
        <div class="metric-label">Document-verified</div>
    </div>

    <div class="card">
        <div class="metric">{unresolved_count}</div>
        <div class="metric-label">Unresolved</div>
    </div>

</section>


<section class="section">

<h2>Headline findings</h2>

<div class="insight-grid">

    <div class="insight">
        <strong>
            {headline_build}/{total}
            ({pct(headline_build,total)})
        </strong>
        classified as directly buildable.
    </div>

    <div class="insight">
        <strong>
            {headline_partial}/{total}
            ({pct(headline_partial,total)})
        </strong>
        classified as partially buildable.
    </div>

    <div class="insight">
        <strong>
            {headline_self}/{total}
            ({pct(headline_self,total)})
        </strong>
        have self-serve credential access.
    </div>

    <div class="insight">
        <strong>
            {mcp.get("Yes",0)}/{total}
            ({pct(mcp.get("Yes",0),total)})
        </strong>
        are marked as having MCP support.
    </div>

</div>

<p class="muted">
These are agent-generated classifications from the 100-app research
dataset. Only the explicitly verified sample is treated as
document-verified.
</p>

</section>


<section class="section">

<h2>Pattern analysis</h2>

<h3>Authentication</h3>

{bar_rows(auth, total)}

<h3>Credential access</h3>

{bar_rows(access, total)}

<h3>API surface</h3>

{bar_rows(api, total)}

<h3>MCP</h3>

{bar_rows(mcp, total)}

<h3>Buildability</h3>

{bar_rows(build, total)}

</section>


<section class="section">

<h2>Common blockers</h2>

{blocker_html}

</section>


<section class="section">

<h2>How the agent works</h2>

<div class="workflow">

    <div class="step">100-app input CSV</div>
    <div class="arrow">→</div>
    <div class="step">Official-doc search</div>
    <div class="arrow">→</div>
    <div class="step">Evidence collection</div>
    <div class="arrow">→</div>
    <div class="step">LLM extraction</div>
    <div class="arrow">→</div>
    <div class="step">Structured CSV</div>

</div>

<p class="muted">
The pipeline searches app-specific official sources, sends the collected
evidence to the extraction model, validates the structured response,
saves progress after every app, and records failures rather than
crashing the whole run.
</p>

</section>


<section class="section">

<h2>Verification</h2>

<div class="grid">

    <div class="card">
        <div class="metric">20</div>
        <div class="metric-label">Targeted sample</div>
    </div>

    <div class="card">
        <div class="metric">19</div>
        <div class="metric-label">Independently supported sample apps</div>
    </div>

    <div class="card">
        <div class="metric">18.1%</div>
        <div class="metric-label">First-pass factual accuracy</div>
    </div>

    <div class="card">
        <div class="metric">1</div>
        <div class="metric-label">Explicit unresolved case</div>
    </div>

</div>

<div class="verify-box">

<strong>Interpretation:</strong>

<p>
The verification sample was deliberately constructed as a targeted
stress test, prioritizing weak/low-confidence rows rather than serving
as a random estimate of all-100 accuracy. The 18.1% figure therefore
describes the sampled first pass, not the expected accuracy of every
row in the dataset.
</p>

<p>
The verified sample was corrected against official documentation.
Unresolved cases remain explicitly unresolved rather than being filled
with guesses.
</p>

</div>

</section>


<section class="section">

<h2>100-app dataset</h2>

<div class="controls">

    <input
        id="search"
        type="text"
        placeholder="Search app, category, auth..."
    >

    <select id="status">
        <option value="">All verification status</option>
        <option value="Verified">Verified</option>
        <option value="Unresolved">Unresolved</option>
        <option value="Unverified">Unverified</option>
        <option value="Needs retry">Needs retry</option>
    </select>

    <select id="build">
        <option value="">All buildability</option>
        <option value="Yes">Yes</option>
        <option value="Partial">Partial</option>
        <option value="No">No</option>
        <option value="Unknown">Unknown</option>
    </select>

</div>

<div class="table-wrap">

<table id="apps">

<thead>
<tr>
    <th>ID</th>
    <th>App</th>
    <th>Category</th>
    <th>Auth</th>
    <th>Access</th>
    <th>API</th>
    <th>MCP</th>
    <th>Buildability</th>
    <th>Blocker</th>
    <th>Evidence</th>
</tr>
</thead>

<tbody>
{table_html}
</tbody>

</table>

</div>

</section>


<section class="section">

<h2>Limitations & human involvement</h2>

<p class="muted">
The research agent is an acceleration layer, not a substitute for
source verification. Search engines can miss official pages, API
documentation can be ambiguous, and access requirements can vary by
plan, workspace, region, approval status, or enterprise agreement.
</p>

<p class="muted">
The final dataset explicitly records uncertainty and failed research
rather than converting missing evidence into invented answers.
Human verification was used on a targeted sample to identify errors
and correct the final sample.
</p>

</section>


<section class="section">

<h2>Repository / reproducibility</h2>

<p class="muted">
Source code, the 100-app input dataset, generated research results,
verification artifacts, analysis scripts, and this case study are
stored in the project repository.
</p>

<pre>
python -m pip install -r requirements.txt
python agent/researcher.py --start 1 --limit 100
python analysis/analyze_patterns.py
python output/build_case_study.py
</pre>

</section>


<footer>
AI Product Ops Intern Take-home · 100-app research pipeline
</footer>

</div>


<script>
const search = document.getElementById("search");
const status = document.getElementById("status");
const build = document.getElementById("build");

function filterRows() {{

    const q = search.value.toLowerCase();
    const statusValue = status.value;
    const buildValue = build.value;

    document
        .querySelectorAll("#apps tbody tr")
        .forEach(row => {{

            const text = row.innerText.toLowerCase();

            const rowStatus = row.dataset.status;
            const rowBuild = row.dataset.build;

            const matchesSearch =
                !q || text.includes(q);

            const matchesStatus =
                !statusValue ||
                rowStatus === statusValue;

            const matchesBuild =
                !buildValue ||
                rowBuild === buildValue;

            row.style.display =
                matchesSearch &&
                matchesStatus &&
                matchesBuild
                    ? ""
                    : "none";
        }});
}}

search.addEventListener("input", filterRows);
status.addEventListener("change", filterRows);
build.addEventListener("change", filterRows);
</script>

</body>
</html>
"""

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        html_doc,
        encoding="utf-8",
    )

    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()