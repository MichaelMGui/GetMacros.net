#!/usr/bin/env python3
"""Export actual editorial research records without manufacturing keyword metrics."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/ultimate-release-2026-10-19"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-count", type=int, default=0)
    args = ap.parse_args()
    rows, seen = [], set()
    for file in sorted((DOCS / "editorial").glob("*.json")):
        document = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or not isinstance(document.get("articles"), list): continue
        for article in document["articles"]:
            slug = article.get("slug", article.get("route", "")).lstrip("/")
            if not slug: continue
            if not slug.endswith(".html"): slug += ".html"
            if slug in seen: continue
            seen.add(slug)
            observations = article.get("search_observations", [])
            overlap = article.get("overlap_review", {})
            if isinstance(overlap, str): overlap = {"existing": overlap}
            review = article.get("review", {})
            if isinstance(review, str): review = {"status": review}
            observed = observations[0] if observations else {}
            rows.append({
                "route": "/"+slug,
                "intended_canonical_not_live_verification": "https://getmacros.net/"+slug,
                "market": article.get("country", article.get("market", "unspecified")),
                "reader_question": article.get("question", article.get("title", "")),
                "literal_research_query": observed.get("query", ""),
                "query_observed_on": observed.get("checked_on", document.get("research_date", "")),
                "observed_result_url": observed.get("source_url", ""),
                "public_result_observation": observed.get("observation", ""),
                "existing_page_overlap": overlap.get("existing", ""),
                "specific_added_value": overlap.get("distinct_value", article.get("question", "")),
                "source_trail": " | ".join(s.get("url", "") for s in article.get("sources", [])),
                "source_review_status": review.get("status", "not recorded"),
                "review_scope": review.get("scope", ""),
                "local_HTML_present": (ROOT/slug).is_file(),
                "publication_scope": "Refer to final integrated release manifest; this map does not establish live publication or indexing",
                "research_evidence_file": file.relative_to(ROOT).as_posix(),
                "search_volume_unavailable": "",
                "keyword_difficulty_unavailable": "",
                "ranking_position_unavailable": "",
                "GSC_impressions_unavailable": "",
                "maintenance_plan": "Recheck on official recipe/label/source changes; review quarterly. Workflow guidance also rechecked when controls change.",
            })
    if not rows: raise SystemExit("No article research records available; no intent map generated.")
    target = DOCS / "keyword-intent-map.csv"
    with target.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    missing = [row["route"] for row in rows if not row["literal_research_query"] or not row["observed_result_url"] or not row["source_trail"] or not row["existing_page_overlap"]]
    status = {"records": len(rows), "requiredCount": args.require_count, "incompleteResearchRows": missing,
              "map": target.relative_to(ROOT).as_posix(), "searchMetrics": "unavailable, intentionally blank",
              "livePublicationOrIndexingVerifiedByThisScript": False}
    (DOCS/"intent-map-status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))
    if len(rows) < args.require_count or missing: raise SystemExit(1)


if __name__ == "__main__": main()
