# SE-FRR-001 Pre-existing Worktree Manifest

Recorded: 2026-09-25  
Original checkout: `/Users/roal/Documents/ChatGPT/structevidence`  
Branch: `main`  
HEAD: `2356c9327ba5b40995435eca952edd706fd944fc`

`ORIGINAL_WORKTREE_MODIFIED_BY_SE_FRR = NO`

This statement applies to the pre-existing application, research, generated-output, and unrelated project files listed below. Phase 0 and Phase 0.5 added only controlled audit reports under `docs/community/`; they did not edit, stage, commit, revert, stash, delete, or relocate any pre-existing work.

## `git status --short`

```text
 M deploy/cloudflare-landing/test/intake.test.js
 M deploy/cloudflare-landing/worker.js
?? carepathchina-update/
?? docs/community/
?? docs/upgrade/cml-fde-v3.0/
?? output/onepage/
?? scripts/build_structurevidence_onepage.py
?? scripts/build_structurevidence_onepage_dark.py
?? scripts/test_cml_fde_v3.py
?? stoneyrola-update/
?? technical-risk/cml-fde-v3.0/
```

`docs/community/` contains the controlled SE-FRR audit reports. All other entries above predated SE-FRR execution.

## `git diff -- deploy/cloudflare-landing/worker.js`

```diff
diff --git a/deploy/cloudflare-landing/worker.js b/deploy/cloudflare-landing/worker.js
index 6b2eebf..ebbde83 100644
--- a/deploy/cloudflare-landing/worker.js
+++ b/deploy/cloudflare-landing/worker.js
@@ -159,6 +159,7 @@ export function createWorker({ authVerifier = verifyAccess } = {}) {
     const url = new URL(request.url);
     try {
       if (url.hostname === "www.structevidence.com") return Response.redirect(`https://structevidence.com${url.pathname}${url.search}`, 308);
+      if (url.pathname === "/admin" || url.pathname === "/admin/") return Response.redirect("https://structevidence.com/admin/requests/", 302);
       if (url.pathname === "/api/requests" && request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request, env) });
       if (url.pathname === "/api/requests" && request.method === "POST") return await submitRequest(request, env);
       if (url.pathname.startsWith("/api/admin/") || url.pathname.startsWith("/admin/requests")) return await adminRoute(request, url, env, authVerifier);
```

## `git diff -- deploy/cloudflare-landing/test/intake.test.js`

```diff
diff --git a/deploy/cloudflare-landing/test/intake.test.js b/deploy/cloudflare-landing/test/intake.test.js
index a468e2a..1dcab57 100644
--- a/deploy/cloudflare-landing/test/intake.test.js
+++ b/deploy/cloudflare-landing/test/intake.test.js
@@ -93,11 +93,21 @@ test("admin list/detail and material changes append events", async () => {
 test("admin routes select independent Access audiences", async () => {
   const audiences = [], db = new FakeD1();
   const worker = createWorker({ authVerifier: async (_request, _env, audience) => { audiences.push(audience); return { email: "admin@example.com" }; } });
+  for (const path of ["/admin", "/admin/"]) {
+    const root = await worker.fetch(new Request(`https://structevidence.com${path}`), baseEnv(db));
+    assert.equal(root.status, 302);
+    assert.equal(root.headers.get("location"), "https://structevidence.com/admin/requests/");
+  }
   await worker.fetch(new Request("https://structevidence.com/admin/requests/"), baseEnv(db));
   await worker.fetch(new Request("https://structevidence.com/api/admin/requests"), baseEnv(db));
   assert.deepEqual(audiences, ["ui-aud", "api-aud"]);
 });
 
+test("admin root redirect target remains authenticated", async () => {
+  const response = await createWorker().fetch(new Request("https://structevidence.com/admin/requests/"), baseEnv(new FakeD1()));
+  assert.equal(response.status, 403);
+});
+
 test("migration enforces append-only events and no file table", () => {
   const sql = readFileSync(new URL("../migrations/0001_customer_intake.sql", import.meta.url), "utf8");
   assert.match(sql, /request_events_no_update/); assert.match(sql, /request_events_no_delete/); assert.doesNotMatch(sql, /CREATE TABLE request_files/i);
```

## Untracked path classification

### External-project contamination candidates

- `carepathchina-update/`
- `stoneyrola-update/`

Disposition: exclude from the SE-FRR branch and worktree.

### Potential StructEvidence development artifacts

- `docs/upgrade/cml-fde-v3.0/`
- `scripts/test_cml_fde_v3.py`
- `technical-risk/cml-fde-v3.0/`

Disposition: exclude from SE-FRR pending separate provenance review.

### Generated/build-output candidate

- `output/onepage/`

Disposition: exclude from SE-FRR; determine reproducibility and ignore policy separately.

### Build scripts requiring separate review

- `scripts/build_structurevidence_onepage.py`
- `scripts/build_structurevidence_onepage_dark.py`

Disposition: exclude from SE-FRR pending separate review.
