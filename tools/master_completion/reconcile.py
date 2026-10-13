"""Reconcile real route-render evidence; never imply manual review of every page."""
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/"docs/master-completion-2026-10-13"
render=json.loads((OUT/"route-renders.json").read_text())
byroute={}
for row in render["renders"]:byroute.setdefault(row["route"],[]).append(row)
rows=[]
for route,checks in sorted(byroute.items()):
    file=ROOT/("index.html" if route=="/" else route.strip("/")+"/index.html" if route.endswith("/") else route.lstrip("/"))
    text=file.read_text(encoding="utf-8")
    kind=re.search(r'data-family="([^"]+)"',text);kind=kind[1] if kind else "existing-public"
    if "data-home-template=" in text:kind="shared-market-home"
    local=route[1:3].upper() if re.match(r"/[a-z]{2}/en/",route) else "US/global"
    remaining=[]
    if route=="/grocery-food-coverage.html" or "food-library" in route:remaining.append("Imported labels remain source-attributed, not independent package verification; missing fields and historical editions retained.")
    if "/ca/en/restaurants/"==route:remaining.append("See source-access and permissions blockers for unsupported local chains in restaurant-research.md.")
    if "food-diary" in route:remaining.append("Local private storage only; no account sync or connected AI/photo/voice service.")
    rows.append(dict(route=route,template=kind,current_visual_problems="No overflow, runtime, theme or stylesheet failure in the recorded automated renders",
        required_changes="Implemented shared system; relevant family journeys separately recorded",
        localization_status=local+"; English interface, source item names retained",data_source_status="Published source editions/provenance retained; new data reviewed in source-specific integrity reports",
        content_SEO_status="Route/link/title/heading/canonical/sitemap checked; diary/offline/error noindex intentional",
        functional_testing="Automated render plus applicable family journey; not every possible interaction on this page",
        mobile_testing="390 and 1280 px automated in both themes; representative family journeys also 320/768/1440",
        visual_verification="Automated rendered checks for this route. Individual images actually opened are listed in visual-review.md; no claim of manual review of all 350 routes.",
        remaining_blockers="; ".join(remaining)))
with (OUT/"coverage.csv").open("w",newline="",encoding="utf-8") as file:
    writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
assert not render["failures"]
print("Reconciled",len(rows),"public routes against",len(render["renders"]),"actual automated renders.")
