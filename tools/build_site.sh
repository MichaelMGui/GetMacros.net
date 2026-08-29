#!/bin/sh
# Full site build. Run from the repository root.
set -e
cd "$(dirname "$0")/.."

python3 tools/generate_articles.py

# Focused product generators. Legacy breadcrumb/related-link post-passes relied
# on now-removed topic hubs and are intentionally not part of this build.
python3 tools/migrate_to_v3.py
python3 tools/build_meal_finder.py
python3 tools/build_restaurant_pages.py
python3 tools/build_focus_pages.py
# Studio v6 owns the homepage hierarchy. build_focus_pages rewrites
# index.html from its own template and drops the gm6 components the
# visual audit then requires, so this has to run after it.
python3 tools/build_studio_v6.py
python3 tools/expand_articles.py
python3 tools/retitle.py
python3 tools/apply_visual_system.py
python3 tools/inject_assets.py
python3 tools/recover_site_focus.py
# Last, so it sees the final head of every page: rewrite each local CSS and
# JS link with a hash of that file, so a changed asset always busts caches
# and an unchanged one keeps its cache entry.
python3 tools/stamp_assets.py

python3 tools/validate_site.py
python3 tools/audit_visual_contract.py
