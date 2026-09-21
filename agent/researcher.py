import argparse
import csv
import json
import multiprocessing as mp
import time
from pathlib import Path

from ddgs import DDGS
from openai import OpenAI

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_BASE_URL,
    REQUEST_TIMEOUT,
    SEARCH_RESULTS_PER_QUERY,
    SEARCH_TIMEOUT,
    MAX_RETRIES,
)

ROOT = Path(__file__).resolve().parents[1]

INPUT_CSV = ROOT / "data" / "apps.csv"
OUTPUT_CSV = ROOT / "data" / "research_results.csv"

FIELDS = [
    "id",
    "category",
    "app",
    "official_hint",
    "what_it_does",
    "auth_methods",
    "self_serve_or_gated",
    "api_surface",
    "api_breadth",
    "mcp",
    "buildability",
    "main_blocker",
    "evidence_url",
    "confidence",
    "agent_source",
    "verification_status",
    "verification_notes",
]

RESEARCH_FIELDS = [
    "what_it_does",
    "auth_methods",
    "self_serve_or_gated",
    "api_surface",
    "api_breadth",
    "mcp",
    "buildability",
    "main_blocker",
    "evidence_url",
    "confidence",
]


SYSTEM_PROMPT = """
You are an AI Product Operations research agent.

You are given search results about one software application.

Your job is to extract factual information useful for deciding whether
an AI-agent toolkit could be built for that application.

IMPORTANT:
- Use ONLY the supplied search evidence.
- Prefer official first-party documentation.
- Do not invent facts.
- When the evidence is insufficient, return "Unknown".
- Keep every answer concise and factual.

Fields:

what_it_does:
One concise sentence describing the application.

auth_methods:
Use values such as:
OAuth2
API key
Basic
token
other
Unknown

self_serve_or_gated:
Use:
Self-serve
Trial
Paid-plan required
Admin approval
Partner/Sales gated
Unknown

api_surface:
Use:
REST
GraphQL
SOAP
SDK
CLI
Webhooks
or combinations
or Unknown

api_breadth:
Broad
Moderate
Narrow
Unknown

mcp:
Yes
No
Unknown

Only say Yes when the evidence supports an MCP server or MCP
integration.

buildability:
Yes
Partial
No
Unknown

Use:
Yes = practical agent toolkit can reasonably be built today
Partial = possible but meaningful restrictions exist
No = access/API restrictions make the toolkit impractical
Unknown = evidence is insufficient

main_blocker:
State the main practical blocker.
Use "None" if there is no meaningful blocker.
Use "Unknown" if evidence is insufficient.

evidence_url:
Use the strongest official URL present in the supplied evidence.
If no reliable official URL is present, use "Unknown".

confidence:
High
Medium
Low
"""


# -------------------------------------------------------------------
# LOAD INPUT
# -------------------------------------------------------------------

def load_apps():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {INPUT_CSV}"
        )

    with INPUT_CSV.open(
        newline="",
        encoding="utf-8",
    ) as f:
        return list(csv.DictReader(f))


def load_existing():
    if not OUTPUT_CSV.exists():
        return {}

    with OUTPUT_CSV.open(
        newline="",
        encoding="utf-8",
    ) as f:
        return {
            row["id"]: row
            for row in csv.DictReader(f)
            if row.get("id")
        }


# -------------------------------------------------------------------
# WEB SEARCH
# -------------------------------------------------------------------

def search_worker(app, queue):
    """
    Run DDGS in a separate process.

    This protects the main process from search backends
    that occasionally hang.
    """

    try:
        official_hint = (
            app.get("official_hint", "")
            .strip()
        )

        domain = (
            official_hint
            .replace("https://", "")
            .replace("http://", "")
            .split("/")[0]
            .strip()
        )

        app_name = app["app"]

        queries = [
            f'site:{domain} "{app_name}" API authentication',
            f'site:{domain} "{app_name}" developer API credentials',
            f'site:{domain} "{app_name}" MCP',
        ]

        results = []

        ddgs = DDGS(
            timeout=SEARCH_TIMEOUT
        )

        for query in queries:

            try:
                hits = ddgs.text(
                    query,
                    max_results=SEARCH_RESULTS_PER_QUERY,
                )

                if not hits:
                    continue

                for hit in hits:

                    url = (
                        hit.get("href")
                        or hit.get("url")
                        or ""
                    )

                    if not url:
                        continue

                    title = (
                        hit.get("title")
                        or ""
                    )

                    snippet = (
                        hit.get("body")
                        or hit.get("snippet")
                        or ""
                    )

                    results.append(
                        {
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                        }
                    )

            except Exception:
                continue

        # De-duplicate.
        unique = []
        seen = set()

        for item in results:

            url = item["url"]

            if url in seen:
                continue

            seen.add(url)
            unique.append(item)

        queue.put(
            unique[:10]
        )

    except Exception as exc:

        queue.put(
            {
                "search_error": str(exc)
            }
        )


def search_web(app):
    """
    Run DDGS in a child process with a hard timeout.
    """

    queue = mp.Queue()

    process = mp.Process(
        target=search_worker,
        args=(app, queue),
    )

    process.start()

    # Hard upper bound.
    hard_timeout = max(
        SEARCH_TIMEOUT * 3,
        20,
    )

    process.join(hard_timeout)

    if process.is_alive():

        process.terminate()
        process.join()

        print(
            f"  [search timeout] "
            f"{app['app']}"
        )

        return []

    if queue.empty():
        return []

    payload = queue.get()

    if (
        isinstance(payload, dict)
        and "search_error" in payload
    ):

        print(
            f"  [search warning] "
            f"{app['app']}: "
            f"{payload['search_error']}"
        )

        return []

    return payload


# -------------------------------------------------------------------
# GROQ CLIENT
# -------------------------------------------------------------------

def create_client():

    if not GROQ_API_KEY:
        raise SystemExit(
            "Missing GROQ_API_KEY. "
            "Add your Groq key to .env"
        )

    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
        timeout=REQUEST_TIMEOUT,
        max_retries=0,
    )


# -------------------------------------------------------------------
# EVIDENCE
# -------------------------------------------------------------------

def build_evidence_text(evidence):

    if not evidence:
        return "No web-search evidence was found."

    chunks = []

    for item in evidence:

        chunks.append(
            f"TITLE: {item['title']}\n"
            f"URL: {item['url']}\n"
            f"SNIPPET: {item['snippet']}"
        )

    return "\n\n".join(chunks)


# -------------------------------------------------------------------
# STRUCTURED EXTRACTION
# -------------------------------------------------------------------

def extract_structured(
    client,
    app,
    evidence,
):

    evidence_text = build_evidence_text(
        evidence
    )

    prompt = f"""
Research target:

APP:
{app["app"]}

CATEGORY:
{app["category"]}

OFFICIAL HINT:
{app["official_hint"]}

SEARCH EVIDENCE:
{evidence_text}

Extract the requested fields from ONLY the evidence above.

Do not use outside knowledge.

Choose Unknown when the evidence does not establish a fact.

For evidence_url, prefer an official developer/API/auth/MCP URL.
"""

    last_error = None

    for attempt in range(
        MAX_RETRIES + 1
    ):

        try:

            response = client.chat.completions.create(
                model=GROQ_MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],

                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "app_research",
                        "strict": True,
                        "schema": {
                            "type": "object",

                            "properties": {
                                "what_it_does": {
                                    "type": "string"
                                },

                                "auth_methods": {
                                    "type": "string"
                                },

                                "self_serve_or_gated": {
                                    "type": "string"
                                },

                                "api_surface": {
                                    "type": "string"
                                },

                                "api_breadth": {
                                    "type": "string"
                                },

                                "mcp": {
                                    "type": "string"
                                },

                                "buildability": {
                                    "type": "string"
                                },

                                "main_blocker": {
                                    "type": "string"
                                },

                                "evidence_url": {
                                    "type": "string"
                                },

                                "confidence": {
                                    "type": "string"
                                },
                            },

                            "required": [
                                "what_it_does",
                                "auth_methods",
                                "self_serve_or_gated",
                                "api_surface",
                                "api_breadth",
                                "mcp",
                                "buildability",
                                "main_blocker",
                                "evidence_url",
                                "confidence",
                            ],

                            "additionalProperties": False,
                        },
                    },
                },

                # Lower reasoning effort helps conserve quota.
                reasoning_effort="low",

                temperature=0,

                max_completion_tokens=900,
            )

            content = (
                response
                .choices[0]
                .message
                .content
                or "{}"
            ).strip()

            data = json.loads(content)

            result = {}

            for field in RESEARCH_FIELDS:

                value = data.get(
                    field,
                    "Unknown",
                )

                if value is None:
                    value = "Unknown"

                value = str(value).strip()

                if not value:
                    value = "Unknown"

                result[field] = value

            # If model did not select an evidence URL,
            # use the first available search result.
            if (
                result["evidence_url"]
                == "Unknown"
                and evidence
            ):
                result["evidence_url"] = (
                    evidence[0]["url"]
                )

            return result

        except Exception as exc:

            last_error = exc

            if attempt < MAX_RETRIES:

                wait_time = (
                    2 * (attempt + 1)
                )

                print(
                    f"  [retry "
                    f"{attempt + 1}/"
                    f"{MAX_RETRIES}] "
                    f"{app['app']}: "
                    f"{exc}"
                )

                time.sleep(wait_time)

    raise RuntimeError(
        f"Groq extraction failed: "
        f"{last_error}"
    )


# -------------------------------------------------------------------
# FAILED ROW
# -------------------------------------------------------------------

def make_failed_row(
    app,
    evidence,
    error,
):

    source_urls = " | ".join(
        item["url"]
        for item in evidence[:5]
    )

    return {
        **app,

        "what_it_does":
            "Unknown",

        "auth_methods":
            "Unknown",

        "self_serve_or_gated":
            "Unknown",

        "api_surface":
            "Unknown",

        "api_breadth":
            "Unknown",

        "mcp":
            "Unknown",

        "buildability":
            "Unknown",

        "main_blocker":
            "Research failed on first pass",

        "evidence_url":
            evidence[0]["url"]
            if evidence
            else "Unknown",

        "confidence":
            "Low",

        "agent_source":
            source_urls,

        "verification_status":
            "Needs retry",

        "verification_notes":
            str(error),
    }


# -------------------------------------------------------------------
# SAVE RESULTS
# -------------------------------------------------------------------

def save_rows(rows):

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    def sort_key(value):

        try:
            return int(value)
        except Exception:
            return value

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=FIELDS,
        )

        writer.writeheader()

        for app_id in sorted(
            rows,
            key=sort_key,
        ):

            row = rows[app_id]

            writer.writerow(
                {
                    field:
                    row.get(field, "")
                    for field in FIELDS
                }
            )


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Research the 100-app dataset "
            "using DDGS + Groq."
        )
    )

    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting app ID",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of apps to process",
    )

    args = parser.parse_args()

    apps = load_apps()

    existing = load_existing()

    client = create_client()

    selected = [
        app
        for app in apps
        if args.start
        <= int(app["id"])
        < args.start + args.limit
    ]

    print()
    print("=" * 65)
    print("AI PRODUCT OPS RESEARCH AGENT")
    print("=" * 65)

    print(
        f"Apps this run : {len(selected)}"
    )

    print(
        f"Model         : {GROQ_MODEL}"
    )

    print(
        f"Search results: "
        f"{SEARCH_RESULTS_PER_QUERY}"
    )

    print("=" * 65)

    for app in selected:

        app_id = app["id"]
        app_name = app["app"]

        print()
        print(
            f"[{app_id}/{len(apps)}] "
            f"Researching {app_name}..."
        )

        # -------------------------------------------------
        # STEP 1: WEB SEARCH
        # -------------------------------------------------

        evidence = search_web(app)

        print(
            f"  → search evidence: "
            f"{len(evidence)} result(s)"
        )

        # -------------------------------------------------
        # STEP 2: GROQ EXTRACTION
        # -------------------------------------------------

        try:

            result = extract_structured(
                client,
                app,
                evidence,
            )

            source_urls = " | ".join(
                item["url"]
                for item in evidence[:5]
            )

            row = {
                **app,
                **result,

                "agent_source":
                    source_urls,

                "verification_status":
                    "Unverified",

                "verification_notes":
                    "",
            }

            existing[app_id] = row

            print(
                "  ✓ extracted | "
                f"auth={result['auth_methods']} | "
                f"access={result['self_serve_or_gated']} | "
                f"api={result['api_surface']} | "
                f"mcp={result['mcp']} | "
                f"build={result['buildability']} | "
                f"confidence={result['confidence']}"
            )

        except KeyboardInterrupt:

            print()
            print(
                "Stopped by user."
            )

            save_rows(existing)

            print(
                f"Partial results saved to:"
                f"\n{OUTPUT_CSV}"
            )

            raise

        except Exception as exc:

            print(
                f"  ⚠ failed: {exc}"
            )

            existing[app_id] = (
                make_failed_row(
                    app,
                    evidence,
                    exc,
                )
            )

        # -------------------------------------------------
        # STEP 3: SAVE IMMEDIATELY
        # -------------------------------------------------

        save_rows(existing)

        print(
            f"  ✓ progress saved "
            f"({len(existing)}/100 rows)"
        )

        # Small delay.
        time.sleep(0.5)

    print()
    print("=" * 65)
    print("RUN COMPLETE")
    print("=" * 65)
    print(
        f"Output: {OUTPUT_CSV}"
    )
    print(
        f"Rows stored: {len(existing)}/100"
    )
    print("=" * 65)


if __name__ == "__main__":

    # Required for macOS multiprocessing.
    mp.freeze_support()

    main()
