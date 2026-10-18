# GetMacros iOS foundation

This is a real Capacitor 8.5.3 iOS project generated with the official CLI. It is **not an App Store release**. No native compilation, signing or simulator execution has been possible in the Windows workspace.

The publication stays static and crawlable. `native_prepare.cjs` copies the current public HTML and hashed assets into an app-only bundle; it does not rewrite the website or require a remote JavaScript application. The development source is the repository, not a live webview of getmacros.net.

## Rebuild from the current website

From `native/app`, with Node 22+ and pnpm available:

```sh
pnpm install --frozen-lockfile --ignore-scripts
pnpm run prepare:web
pnpm exec cap sync ios
pnpm run check
```

On a Mac with Xcode 26 or later:

```sh
pnpm exec cap open ios
# Or validate an unsigned simulator build:
xcodebuild -project ios/App/App.xcodeproj -scheme App \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath ios/DerivedData CODE_SIGNING_ALLOWED=NO build
```

Select an installed simulator or physical device in Xcode. The application's supported deployment target is **iOS 16.4**, above Capacitor's SDK minimum. This covers the shared interface's native dialogs, `:has()` selection styling and the grocery reader's `DecompressionStream` gzip support. The generated Swift dependency package uses major iOS 16; every application/project build configuration explicitly requires 16.4. `net.getmacros.app` is a provisional bundle identifier, **not verified registration or ownership**. Set the actual team and registered identifier before physical-device distribution. No team, certificate, provisioning profile or membership has been supplied.

## What is implemented

- Actual `.xcodeproj`, Swift Package Manager runtime reference pinned to 8.5.3, launch screen, current brand icon and local-origin `WKWebView`.
- Bundled HTML, models, calculators, source notes, reference foods and restaurant records. The ~692,000-profile branded-food catalogue is **not bundled**. Its requested static shards use an explicit HTTPS source and a bounded 64 MiB local cache; previously fetched shards remain usable when the request fails.
- The existing diary remains in local IndexedDB, preserving historical nutrient snapshots and entry IDs. A validated, atomic, protected Application Support archive mirrors mutations; it can restore the diary if the web store becomes empty. The archive is excluded from automatic device-cloud backups. Removing the app removes it.
- Native Files backup export and file import, with a 20 MB maximum, native JSON-envelope checks and the exact same `food-core.js` record validation before importing.
- Explicit Safari-to-app migration: export JSON in Safari, then choose **Preferences & backups → Import Safari backup** in the app. This merges existing IDs and does not pretend Safari and WKWebView share storage. A cancelled or invalid import leaves the diary unchanged.
- System sharing for public GetMacros links. Official external references open through the native external-link bridge; non-HTTPS web schemes and arbitrary native paths are rejected. There is no arbitrary file-access bridge.
- Safe-area styles, inherited theme and reduced-motion behavior, manual barcode lookup, existing offline reference/restaurant search, local recent foods, favorites and saved orders.
- Web ad-placement adapters, external script tags and service-worker installation promotion are removed from bundled HTML. No advertising, tracking, account, camera, microphone, location, HealthKit or push SDK was added.

## Tests and limits

`node tools/flagship_release/native_test.cjs` validates project wiring, source origin, permissions, privacy manifest, bundle scope and schema handoff. `native_browser.cjs` exercises actual generated web assets with a **simulated native bridge** in Edge; it does not test Swift or iOS.

Before TestFlight, complete `docs/flagship-release-2026-10-18/ios/readiness.md`: native compilation, physical-device update retention, locked-device interruptions, actual Files picker, share dismissal, WKWebView keyboard/safe areas, real offline use and memory measurements. Saved restaurant notebook migration remains separate from diary JSON; do not imply the diary export contains it. Optional camera barcode scanning is not implemented; manual entry remains available and no camera permission is requested.

The package's app privacy manifest describes the APIs/SDK behavior implemented here. It is not a completed App Store Connect privacy label. Verify production hosting access-log retention and the final network trace before answering Apple's collected-data questions. Public app-specific support/privacy text, App Store screenshots and the final binary privacy report are release gates.

Do not publish an App Store badge or install promotion from this scaffold. Do not submit to Apple without owner authorization.
