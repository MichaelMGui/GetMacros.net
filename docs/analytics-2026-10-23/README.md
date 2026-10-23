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
- Only clean production public-content routes are eligible. The route manifest
  distinguishes them from the 32 private/tool routes. Queries, fragments, previews,
  automated browsers and Global Privacy Control browsers are unmeasured.
- Diary, saved foods, finders, calculators, food search, comparisons, order tools
  and contact forms do not load Google Analytics, even with saved consent.
- The only event explicitly sent by GetMacros is `page_view`. Its location is the
  published canonical pathname, title is static social metadata, and referrer is
  reduced to the referring origin. No product-event bus, form inputs, local food
  storage, notes, user identifiers or body measurements are read or forwarded.
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

## Account work not verified

The authenticated browser connection was unavailable on October 23. Realtime /
DebugView receipt, Enhanced Measurement stream settings, retention, account data
filters and Journey's OAuth connection have not been changed or confirmed.
In particular, `send_page_view:false` alone does not disable history-based
Enhanced Measurement pageviews in the Google stream settings. The site has no
SPA route tracking or explicit automatic form/search event forwarding; sensitive
tools and URL states are excluded. Review the stream settings in GA4 Admin before
expanding measurement. No claim is made that account-side automatic events were
disabled by repository code.

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
Both run in hosted Site quality CI. Browser verification uses a fresh unauthenticated
test context; no Google account cookies or profiles are accessed. Test traffic is
synthetic and is not evidence of an audience. Deployment and network results are
recorded separately after they are observed.
