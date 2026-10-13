"""Copy only this release into the existing approved writable Git publisher."""
from pathlib import Path
import json, re, shutil, subprocess, time
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"docs/master-completion-2026-10-13"
DEST=ROOT/"docs/master-release-2026-10-12/publisher"
assert DEST.resolve().is_relative_to(ROOT/"docs") and (DEST/".git").is_dir()
assert subprocess.check_output(["git","remote","get-url","origin"],cwd=DEST,text=True).strip()=="https://github.com/MichaelMGui/GetMacros.net.git"
previous=json.loads((OUT/"baseline.json").read_text())["publishedRevision"]
assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=DEST,text=True).strip()==previous
baseline=set(json.loads((OUT/"baseline.json").read_text())["hashes"])
tracked=set(subprocess.check_output(["git","ls-files"],cwd=DEST,text=True).splitlines())
# Preserve unrelated historical generators that were never in production.
candidates={ROOT/name for name in baseline if name in tracked}
candidates.update(ROOT.glob("*.html"))
for code in ["ca","mx","gb","ie","au","nz","jp"]:candidates.update((ROOT/code/"en").rglob("index.html"))
for folder in ["assets/generated","data/branded-foods/off","tools/master_completion"]:
    candidates.update(p for p in (ROOT/folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
owned=["tools/build_master_completion.py","tools/site_scope.py","tools/growth_release/review-source.py","tools/growth_release/menu-records.json",
       "tools/international/test-markets.cjs","tools/product_release/test-food.cjs","tools/product_release/dev-server.cjs","tools/product_release/test-generators.py","data/restaurant-presence.json",
       "tools/master_release/test-branded-search.cjs","tools/master_release/test-branded-integrity.cjs",
       "tools/master_release/visual-completion.cjs","tools/master_release/visual-motion.cjs","tools/master_release/visual-zoom.cjs",
       "tools/food-design.css","sitemap.xml"]
candidates.update(ROOT/name for name in owned)
candidates.update(p for p in OUT.glob("*") if p.is_file() and p.suffix in [".md",".csv",".json"] and p.name not in ["baseline.json","publication-files.json","stage-paths.json","deployment-verification.json"])
changed=[];allowed=set()
for p in sorted(candidates):
    if not p.is_file():continue
    assert p.resolve().is_relative_to(ROOT)
    name=p.relative_to(ROOT).as_posix()
    assert not name.startswith(("music-platform/","server/private/")) and "/grocery-sources/" not in name and "/restaurant-sources/" not in name
    if p.stat().st_size>95_000_000:raise ValueError("Individual GitHub publication file too large: "+name)
    allowed.add(name);target=DEST/name
    source_bytes=p.read_bytes();target_bytes=target.read_bytes() if target.exists() else None
    if target_bytes is not None:
        if p.suffix not in [".gz", ".zip", ".png", ".jpg", ".webp"]:
            source_bytes=source_bytes.replace(b"\r\n",b"\n");target_bytes=target_bytes.replace(b"\r\n",b"\n")
        if source_bytes==target_bytes:continue
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);changed.append(name)
# Prune only content-addressed artifacts in the fixed generator-owned directory.
base=DEST/"assets/generated"
for p in base.iterdir():
    assert p.resolve().is_relative_to(base.resolve())
    if p.is_file() and re.fullmatch(r"[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)",p.name) and not (ROOT/"assets/generated"/p.name).exists():
        p.unlink();changed.append(p.relative_to(DEST).as_posix());allowed.add(p.relative_to(DEST).as_posix())
pending=[]
for entry in subprocess.check_output(["git","status","--porcelain","--untracked-files=all","-z"],cwd=DEST,text=True).split("\0"):
    if entry and entry[3:] in allowed:pending.append(entry[3:])
(OUT/"stage-paths.json").write_text(json.dumps(sorted(set(pending)),indent=2),encoding="utf-8")
(OUT/"publication-files.json").write_text(json.dumps(dict(previousRevision=previous,changedFiles=len(set(changed)),paths=sorted(set(changed)),scope="Reviewed master completion only; private source archives and inherited unrelated work excluded."),indent=2),encoding="utf-8")
for i in range(0,len(pending),60):
    command=["git","-c","core.safecrlf=false","-c","gc.auto=0","add","--"]+pending[i:i+60]
    for attempt in range(3):
        result=subprocess.run(command,cwd=DEST,capture_output=True,text=True)
        if not result.returncode:break
        print("Staging retry",attempt+1,"at",i,":",result.stderr.strip(),flush=True)
        time.sleep(0.3)
    if result.returncode:
        print(result.stderr);raise RuntimeError("Staging batch failed at "+str(i))
release_paths=subprocess.check_output(["git","diff","--cached","--name-only","-z"],cwd=DEST,text=True).split("\0")
release_paths=sorted(p for p in release_paths if p)
(OUT/"publication-files.json").write_text(json.dumps(dict(previousRevision=previous,changedFiles=len(release_paths),paths=release_paths,scope="Reviewed master completion only; private source archives and inherited unrelated work excluded."),indent=2),encoding="utf-8")
print(json.dumps(dict(stagedPaths=len(pending),changedFiles=len(release_paths),previousRevision=previous)))
