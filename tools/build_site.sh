#!/bin/sh
# Publication build. Reviewed HTML is the source for retained inner pages.
# Historical redesign generators are retired: running them would overwrite
# reviewed content and restore the discarded presentation layers.
set -e
cd "$(dirname "$0")/.."
python3 tools/build_restaurant_expansion.py --apply
python3 tools/apply_audited_data.py
python3 tools/build_release_resources.py
python3 tools/build_editorial_release.py
python3 tools/rebuild_publication.py
python3 tools/build_restaurant_data_report.py --apply
python3 tools/strengthen_meal_comparisons.py
python3 tools/sync_restaurant_release.py
python3 tools/release_copy_audit.py --apply-reviewed
python3 tools/finish_release_metadata.py
python3 tools/refine_food_pages.py
python3 tools/build_playful_interface.py
python3 tools/build_play_release.py
python3 tools/integrate_playful_release.py
python3 tools/refresh_release_search.py
python3 tools/stamp_assets.py
python3 tools/validate_site.py
python3 tools/test_publication.py
python3 tools/test_search_visibility.py
python3 tools/test-content-value.py
python3 tools/test-editorial-release.py
python3 tools/restaurant_release/test_expansion.py
