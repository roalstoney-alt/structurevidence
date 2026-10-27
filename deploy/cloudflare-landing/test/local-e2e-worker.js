// Local-only Wrangler entry point. It replaces external Turnstile and Access
// calls while retaining the real Worker, D1 binding, migrations, and SQL paths.
// This file is not referenced by wrangler.jsonc and must never be deployed.
import { createWorker } from "../worker.js";

const usedTokens = new Set();
const worker = createWorker({
  authVerifier: async () => ({ email: "local-admin@example.test" }),
  turnstileVerifier: async (token) => {
    if (!token.startsWith("local-valid-") || usedTokens.has(token)) throw new Response("Human verification failed", { status: 400 });
    usedTokens.add(token);
    return { success: true, hostname: "structevidence.com", action: "public-intake" };
  }
});

export default {
  fetch(request, env) {
    return worker.fetch(request, {
      ...env,
      CUSTOMER_CASES_DB: env.CUSTOMER_CASES_DB,
      PUBLIC_ORIGINS: env.PUBLIC_ORIGINS,
      PUBLIC_INTAKE_RATE_LIMITER: { limit: async () => ({ success: true }) },
      ADMIN_UI_AUD: "local-ui",
      ADMIN_API_AUD: "local-api",
      ADMIN_EMAILS: "local-admin@example.test"
    });
  }
};
