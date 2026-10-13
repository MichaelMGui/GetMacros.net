"""Checkpoint the served application, keeping unrelated work and private data out."""
from pathlib import Path
import csv, hashlib, json, re, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/master-completion-2026-10-13"
PUBLISHER = ROOT / "docs/master-release-2026-10-12/publisher"
OUT.mkdir(parents=True, exist_ok=True)
markets = json.loads(re.search(r"window.GM_MARKETS=(.*);", (ROOT/"js/market-definitions.js").read_text(encoding="utf-8"))[1])
files = list(ROOT.glob("*.html"))
for code, market in markets.items():
    if code != "US":
        files.extend((ROOT/code.lower()/"en").rglob("index.html"))
rows = []
for p in sorted(set(files)):
    text = p.read_text(encoding="utf-8")
    relative = p.relative_to(ROOT).as_posix()
    route = "/" if relative == "index.html" else "/"+relative.removesuffix("index.html") if relative.endswith("/index.html") else "/"+relative
    template = re.search(r'data-family="([^"]+)"', text)
    template = "homepage" if route == "/" or re.fullmatch(r"/[a-z]{2}/en/", route) else template[1] if template else "game" if "/play-" in route else "existing-public"
    rows.append(dict(route=route, template=template, current_visual_problems="Pending fresh rendered review",
        required_changes="Verify against the 28-part acceptance checklist", localization_status=relative[:2].upper() if "/en/" in relative else "US/global",
        data_source_status="Existing editions retained; additions reviewed separately", content_SEO_status="Pending current research and route check",
        functional_testing="Pending this release", mobile_testing="Pending this release", visual_verification="Not manually inspected this release", remaining_blockers=""))
with (OUT/"coverage.csv").open("w", newline="", encoding="utf-8") as f:
    writer=csv.DictWriter(f, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
code = files + list((ROOT/"js").glob("*")) + list((ROOT/"css").glob("*")) + list((ROOT/"tools").glob("*.py")) + [ROOT/"tools/build_site.sh", ROOT/"sw.js", ROOT/"site.webmanifest", ROOT/".github/workflows/site-quality.yml"]
hashes = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in code if p.is_file()}
with zipfile.ZipFile(OUT/"baseline-source.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in hashes:z.write(ROOT/name, name)
revision=subprocess.check_output(["git","rev-parse","HEAD"], cwd=PUBLISHER, text=True).strip()
changed = [name for name in hashes if (PUBLISHER/name).exists() and (PUBLISHER/name).read_bytes().replace(b"\r\n",b"\n")!=(ROOT/name).read_bytes().replace(b"\r\n",b"\n")]
record=dict(capturedAt="2026-10-13", publishedRevision=revision, publicRoutes=len(rows), markets=list(markets),
    sourceHashCount=len(hashes), hashes=hashes, differencesAgainstPublisher=changed,
    checkpoint="Source archive plus immutable published Git revision; no credentials, private browser storage or unrelated project files included.")
(OUT/"baseline.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
print(json.dumps({k:v for k,v in record.items() if k not in ["hashes"]}, indent=2))
