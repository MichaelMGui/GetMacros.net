# GetMacros AdSense and SEO recovery report

## Outcome

GetMacros now has one explicit product purpose: help people find fast-food meals that fit calories, protein and practical goals, then provide the tools and focused education needed to understand those numbers. The indexable footprint was reduced from 448 pages to 72; 397 HTML URLs were removed rather than redirected to unrelated destinations.

## What was wrong

- The homepage promoted article quantity instead of the site's distinctive restaurant data and tools.
- Hundreds of broad medical, academic-biochemistry, trend-diet, quiz, game and worksheet pages diluted topical focus.
- The calculators hub mixed useful macro tools with condition-specific planners.
- Restaurant guides exposed only a small portion of the central data and repeated near-identical editorial copy.
- Primary navigation and partial translations made the product look broader and less complete than it was.

## Structural changes made

- Established an explicit allowlist around healthy fast food, core tools, trust pages and a curated supporting guide library.
- Removed 397 out-of-scope HTML URLs from navigation, search, sitemap and the published file tree. No mass homepage redirects were created; URLs without a true equivalent correctly resolve as missing pages.
- Removed partial Spanish and French footprints and stale hreflang references.
- Simplified the site-wide navigation to Healthy Fast Food, Healthy Order Match, Macro Calculator, Nutrition Guides and About, with Search as a utility action.
- Rebuilt client-side search and XML sitemap exclusively from surviving indexable content.
- Changed the routine build so removed quizzes, games, glossary entries and broad articles cannot be regenerated.

## Homepage and healthy fast food

- Rebuilt the homepage around real repository data: 83 tracked options across 15 chains, a real meal example, goal pathways, cross-chain rankings, chain access, a compact macro calculator and transparent methodology.
- Removed the “340 guides” claim and broad condition/topic directories.
- Rebuilt the Healthy Fast Food hub with explicit search intent, complete-meal safeguards, cross-chain protein/calorie/fibre/sodium comparisons, goal definitions, restaurant directory and limitations.
- Kept substantial static meal-finder rankings and explanatory content available before JavaScript interaction.

## Restaurant pages upgraded

- Rebuilt all 15 chain guides from `js/meal-data.js`, exposing all 83 tracked menu records rather than teaser rows.
- Added chain-specific titles, H1s, introductions and ordering guidance.
- Added full nutrient tables, high-protein, substantial lower-calorie, higher-energy and supported vegetarian picks.
- Added transparent protein grams per 100 calories with its formula and a warning that it is not a health score.
- Preserved official restaurant sources, an August 2026 checked date, missing-value semantics and menu-change disclaimers.

## Tools, guides and trust

- Focused the calculators hub on macro, label, recipe, budget, hydration and restaurant-decision tools.
- Rebuilt the article hub as a curated guide library tied to macros, food decisions, meal building, training and eating out.
- Updated About with truthful editorial ownership, data methodology, independence, limitations and corrections information.
- Standardized footer access to About, Editorial Policy, Sources, Corrections, Privacy, Terms, Accessibility and Contact.
- Preserved the verified AdSense publisher ID and `ads.txt` record; obsolete third-party ad code is rejected by validation.

## SEO and technical changes

- Aligned the homepage, Healthy Fast Food hub, Healthy Order Match, directory and 15 restaurant pages with natural search intent.
- Regenerated canonical sitemap and search coverage from the final indexable set.
- Removed broken internal links and incomplete-language alternates.
- Added or preserved unique title, description, canonical, Open Graph, Twitter and valid JSON-LD requirements through automated validation.
- Continuous integration now performs a deterministic rebuild before validating links, metadata, structured data, accessibility basics and advertising configuration.

## Remaining legitimate risks

- AdSense approval cannot be guaranteed; Google makes the decision and may consider account history, traffic, policy signals and crawl timing outside this repository.
- Restaurant menus change. The site links to official sources and must continue periodic human rechecks.
- The available in-app browser runtime did not initialize during this work, so automated source/mobile CSS checks replace a final interactive browser pass. A production-device spot check remains prudent after deployment.
- No Search Console verification token was present in this repository. Nothing was removed; if verification is DNS-based or injected by hosting it remains external.

## Manual actions requiring external access

- Deploy the rebuilt files, submit the focused sitemap in Search Console and request recrawling for the homepage, Healthy Fast Food hub and restaurant guides.
- Confirm the AdSense consent message/CMP in the AdSense account for EEA, UK and Switzerland; this setting is account-side, not safely implementable from static source alone.
- Reapply for AdSense only after Google has crawled the new focused site and production smoke tests pass.
