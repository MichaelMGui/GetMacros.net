# Journey readiness — GetMacros

Checked **19 October 2026**. This is a preparation audit, **not an eligibility decision or an application**. No GA4, Search Console, Journey, AdSense or Cloudflare account was connected or inspected. Session qualification, traffic integrity, engagement, account standing and approval remain unverified.

## Current program rules

The official [application requirements](https://www.mediavine.com/application-requirements/) specify at least **1,000 sessions from Tier 1 markets in 30 days**, including the U.S., Canada, U.K. and Australia. The [Journey minimum requirements](https://journeymv.zendesk.com/hc/en-us/articles/24633185741723-Journey-Minimum-Requirements) also require connected GA4, original brand-safe content, engagement and continuing maintenance; the threshold alone does not establish acceptance. A visitor increase, pageview count or Cloudflare request count is not proof of qualifying sessions.

[Grow is optional](https://journeymv.zendesk.com/hc/en-us/articles/54637967339163-Journey-by-Mediavine-What-s-New). There is no requirement to install Grow for 30 days before applying under the current process. Old posts advising otherwise are superseded by current official guidance.

## Readiness checklist

| Requirement | Status | Evidence and next action |
|---|---|---|
| Qualifying 30-day sessions | **Not Verified** | No authorized GA4 export. Obtain the exact date range, timezone and eligible-country session report. Do not use users or pageviews as substitutes. |
| GA4 installed on this release | **Needs Work** | All 468 final public HTML files contain zero GA4/GTM loaders. Browser requests confirm a separate Cloudflare Web Analytics beacon, not a GA4 property. No GA4 measurement ID has been supplied or invented. |
| Correct property connected to Mediavine | **Blocked** | Requires owner-controlled GA4 and Mediavine accounts. No OAuth or connection was attempted. |
| Measurement duplication | **Not Verified** | No GA4 loader exists in the audited source. Recheck browser requests, Realtime/DebugView and one pageview per navigation after an authorized installation. |
| Traffic sources, country/device mix, engagement | **Not Verified** | No acquisition, landing-page or engaged-session report was available. International database coverage is not audience evidence. |
| Bots, paid/incentivized traffic or testing visits | **Not Verified** | No suspicious-traffic conclusion can be made from repository code. Compare acquisition/engagement reports and permitted hosting evidence; exclude development traffic appropriately. |
| Original, useful content | **Pass — scoped release checks** | The 29 new authored guides contain distinct source-backed comparisons, portion calculations or tested logging instructions. Source, arithmetic, overlap and integrated browser checks are recorded individually. Review was AI-assisted engineering/editorial review, not medical or dietitian review. This does not predict Journey's content assessment. |
| Brand safety and health-sensitive claims | **Not Verified** | The editorial policy disclaims medical review and fabrication. Provider review and appropriate scrutiny of health-sensitive claims have not occurred. |
| Image permissions | **Needs Work** | Seventeen original category SVGs, original inline botanical art and source-comparison charts have provenance or authored source. Exact meal photographs remain unavailable; illustrations are labeled. Historical restaurant-logo raster rights remain unresolved and those assets stay unused. Source-evidence pictures are not public artwork. |
| Navigation and mobile reading | **Pass — scoped browser checks** | Every public route was rendered; representative families were checked at five widths and four themes, with real screenshots and interaction traces. Text enlargement, keyboard-reachable tables, native-dialog focus and reduced/calm motion were checked. This is not a WCAG conformance certification or provider approval. |
| About, Contact, Privacy, Terms, Editorial Policy, Corrections | **Pass — presence** | All eight inspected trust/policy destinations, including Sources and Accessibility, exist and are linked from the homepage. This does not certify legal sufficiency or complete accuracy. |
| Policy accuracy | **Pass — corrected release copy** | The stale About count was removed and the October 4 Sources snapshot is explicitly historical. Privacy describes the browser-observed Cloudflare beacon and separates it from GA4 sessions. Cloudflare account configuration and legal sufficiency remain unverified. |
| Google account/policy standing | **Not Verified** | A previously reported AdSense content rejection is not evidence of an account ban. Actual account notices and restrictions were not accessible. |
| Static-site platform compatibility | **Pass — technical path** | Current [non-WordPress instructions](https://journeymv.zendesk.com/hc/en-us/articles/24188199109403-How-To-Install-The-Journey-Script-on-Non-WordPress-Sites) support manually inserting the supplied site-specific head script. GitHub Pages can serve it; final acceptance remains Journey's decision. |
| Safe integration point | **Pass — existing local contract** | `js/ad-placements.js` defaults to disabled with unknown consent and no adapter. Four runtime contract tests pass. No production ad script was added. |
| Advertising separation | **Pass — baseline source placement** | The 33 existing placement hosts are `article-after-content`, on editorial pages. None are in the diary, quiz, calculator or games. This is not approval of future provider placements. |
| Consent and future provider disclosures | **Blocked for activation** | The disabled adapter gate is not a certified CMP. Actual provider configuration, required disclosures, consent implementation and geographic behavior must be tested before activation. |
| Correct supplied script / ads.txt | **Blocked for activation** | Journey has supplied neither in this session. Existing genuine AdSense ownership metadata and ads.txt were preserved; no Journey seller IDs were fabricated. |
| Identity and launch authorization | **Blocked for activation** | Owner must review terms and complete the provider's identity process. No application, terms acceptance, biometric step or launch was attempted. |

## Evidence

- [Local source summary](../ultimate-release-2026-10-19/technical-monetization-audit-baseline.json) and [page-by-page audit](../ultimate-release-2026-10-19/technical-page-audit-baseline.csv): 439 HTML files, 436 indexable canonical sitemap entries; no duplicate indexable titles/descriptions, invalid JSON-LD, missing image alt attributes or broken reciprocal hreflang found by this parser. The noindex 404 deliberately has no canonical.
- [Production HTTP capture](../ultimate-release-2026-10-19/live-measurement-audit.json): six real URLs returned 200; no GA4, ad loader or Cloudflare Web Analytics beacon in the HTML. A Cloudflare security appendix was present. This is not a browser network trace or evidence about dashboard analytics.
- `node --test tools/ultimate_release/journey_runtime_test.cjs`: **4 passed**. Checks cover disabled/consent gates, placement-only adapter input, revocation/late responses and provider-free product events.
- [Prior image rights review](../flagship-release-2026-10-18/images/rights-review.md). Public accessibility of an image or nutrition source is not an image license.

## Authorized onboarding, when evidence and approval exist

Follow the [current launch instructions](https://journeymv.zendesk.com/hc/en-us/articles/23745987278363-Journey-From-Application-to-Launch): use the single Mediavine application, connect the correct GA4 property and inspect actual traffic. After approval, the owner reviews terms and privacy details; engineering installs only the site's supplied script and ads.txt through the approved release workflow. The owner completes Stripe identity verification. Verify provider checks, consent, performance and placements before choosing launch. No separate Google MCM approval is described for Journey's current process.

Keep ad delivery away from selections, food logging, body measurements, games and calculator controls. Do not transmit diary entries, notes, raw searches, individual targets or inferred health information to advertising. Any future GA4 installation needs sanitized page locations, appropriate consent and a private-input exclusion test. The existing in-page event bus carries only whitelisted action names and a version number; it is not currently an external analytics connection.

**Eligibility status: not established.** The outstanding account evidence cannot be supplied by a build, design review, page count or this report.

## Integrated evidence update

The final source audit covers **468 public HTML routes and 465 indexable/sitemap pages** after adding 29 source-checked articles. The browser network capture in `docs/ultimate-release-2026-10-19/after/browser-results.json` confirms that Cloudflare’s live Web Analytics beacon loads on both the homepage and food diary, despite being absent from the passive HTTP captures. The privacy notice now describes that observed beacon and distinguishes its reports from GA4 sessions. No GA4 tag was found, and no account/property/audience access was provided. Cloudflare account settings and consent/legal sufficiency were not certified by this engineering audit.

The About page’s stale whole-site count and the Sources page’s historical-snapshot wording have been corrected. New exact meal photographs remain unavailable: two new original category SVGs supplement the existing 15, with explicit illustration labels. Source evidence images are not republished as licensed photography. These implementation updates do not establish Journey acceptance, qualifying sessions, indexed pages or ad revenue.
