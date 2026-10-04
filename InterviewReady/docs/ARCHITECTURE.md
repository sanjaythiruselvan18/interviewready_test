# Implementation decisions

The mobile app uses React Native/Expo for one Android and iOS codebase. The same screens export to the web for evaluation. Screens use navy, teal and white, large recording controls, editable text inputs and a five-step progress bar. Navigation has Home, History and Plans, with settings in the header.

The backend is a minimal Python 3.12 HTTP API with SQLite persistence. Passwords use salted scrypt. Bearer tokens are random, stored hashed on the server, and expire after 30 days. Native tokens use SecureStore. The local web demo uses sessionStorage. Every session operation checks account ownership. Rate limits cover authentication, generation, feedback and transcription. Database mutations and same-account requests are serialized for this single-process deployment.

Drafts are stored locally and synchronized to the server. A saved answer is an immutable attempt in its question's attempt list. A follow-up invites the user to expand the answer, consuming another attempt. Finished interviews can be reopened to practise any answer up to three attempts. Starting a new interview consumes a new credit. Existing session feedback can be read after a paid plan expires.

The app calls the server for question generation, feedback and transcription. AI keys never ship in the client. Question/feedback calls ask for JSON and validate shape before persisting. Transcripts and supplied job descriptions are marked as untrusted data in the prompt. Live output is not guaranteed factually correct; the UI explicitly asks users to verify rewritten answers. No regional-accent score is produced.

Billing uses the RevenueCat native SDK and a server-to-server subscriber query. The server never trusts client claims of payment. The monthly usage bucket is tied to the verified purchase period; the pass bucket is tied to the transaction. Receipt verification is delegated to RevenueCat's Apple/Google integration. App-store tax, local pricing and renewal terms come from store products. The configurable numeric fallback prices are illustrative until store offerings load.

Known production boundaries: this is a source MVP, not a managed production service. A launch needs native signing and store review, HTTPS hosting, verified provider retention settings, password recovery and email verification, abuse prevention across new accounts, monitored quota/rate-limit behaviour, deletion-aware backup retention, and tested webhooks/receipt lifecycles. These are described explicitly so a runnable demo is not confused with a public release.
