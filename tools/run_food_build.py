from pathlib import Path
import subprocess,sys
P=sys.executable
subprocess.run([P,'-X','utf8','tools/restore_asset_sources.py'],check=True)
files=['build_restaurant_expansion','apply_audited_data','build_release_resources','build_editorial_release','rebuild_publication','build_restaurant_data_report','strengthen_meal_comparisons','sync_restaurant_release','release_copy_audit','finish_release_metadata','refine_food_pages','build_playful_interface','build_play_release','integrate_playful_release','build_growth_release','refresh_release_search','stamp_assets','validate_site','test_publication','test_search_visibility','test-content-value','test-editorial-release','restaurant_release/test_expansion']
files.insert(files.index('refresh_release_search'),'build_international_release')
files.insert(files.index('refresh_release_search'),'build_global_product')
files.insert(files.index('refresh_release_search'),'build_master_release')
files.insert(files.index('refresh_release_search'),'build_master_completion')
files.insert(files.index('refresh_release_search'),'build_master_diary')
files.insert(files.index('refresh_release_search'),'build_master_interface')
files.insert(files.index('refresh_release_search'),'build_clarity_release')
for f in files:
 subprocess.run([P,'-X','utf8','tools/'+f+'.py']+(['--apply-reviewed'] if f=='release_copy_audit' else ['--apply'] if f in {'build_restaurant_expansion','build_restaurant_data_report'} else []),check=True)
subprocess.run(['node','tools/international/test-markets.cjs'],check=True)
subprocess.run([P,'-X','utf8','tools/test_visible_workspace.py'],check=True)
for test in ['tools/test_master_homepages.py','tools/master_release/test_branded_import.py','tools/master_release/test_restaurants.py','tools/master_completion/test_restaurants.py','tools/master_completion/grocery_test_off.py','tools/test_asset_stamps.py']:
 subprocess.run([P,'-X','utf8',test],check=True)
for test in ['tools/master_release/test-branded-search.cjs','tools/master_release/test-branded-integrity.cjs','tools/master_release/test-diary-meals.cjs','tools/master_completion/test-source-ui.cjs']:
 subprocess.run(['node',test],check=True)
