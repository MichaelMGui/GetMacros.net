# GetMacros GA4 connection — October 23, 2026

Uses the existing, owner-account-verified measurement ID **G-MWXSWP6ZGY**.
This is a public website tag identifier, not an API secret. No new property,
account, advertising SDK or Measurement Protocol secret was created.

## Measurement boundary

- Basic consent: no Google tag, data-layer initialization, analytics cookie or
  collection request before affirmative permission. Allow and decline have equal
  prominence; preferences remain available in every footer.
- Consent is stored in `gm-analytics-consent-v1`. A browser exclusion option lets
  the owner exclude their own visits. No IP-based filter was invented or activated.
- Production public-content routes are eligible even with market/campaign
  parameters or anchors. Page addresses sent to Google are always the clean
  canonical pathname; parameter/fragment values are never forwarded. The route
  manifest distinguishes these pages from 32 private/tool routes. Previews,
  automated browsers and Global Privacy Control browsers remain unmeasured.
- Diary, saved foods, finders, calculators, food search, comparisons, order tools
  and contact forms do not load Google Analytics, even with saved consent.
- GetMacros sends `page_view`, trusted `navigation_click` and `outbound_click`.
  Page location is the published canonical pathname, title comes from static
  social metadata, and referrer is reduced to the referring origin. Clicks contain
  only fixed destination categories and header/footer/content placement. No link
  text, clicked URL, selected food, product-event bus, form input, local food
  storage, notes, user identifier or body measurement is forwarded.
- Preferences offer a deliberate Diagnostic mode. It uses separate `gm_qa`
  prefixed cookies, `traffic_type=internal`, `debug_mode=true`,
  `gm_traffic_class=diagnostic` and a `[Diagnostic]` report-title prefix. Standard
  visits use `gm_traffic_class=standard`. Diagnostic events still exist in the
  property and must be excluded when calculating audience totals; All Users must
  never be relabeled as independently verified humans. Browser exclusion remains
  available for owners who do not need to send diagnostic events at all.
- `send_page_view:false` prevents a duplicate config pageview. Google Signals and
  ad personalization are disabled; all advertising consent remains denied.
  Analytics cookies are configured for 90 days. This is not a retention setting
  for data already in the Google account.
- Revocation disables the property, clears this site's `_ga` cookies and reloads
  to unload listeners. Cross-tab revocation is supported. No denied-consent ping
  is deliberately sent by this basic-consent implementation.
- CSP adds only the named Google tag and Analytics endpoints, on public routes.
  Content-addressed assets and the service-worker version update with this release.

This is **public-content, consenting-visitor measurement**, not a census of real
humans or all site sessions. A cookie/session is not proof that someone is human.
Cloudflare visit/request counts and Search Console clicks remain different metrics.
Historical unmeasured sessions cannot be recovered by installing the tag.

## Account configuration and verification

After authenticated browser access returned, Enhanced Measurement extras were
turned off in GA4 and the saved state was verified. This prevents automatic
search/form/history/outbound events from bypassing the site's payload whitelist;
the implementation continues to send deliberate pageviews and safe clicks.
Event-scoped Traffic class and Click destination dimensions were created and
verified. The existing Internal Traffic exclusion filter remains in Testing
mode; no permanent account-side data exclusion was activated. Retention and
Journey's OAuth connection were not changed. Actual audience reports and browser
verification screenshots belong in the private evidence directory, not this
public source repository. A collector HTTP response alone is not proof of
Realtime receipt or of non-test visitors.

No traffic eligibility, Journey approval or ad revenue is established here.
No production ad script or publisher identifier was added.

## Official implementation references

- [Basic consent implementation](https://developers.google.com/tag-platform/security/guides/consent?consentmode=basic)
- [Manual pageviews and Enhanced Measurement distinction](https://developers.google.com/analytics/devguides/collection/ga4/views)
- [GA4 configuration, Google Signals and ad personalization](https://developers.google.com/analytics/devguides/collection/ga4/reference/config)
- [Internal traffic filters and permanent exclusion cautions](https://support.google.com/analytics/answer/10104470)

## Verification

Runtime privacy tests: `node --test tools/analytics_measurement/runtime.test.cjs`.
Generated route checks: `python tools/analytics_measurement/test_build.py`.
Both run in hosted Site quality CI. The browser script defaults to offline
collection; `--live-collector` is an explicit, labeled diagnostic smoke test.
It no longer rewrites the analytics source or invents tracking parameters outside
the application's actual Diagnostic mode. Production and GA4 account verification
use ordinary browser interactions, and all resulting diagnostic visits are
reported separately from audience traffic. Never request a new immutable asset
before Pages reports successful deployment; then probe an uncached query first
to avoid caching a premature 404 at Cloudflare.
