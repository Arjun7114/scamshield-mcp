# ScamShield — Friction Log

Developer-experience friction encountered while building ScamShield for the Amazon Developer Hackathon (Alexa+ track). Format per entry: task, steps, expected vs. actual, severity, workaround, suggestion.

## 1. Connecting a self-hosted MCP server to Alexa+
- **Task:** Create an Alexa+ add-on from my MCP server via the developer console.
- **Steps:** Registered an Amazon developer account (India), verified identity, opened Alexa+ Developer Console → Create add-on.
- **Expected vs. actual:** Expected an add-on creation UI; got a "Coming Soon" page.
- **Severity:** High (blocked the primary integration path for my region).
- **Workaround:** Used the hackathon's sanctioned simulated-experience web-app path — a real MCP server plus a web client that calls it exactly as Alexa+ would.
- **Suggestion:** State regional/account availability for the add-on console in the quickstart, and replace a bare "Coming Soon" with a clear "not yet available in your region" message.

## 2. Installing the Alexa AI CLI on Windows
- **Task:** Install `@alexa-ai/cli` to deploy an add-on.
- **Steps:** Followed "Set Up Your Development Environment."
- **Expected vs. actual:** Expected a cross-platform install; the docs list only macOS/Ubuntu, and install routes through a private AWS CodeArtifact registry requiring IAM AssumeRole setup.
- **Severity:** Medium.
- **Workaround:** Would require WSL; deprioritized in favor of the simulated path.
- **Suggestion:** Document Windows/WSL explicitly and offer a simpler install (public npm package or one-command installer) instead of per-user CodeArtifact auth.

## 3. Using Bedrock on a new account
- **Task:** Call Nova Micro from the Bedrock playground/API as the production AI brain.
- **Steps:** Opened the playground, ran a prompt; tried again a day later.
- **Expected vs. actual:** Expected a response (serverless models auto-enable); got "ThrottlingException: too many tokens per day" repeatedly on a barely-used account.
- **Severity:** High (blocked the AWS Builder integration).
- **Workaround:** Ran the AI layer locally on Llama 3 via Ollama; kept the Bedrock backend pluggable for a later swap.
- **Suggestion:** Surface the actual daily quota and a direct "request increase" link in the throttling error, and give new accounts a small but usable default Bedrock quota.

## 4. MCP Python SDK version churn
- **Task:** Build a Streamable HTTP MCP server and client from online examples.
- **Expected vs. actual:** Expected examples to match the installed SDK; SDK v2 renamed core classes (`FastMCP` → `MCPServer`, `streamablehttp_client` → `streamable_http_client`), so most tutorials fail with import errors.
- **Severity:** Low.
- **Workaround:** Inspected the installed package's actual API to find the correct names.
- **Suggestion:** Add a prominent v1→v2 migration note and update the official quickstart examples.