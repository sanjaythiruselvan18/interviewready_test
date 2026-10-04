# Verification and release handoff

## Passed in this workspace

- 12 Python tests: complete five-question interview, Tamil draft persistence, question relevance in demo mode, repeated-request idempotency, free-credit enforcement after deletion, failed-generation refund, cross-account access denial, three-attempt limit, account-deletion cascade, rejection of unverified payment claims, simulated verified billing-period renewal, malformed live feedback rejection, login/logout, and HTTP public routes with stale/empty authorization. Some tests cover multiple assertions.
- TypeScript strict type checking (`tsc --noEmit`).
- Expo dependency compatibility check (`expo install --check`).
- Metro production export for Android, iOS and web. Native exports generate JavaScript/Hermes bundles; they are not signed APK/IPA files.
- Chromium automation at a 390 × 844 phone viewport: onboarding → register → home → paste JD → five answers → follow-up → reload → resume saved draft → feedback → retry answer → compare attempts → history → plans. No browser JavaScript exceptions in the completed flow.
- Visual inspection of home, interview, feedback and pricing screenshots. Fixed literal newline rendering, an empty-authorization startup bug, and retained scroll position between screens during this review.

The browser automation is in `tests/browser.cjs`. Install Playwright and Chromium in a test environment, then run the script from the project root. `PLAYWRIGHT_MODULE` and `PLAYWRIGHT_CHROMIUM` optionally override the module and executable locations. It starts local API/static servers on ports 8000 and 8081 and uses a temporary database. Screenshots are in `docs/screenshots/`.

## Not verified here

- Native installation, signing, device permission prompts, real microphone recording, background interruption and speaker routing on physical Android/iOS devices.
- Live OpenAI transcription, Tamil/Hindi semantic accuracy, mixed-language rewriting, factual fidelity or production latency. No live AI credentials were supplied.
- Real purchases, renewals, refunds, cancellation, account transfer and restoration in Apple/Google sandboxes. Billing tests use simulated provider responses; no purchase was made.
- Public hosting, email verification, password recovery, load tests, accessibility with a screen reader, or app-store review.

## Required before public launch

1. Set up a hosted HTTPS API with persistent protected storage, backups, monitoring and request limits. Use a single process for this reference SQLite server, or move concurrency handling and persistence to a production stack.
2. Set live AI credentials and evaluate all three languages using representative answers, including short answers, missing metrics, entry-level candidates and prompt-injection attempts. Review rewrite faithfulness; do not invent claims to make examples sound stronger.
3. Configure store products and RevenueCat offering/package mapping. Add authenticated webhook handling and exercise refund/revocation behaviour. Confirm original-account restoration for the consumable seven-day pass. Check the overlapping-plan behaviour described in README.
4. Add verified email/password recovery and stronger trial-abuse prevention before opening public registration. Rate limits alone do not enforce one free trial per person.
5. Publish actual privacy/terms/support URLs and set the environment values. Define retention, provider handling and backup deletion policy; complete store privacy disclosures based on the services actually deployed.
6. Test real devices: deny/revoke microphone permission, two-minute timeout, empty transcription, airplane mode during submission, interrupted recording, background/relaunch, failed payment verification and restore after reinstall.
7. Build signed Android/iOS binaries, add production branding/store assets, configure store listings, and submit for review under your developer accounts.

The demo remains clearly marked and never grants paid access based on a client-side toggle. It must not be marketed as having live AI translation or live payments enabled until those services are configured and tested.
