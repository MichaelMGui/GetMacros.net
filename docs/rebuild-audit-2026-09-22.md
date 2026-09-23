# GetMacros rebuild audit — 22 September 2026

Owner reports AdSense rejection for “low quality content.” This broad category does not identify specific offending URLs; findings below are independently observed, not a claim to know Google's internal decision.

## Priorities

1. **Confirmed: competing presentation and unnecessary delivery weight.** Pages include numerous generations of styles, inline CSS and JavaScript which can inject older styles after load. Replace the delivered cascade with one responsive publication stylesheet, preserving tool hooks and URLs.
2. **Confirmed: meal macro information is incomplete.** The central `f` field is fiber, not fat; results display calories, protein, fiber and sodium. Add explicit carbohydrates and fat fields without deriving fat from leftover calories. Display unverified values honestly. Preserve existing source records and dates.
3. **Confirmed: ad requests load immediately.** Both HTML and legacy `main.js` load AdSense. No certified CMP integration is verifiable in repository code. Pause ad serving while retaining the supplied ownership meta tag and matching ads.txt entry. Owner must configure/verify account-side consent before activation; this is not itself evidence of the stated content rejection.
4. **Content review:** preserve sourced guides and working tools; replace the slogan-heavy homepage with concrete meal, restaurant, calculator and educational routes. Review pages individually, improve decision examples and clarify regional menus and serving definitions. No broad deletions or noindex changes.
5. **Publisher transparency:** keep GetMacros authorship, supplied contact address and original review dates. No invented qualifications, medical review, personal testing or updated-data claims.
6. **SEO:** preserve the 72 canonical URLs in the sitemap and established internal destinations. Historical 441-indexed-page screenshots do not establish today's indexed count. Current Search Console exports/account access are not available in this turn.

## Official guidance checked

- Google Publisher Policies: https://support.google.com/adsense/answer/10502938
- Required privacy disclosures: https://support.google.com/adsense/answer/1348695
- Certified CMP requirements for EEA, UK and Switzerland: https://support.google.com/adsense/answer/13554116

## Photography

`images/editorial-salad.webp`: Anna Pelzer, “Bowl of vegetable salads,” https://unsplash.com/photos/bowl-of-vegetable-salads-IGfIGP5ONV0 — free Unsplash License, https://unsplash.com/license, verified and downloaded 22 September 2026. Local resized WebP delivered from the site. Used as general food photography, not as a picture of an official restaurant order. Attribution included beside the image.

## Account actions outstanding

Confirm the exact full rejection notice if it includes more than the category; verify AdSense account ownership/status and authorized ads.txt seller detail in the account; configure a Google-certified CMP before enabling ads; review Cloudflare's injected analytics and its actual regional behavior. These cannot be verified solely from static repository files.
