"""Editorial and calculator scope repairs applied after page generation."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
for name in ['calculators.html','sources.html','privacy.html','sweat-rate-calculator.html','corrections.html']:
 p=ROOT/name;s=p.read_text(encoding='utf-8')
 if name=='calculators.html':
  s=s.replace('name="age" min="14"','name="age" min="18"')
  if 'id="adult-scope"' not in s:
   s=s.replace('<form class="calc-form" id="macro-form">','<p class="editorial-note" id="adult-scope">For adults 18 and older. This is a starting estimate, not a personal prescription. Pregnancy, breastfeeding, growth and conditions that affect nutrition need individual guidance. <a href="https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner">Read about adult weight-planning limits.</a></p><form class="calc-form" id="macro-form">')
 if name=='sources.html':
  s=s.replace('Every factual claim on this site is sourced from peer-reviewed research, government health agencies, major academic medical centers, or (for athlete-diet stories) established news reporting. This page lists every citation used, grouped by topic.','This page explains the core references behind our nutrition tools. Individual articles and restaurant guides include their own sources, which provide the context for specific claims and menu figures.')
  # Remove obsolete bibliography sections for topics no longer in this library.
  def section(m):
   block=m.group(0)
   if any(x in block for x in ['id="ath1"','General &amp; lifestyle','Micronutrients &amp; supplements','Health &amp; medical','Research methodology &amp; critical thinking']):return ''
   return block
  s=re.sub(r'<section\b.*?</section>',section,s,flags=re.S)
  if 'id="restaurant-method"' not in s:
   method='<section id="restaurant-method"><div class="container"><h2>Restaurant data and rankings</h2><p>Each <a href="restaurant-meal-guides.html">restaurant guide</a> links to the chain’s official nutrition information. Figures describe the named standard build, not every possible substitution. Location, portioning and menu changes can affect your order.</p><p>The meal finder ranks the menu options in our dataset against your chosen preferences. It does not search every item a restaurant sells. Unpublished values stay unknown; the finder excludes incomplete records by default and lets you include them explicitly.</p><p>A high-protein match is not automatically a low-calorie or low-sodium meal. Read the complete numbers and the trade-offs on each result, and check the restaurant’s allergen information before ordering.</p></div></section>'
   s=s.replace('<section class="tight">',method+'<section class="tight">',1)
 if name=='privacy.html':
  s=re.sub(r'The calculators, quizzes, and games use your browser.*?removes it completely\.', 'The current site stores your theme and motion preferences and saved restaurant meals in your browser. Some pages may also remember a language preference. These settings use localStorage on your device; clearing site data removes them. Calculator arithmetic runs in the page without submitting your entries to a GetMacros calculation server.',s,flags=re.S)
  s=s.replace('We don\'t collect names, emails, or any personal information you type in, because there\'s nowhere on the site that asks you to.','The site has no registration form. If you email us, your email provider delivers your message and address to our published contact mailbox.')
  if 'Shared meal-finder links' not in s:
   s=s.replace('<h2>Hosting and basic logs</h2>','<h2>Shared meal-finder links</h2><p>Meal-finder choices can appear in the page URL so you can revisit or share the same filters. Anyone receiving that link can see those choices. URLs may also appear in browser history and hosting logs when requested. Do not put sensitive personal information in a shared link.</p><h2>Hosting and basic logs</h2>')
 if name=='sweat-rate-calculator.html':
  s=s.replace('<p><a href="sweat-rate-calculator.html">Read the complete measurement guide</a> · Understand overhydration · Hydration collection</p>','<p><a href="sources.html">Review the site’s sources and calculation methods</a>.</p>')
 if name=='corrections.html' and 'id="recipe-correction"' not in s:
  s=s.replace('<div class="container policy">','<div class="container policy"><section id="recipe-correction"><h2>September 7, 2026 — recipe and comparison calculators</h2><p>The recipe tool previously combined a fixed-batch portion calculation with instructions to scale all ingredients. Those are different operations. The tool now lets readers choose either operation and shows the correct per-serving result for each. The protein-cost calculator now identifies equal costs correctly, and measurement buttons in the macro calculator convert the entered value.</p></section>',1)
 if name=='calculators.html':
  note=re.search(r'<p class="editorial-note" id="adult-scope">.*?</p>',s,flags=re.S)
  if note:
   s=s.replace(note.group(0),'').replace('<div class="calc-wrap">',note.group(0)+'<div class="calc-wrap">',1)
 p.write_text(s,encoding='utf-8')
