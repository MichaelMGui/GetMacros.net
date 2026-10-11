# GetMacros food-service adapter

Implemented separately from the existing GitHub Pages frontend. No production service, provider account, native app distribution, cloud diary sync or credentials have been provisioned.

Node 24+ is required for the SQLite database. `npm install` in this directory installs the image decoder; `node food-index.cjs` imports the reviewed public food snapshots into `private/foods.sqlite`. Then `npm start` runs the service. The published static site excludes this directory. Never expose `private/` over HTTP.

The service uses the Responses API for structured food candidates and the audio transcription endpoint for push-to-talk. It does **not** ask a model for nutrient totals. Candidate IDs come from the SQLite FTS index, restricted to the selected restaurant market. Every amount and source is reviewed in the browser before local saving. Unspecified quantities require clarification. Typed corrections produce a new review draft; they do not automatically mutate a diary entry.

Production activation requires all of the following:

- Owner-approved hosting and provider spending limits, with HTTPS and an approved exact frontend origin. Binding, proxy configuration and persistent private storage must be reviewed for that host.
- Provider credentials kept in server secrets; explicit food and transcription model names chosen after measured recognition, language, portion, latency and cost evaluations.
- A persistent session secret, a reviewed daily request cap, and host-level body/connection/rate limits. Do not trust arbitrary forwarded-IP headers. Behind a proxy, configure the verified remote address correctly; the present default uses the direct connection address.
- Review/update the public privacy disclosure, retention settings and explicit submission consent. `store:false` is used; it is **not** a guarantee of zero provider retention. See [current OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data).
- Set the reviewed frontend API URL and `aiEnabled:true` in `js/app-config.js` only after the service passes production checks. No DNS or hosting changes were made for this implementation.

The request cap bounds the number of provider calls, not a guaranteed dollar amount. Output limits, image dimensions and audio size limits reduce exposure; accurate budgeting requires actual model pricing and workload measurements. Quotas persist in SQLite. There is no fake account system or cloud-sync endpoint. No diary history or private note is sent to the service.

Uploads are processed in memory, decoded, resized and stripped of metadata. No image, audio, food description or draft is written to application storage. Ordinary hosting/proxy logs need separate review. The quota database stores day, request count and a keyed address hash; this is not an analytics export or a user profile.

Tests: `node --test test/service.test.cjs`; source arithmetic: `node ../tools/product_release/test-food.cjs`. The tests inject provider responses. Real provider recognition/cost evaluation is unperformed because no account/key is configured.
