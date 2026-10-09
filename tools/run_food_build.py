from pathlib import Path
import subprocess
P='C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
files=['build_restaurant_expansion','apply_audited_data','build_release_resources','build_editorial_release','rebuild_publication','build_restaurant_data_report','strengthen_meal_comparisons','sync_restaurant_release','release_copy_audit','finish_release_metadata','refine_food_pages','build_playful_interface','build_play_release','integrate_playful_release','build_growth_release','refresh_release_search','stamp_assets','validate_site','test_publication','test_search_visibility','test-content-value','test-editorial-release','restaurant_release/test_expansion']
for f in files:
 subprocess.run([P,'-X','utf8','tools/'+f+'.py']+(['--apply-reviewed'] if f=='release_copy_audit' else ['--apply'] if f in {'build_restaurant_expansion','build_restaurant_data_report'} else []),check=True)
