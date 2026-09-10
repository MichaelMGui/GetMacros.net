#!/bin/sh
# Full site build. Run from the repository root.
set -e
cd "$(dirname "$0")/.."

python3 tools/bundle_styles.py --restore
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
# Add the focused intent-specific guides and rebuild the
# curated article hub after every generator that can rewrite article markup.
python3 tools/build_focused_guides.py
python3 tools/apply_visual_system.py
python3 tools/inject_assets.py
python3 tools/recover_site_focus.py
# After the focus pass, so it only ever links pages that survived it.
python3 tools/link_siblings.py
# After every pass that can rewrite a nav or a breadcrumb.
python3 tools/finish_navigation.py
python3 tools/normalize_calculator_layouts.py
python3 tools/extend_homepage.py
python3 tools/refine_recipe.py
python3 tools/refine_core_content.py
python3 tools/refine_journal.py
python3 tools/refine_reading.py
python3 tools/refine_plain_tools.py
python3 tools/refine_workspaces.py
python3 tools/refine_organization.py
python3 tools/finalize_quality.py
python3 tools/simplify_interface.py
python3 tools/refine_approachability.py
python3 tools/refine_food_reference.py
python3 tools/refine_submission.py
python3 tools/refine_motion_design.py
python3 tools/refine_tool_clarity.py
python3 tools/refine_depth_theme.py
python3 tools/refine_quiz_experience.py
python3 tools/refine_reading_finish.py
python3 tools/refine_learning_sections.py
python3 tools/refine_site_character.py
python3 tools/refine_meal_ideas.py
python3 tools/bundle_styles.py
# Last, so it sees the final head of every page: rewrite each local CSS and
# JS link with a hash of that file, so a changed asset always busts caches
# and an unchanged one keeps its cache entry.
python3 tools/stamp_assets.py

python3 tools/validate_site.py
python3 tools/test_style_bundles.py
python3 tools/audit_visual_contract.py
python3 tools/test_workspace_contract.py
python3 tools/test_homepage_extension.py
python3 tools/test_submission_content.py
