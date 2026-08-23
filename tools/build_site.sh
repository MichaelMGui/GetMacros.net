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
python3 tools/recover_site_focus.py

python3 tools/validate_site.py
