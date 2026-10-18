# iOS readiness — 18 October 2026

## Final stable web build packaged

The final preparation includes **439 HTML routes** and the final 10,327-record restaurant registry. The package contains **976 files totaling 141,810,588 bytes**, including `native-build.json`. These are uncompressed web assets, not a signed IPA size or App Store download estimate. The 692,000-profile branded catalogue, uncleared restaurant-logo directory, web advertising files and app-install script are excluded. Grocery requests use the explicit HTTPS source and bounded cache described below.

`native_prepare.cjs` reads and validates the current generated-asset manifest, including the final navigation and liquid-motion assets. Official Capacitor 8.5.3 `cap sync ios` succeeded; every prepared asset has the same hash in the generated Xcode project's public directory. Fourteen scaffold/integrity checks and twelve generated-bundle browser journeys passed. The latter use a **simulated native bridge in Microsoft Edge** and do not execute Swift or WKWebView. The initial Windows-sandbox browser launch failed; rerunning the actual checks outside that sandbox succeeded.

Final app-only fixes place Files import/export under **Backup & restore**, preserve the mobile task-navigation safe-area padding and reject an invalid import without changing entries. Light/dark preference-sheet screenshots were rendered, allowed to settle and manually inspected: `bundle-migration-light-390.png` and `bundle-migration-dark-390.png`. These are browser integration screenshots, not native App Store screenshots.

Machine-readable evidence: [final-bundle-coverage.json](final-bundle-coverage.json), [scaffold-checks.json](scaffold-checks.json), [bundle-browser-checks.json](bundle-browser-checks.json). Final generated-web manifest SHA-256: `b8c4dd92d77c969913b8c387ffb331e816179d89b0f742377bfbc456dc414401`.

Native compilation, simulator execution, signing and on-device retention remain unperformed on this Windows host.

## Supported application feature floor

All four application/project configurations require **iOS 16.4**. The generated Swift dependency package targets major iOS 16; it is allowed to support a lower minimum than the application. [WebKit’s Safari 15.4 release](https://webkit.org/blog/12445/new-webkit-features-in-safari-15-4/) documents native dialog/backdrop and `:has()` support, while [WebKit’s Safari 16.4 release](https://webkit.org/blog/13966/webkit-features-in-safari-16-4/) documents Compression Streams for browser compression/decompression. The latter supports the shared grocery reader’s `DecompressionStream` requirement. This feature-based floor is deliberately above Capacitor’s minimum, and is enforced by the scaffold checks and idempotent project-wiring tool.

The final generated-bundle test also follows the packed GB finder record through meal details to its bundled restaurant guide, checking that compact projection retains the destination URL. Source research and the remaining actual-device limit are in [compatibility-research.json](compatibility-research.json). [source-origin-checks.json](source-origin-checks.json) records real public USDA/OFF manifest responses permitting the `capacitor://localhost` origin; these header checks do not replace an actual WKWebView network test.

| Requirement | Status | Evidence / next action |
|---|---|---|
| Reuse existing nutrition models and formulas | Implemented | The app copies current `js/food-core.js`, calculator logic and real record sources. No parallel arithmetic engine. |
| Actual Xcode project | Generated, not compiled | `native/app/ios/App/App.xcodeproj`; official Capacitor CLI 8.5.3; Swift Package Manager. |
| Native backup/import/share | Source implemented | Two custom Swift files are members of the target; web adapter uses shared schema validation. |
| Local diary and source snapshots | Browser integration tested | IndexedDB plus atomic Application Support archive; no remote diary service. |
| Durable retention across signed updates | Unverified | Install build A, enter real fixture, install build B without uninstalling, compare snapshots and saved orders on physical iOS. |
| Browser → app migration | Explicit implementation | JSON export/import, ID merge, invalid payload rejection. Actual iOS Files picker still requires device test. |
| Offline reference and restaurant browsing | Bundled | App preparation excludes the branded catalogue; includes current reference and restaurant snapshots. |
| Previously loaded grocery data offline | Implemented, browser-tested | Static HTTPS fetch adapter with 64 MiB IndexedDB cache; profile provenance remains visible. |
| Barcode scanning | Manual lookup only | No camera entry point, SDK or permission string. |
| Native sharing / external references | Implemented, bridge simulated | Swift `UIActivityViewController` and `UIApplication.open`; actual iOS dismissal and iPad popover need testing. |
| Theme, reduced motion, safe areas | App styles integrated | Final device keyboard, home indicator, rotation and VoiceOver checks remain. |
| Privacy manifest | Added and target-wired | No tracking domains or collection SDKs; no newly used required-reason API declarations. Verify final archive privacy report. |
| App Store privacy label | Not submitted | Audit static source hosting logs/retention and final binary traffic; local-only diary is not a reason to ignore server logs. |
| Accounts / deletion | No accounts added | Existing local delete removes diary/recipes/settings; native mirror cleared too. Account-deletion policy applies if accounts are later added. |
| App identity / signing | Owner action required | Confirm registered bundle ID, team, developer membership, certificates and provisioning. None invented. |
| Current Xcode compatibility | Requires Mac | Official Capacitor 8 docs specify Xcode 26+; this application requires iOS 16.4. No macOS/Xcode exists in this workspace. |
| Support/privacy destinations | Existing web URLs available; app copy needs review | `https://getmacros.net/contact.html`, `https://getmacros.net/privacy.html`; ensure app-specific policy matches final binary. |
| Store screenshots / review notes | Pending native build | Capture actual iPhone and iPad app screens with fictional diary data; no browser chrome or fabricated native screenshots. |
| App Store review | Not requested | Minimum-functionality and completeness review still applies; a scaffold is not review approval. |

## Current primary guidance inspected

Research date: 18 October 2026. No Apple account or App Store Connect access was used.

- [Capacitor iOS documentation](https://capacitorjs.com/docs/ios): current version 8, native WKWebView, iOS 15+, Xcode 26+ and project-generation workflow.
- [Capacitor environment setup](https://capacitorjs.com/docs/getting-started/environment-setup): current development requirements. Node 24 is available; macOS/Xcode is not.
- [Capacitor privacy manifests](https://capacitorjs.com/docs/ios/privacy-manifest): app and SDK privacy declarations must reflect chosen APIs; manifests are not speculative permission lists.
- [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/): reviewed completeness, privacy, accurate metadata and minimum-functionality requirements. App review remains a separate external decision.
- [Apple App Privacy Details](https://developer.apple.com/app-store/app-privacy-details/): data collection by webviews and partners must be considered; review final source-hosting access logs, not just diary storage.
- [Apple account deletion guidance](https://developer.apple.com/help/app-review/guideline-reference/5-1-1-account-deletion): no account creation exists here. If accounts are introduced, deletion must be available in the app with associated-data handling.

No purchase, signing, simulator build, TestFlight upload, App Store submission or developer enrollment was performed.
