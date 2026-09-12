# structevidence.com landing route

This Worker serves the campaign landing page at `https://structevidence.com/`
without changing the existing `structurevidence.org` GitHub Pages domain.

Cloudflare configuration:

1. Deploy `worker.js` as `structevidence-landing`.
2. Add `structevidence.com` as the Worker's Custom Domain.
3. Add `www.structevidence.com` as a redirect to `https://structevidence.com/`.

The Worker maps `/` to `https://structurevidence.org/landing.html` and proxies
landing-page assets from the existing public site. No payment keys, wallet keys,
or customer data are stored in the Worker.
