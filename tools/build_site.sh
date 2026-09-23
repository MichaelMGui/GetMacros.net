#!/bin/sh
# Publication build. Reviewed HTML is the source for retained inner pages.
# Historical redesign generators are retired: running them would overwrite
# reviewed content and restore the discarded presentation layers.
set -e
cd "$(dirname "$0")/.."
python3 tools/rebuild_publication.py
python3 tools/stamp_assets.py
python3 tools/validate_site.py
python3 tools/test_publication.py
python3 tools/test_search_visibility.py
