# InterviewReady

A runnable first implementation of the Android/iOS interview coach, built with Expo React Native and a Python/SQLite API. A prebuilt browser demo is included so you can try the complete typed interview journey without installing Node or providing API keys.

**Status:** tested demo and source implementation, not a published or store-ready app. Live transcription, AI translation/rewriting and store purchases are integrated in code but need your service credentials, product setup and real-device verification. No APK or signed iOS application is included.

## Try it on your computer

1. Install Python 3.12 or newer if needed.
2. Extract this folder.
3. In Terminal, enter this folder and run:

```sh
python3 run_demo.py
```

Open **http://localhost:8081** if your browser does not open automatically. Create an account with any valid-format email and a password of at least 10 characters. Use fictitious details for evaluation. No email is sent in this implementation.

The local demo includes onboarding, sign-in, role/JD setup, five questions, spoken questions, typed answers, follow-ups, saved drafts, feedback, retries, history, plan screens and deletion. It grants one free interview per account. Deleting a session does not refund that credit. Demo feedback uses transparent rules and preserves the original answer; it does not pretend to translate or assess answers using AI. Real purchases are disabled. Demo data remains in `demo.db` until you delete it or remove your account.

## Native development

Requires Node 20.19+ (tested on Node 24), npm and Python 3.12+. Native iOS builds require macOS/Xcode or EAS; Android builds require the Android toolchain or EAS.

```sh
cd mobile
npm ci
cp .env.example .env
# Set EXPO_PUBLIC_API_URL to your backend URL.
npm start
```

In another terminal:

```sh
cd server
python3 app.py
```

A physical phone cannot use `localhost` to reach your computer. Use a reachable HTTPS backend or an appropriate local development network address. Android emulator host access normally uses `10.0.2.2`. For store billing, use a native development build, not Expo Go. The app has EAS profiles; link your own EAS project before building. Add `expo-dev-client` using `npx expo install expo-dev-client` if using the development-client profile, or use the preview profile for internal installation.

```sh
cd mobile
npx expo run:android
# On a Mac:
npx expo run:ios
# Or, after configuring your EAS account/project:
npx eas-cli build --platform all --profile preview
```

Keep all secret keys in backend environment variables. The RevenueCat client keys are public SDK keys, not secret API keys.

## Enable live coaching

Set environment variables from `server/.env.example` in your host or shell. The Python process does not automatically load `.env` files. For local shell use, after filling in a trusted file:

```sh
cd server
set -a
. ./.env
set +a
python3 app.py
```

Set `DEMO_MODE=false`, `OPENAI_API_KEY`, `OPENAI_MODEL` and `TRANSCRIPTION_MODEL`. The default live models are configurable. Deploy behind HTTPS with a persistent encrypted volume, backups, request-size/time limits and restricted origins. Do not expose the built-in HTTP server directly to the public Internet. This reference server uses one process and account-level mutation locks; do not run multiple workers against this SQLite implementation.

The backend generates five questions from the job description and selected experience. It accepts English, Tamil, Hindi and mixed-language answers, then asks the model to rewrite them in professional English without adding facts. All live question/feedback responses are shape-checked. AI outputs can still make mistakes and are labelled for user review. Accent and pronunciation are not scored from a transcript.

Audio is held in request memory, forwarded for transcription and not written to the backend database. The client deletes successful recordings; failed recordings can be retried or discarded. Recordings interrupted by an app crash may remain in OS cache. Provider retention is separate and must be reflected accurately in your published privacy policy.

## Configure payments

Use your own App Store Connect, Play Console and RevenueCat projects.

| Setting | Seven-day pass | Monthly subscription |
| --- | --- | --- |
| Launch price | ₹199 | ₹399 |
| Default interview allowance | 10 | 30 per billing period |
| Default product ID | `interviewready_week` | `interviewready_monthly` |
| RevenueCat package identifier | `week` | `month` |
| Store configuration | One-time consumable purchase; backend grants 7 days | Auto-renewing monthly subscription |

Create these as custom packages in the current RevenueCat offering. Product identifiers may be changed through server configuration. The client selects the package identifiers `week` and `month`; maintain that mapping when configuring offerings.

The one-time pass must be configured as consumable if users can buy it again. Its history is recovered through the signed-in app user's RevenueCat server record. Store restoration alone does not restore consumed products to an unrelated app account. Configure RevenueCat restoration/transfer policy to keep purchases associated with the original app user; test original-account restoration on both platforms. A deleted app account cannot recover a consumed pass's old identity.

Set `REVENUECAT_SECRET_KEY` on the server, and platform public SDK keys in `mobile/.env`. Purchase and restoration run through the native SDK; the server independently fetches the subscriber record before granting access. Sending a plan name from a client never grants access. If verification fails after a successful charge, the user can retry **Refresh verified access** or **Restore purchases** without repurchasing.

Actual store pricing is shown when available. Changing `WEEK_PRICE` or `MONTH_PRICE` only changes the fallback launch display; change prices in both stores as well. Allowances are backend-configurable. The pass expires after seven elapsed days. Monthly allowances use the verified current purchase period. When both products are active, this implementation uses the access period with the later expiry; credits are not stacked. Test and communicate this behaviour before offering overlapping purchases.

For public release, add signed store/RevenueCat webhook processing for timely refund/revocation handling and robust cancellation/account migration support. The implementation polls RevenueCat for existing paid access when loading the account and starting a session. Test refunds and revocations in each store sandbox before charging users.

## Usage and persistence

- Free: one five-question interview per account.
- Seven-day pass: 10 interviews; monthly: 30 per period.
- Three feedback attempts per question, including an expanded follow-up answer.
- 15 transcription requests per interview, two-minute client recording limit, 3 MB server audio limit. Failed transcription requests count toward this cost limit.
- Repeated identical submission is idempotent; failed question generation refunds its reserved interview credit.
- Session deletion does not reset allowances. Account deletion cascades through sessions, credentials and usage.
- Typed drafts save locally, then sync after a brief debounce; completed answers persist on the server.
- Scores are practice indicators (1–5), not hiring predictions. Past attempts remain visible alongside the latest version.

## Verification

```sh
python3 -m unittest discover -s server/tests -v
cd mobile
npm run typecheck
npx expo install --check
npx expo export --platform web
npx expo export --platform ios --platform android --output-dir native-export
```

See `docs/VERIFICATION.md` for the actual test results and remaining release work. Native JavaScript export is not a signed device build.

## Project map

- `mobile/App.tsx`: nine screens and the native recording/coaching journey.
- `mobile/src/api.ts`: authenticated network requests, secure native token storage and timeout handling.
- `mobile/src/types.ts`: shared UI data shapes.
- `server/app.py`: authentication, database, coaching, transcription, quotas, billing verification and deletion.
- `server/tests/test_api.py`: behavioural tests for the core server flow.
- `mobile/dist/`: prebuilt browser demo.
- `run_demo.py`: one-command local launcher.
- `docs/`: architecture, verification and release handoff.

## Documentation used

- Expo Audio: https://docs.expo.dev/versions/v54.0.0/sdk/audio/
- RevenueCat React Native: https://www.revenuecat.com/docs/getting-started/installation/reactnative
- RevenueCat restoration: https://www.revenuecat.com/docs/getting-started/restoring-purchases
- OpenAI audio: https://developers.openai.com/api/reference/typescript/resources/audio
