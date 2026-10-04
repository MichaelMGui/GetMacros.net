from pathlib import Path
import subprocess
P='C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
files=['apply_audited_data','build_release_resources','rebuild_publication','strengthen_meal_comparisons','sync_restaurant_release','release_copy_audit','refresh_release_search','finish_release_metadata','refine_food_pages','stamp_assets','validate_site','test_publication','test_search_visibility','test-content-value']
for f in files:
 subprocess.run([P,'-X','utf8','tools/'+f+'.py']+(['--apply-reviewed'] if f=='release_copy_audit' else []),check=True)
