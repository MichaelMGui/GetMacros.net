#!/bin/sh
# Full site build. Run from the repository root.
set -e
cd "$(dirname "$0")/.."

python3 tools/generate_articles.py
python3 tools/generate_quizzes.py
python3 tools/generate_games.py
python3 tools/generate_glossary.py

# Post-passes over the hand-authored pages the generators do not own.
python3 tools/build_localized_homepages.py
python3 tools/migrate_to_v3.py
python3 tools/build_meal_finder.py
python3 tools/add_breadcrumbs.py
python3 tools/fix_breadcrumb_labels.py
python3 tools/add_related_links.py
python3 tools/add_game_context.py
python3 tools/harden_pages.py

python3 tools/validate_site.py
