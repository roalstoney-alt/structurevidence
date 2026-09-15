const { chromium } = require('/Users/roal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  });
  const cases = [
    { name: 'desktop', width: 1440, height: 1000 },
    { name: 'mobile', width: 390, height: 844 },
  ];
  for (const item of cases) {
    const page = await browser.newPage({ viewport: { width: item.width, height: item.height } });
    const errors = [];
    page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
    await page.goto('http://127.0.0.1:8765/technical-risk/', { waitUntil: 'networkidle' });
    if (!(await page.locator('h1').innerText()).includes('Technical change')) throw new Error(`${item.name}: landing heading`);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (overflow > 1) throw new Error(`${item.name}: horizontal overflow ${overflow}`);
    await page.screenshot({ path: `/tmp/cml-${item.name}.png`, fullPage: true });
    if (errors.length) throw new Error(`${item.name}: console ${errors.join('; ')}`);
    await page.close();
  }

  for (const item of cases) {
    const page = await browser.newPage({ viewport: { width: item.width, height: item.height } });
    await page.goto('http://127.0.0.1:8765/', { waitUntil: 'networkidle' });
    if (!(await page.locator('body').innerText()).includes('Evidence domains')) throw new Error(`${item.name}: org domain section`);
    if (!(await page.locator('a[href="technical-risk/"]').count())) throw new Error(`${item.name}: org Technical Risk link`);
    if ((await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)) > 1) throw new Error(`${item.name}: org overflow`);
    await page.screenshot({ path: `/tmp/cml-org-${item.name}.png`, fullPage: true });
    await page.goto('http://127.0.0.1:8765/landing.html', { waitUntil: 'networkidle' });
    if (!(await page.locator('header a[href="/technical-risk/"]').count())) throw new Error(`${item.name}: com Technical Risk navigation`);
    if (!(await page.locator('header a[href="/technical-risk/request-analysis/"]').count())) throw new Error(`${item.name}: com request navigation`);
    if ((await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)) > 1) throw new Error(`${item.name}: com overflow`);
    await page.screenshot({ path: `/tmp/cml-com-${item.name}.png`, fullPage: true });
    await page.close();
  }

  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto('http://127.0.0.1:8765/technical-risk/search/', { waitUntil: 'networkidle' });
  await page.fill('#cml-query', 'MRF101AN');
  await page.locator('[data-cml-search] button').click();
  await page.waitForSelector('.search-result');
  if (!(await page.locator('[data-cml-results]').innerText()).includes('RADIO-POWER-2026-FAMILY')) throw new Error('search match');
  await page.fill('#cml-query', 'NOT-A-REAL-PART');
  await page.locator('[data-cml-search] button').click();
  if (!(await page.locator('[data-cml-results]').innerText()).includes('No structured assessment')) throw new Error('search empty state');
  if (!(await page.locator('[data-cml-results] a').getAttribute('href')).includes('request-analysis')) throw new Error('search request CTA');
  await page.goto('http://127.0.0.1:8765/technical-risk/record/amphenol-rf-095-725-134-006/', { waitUntil: 'networkidle' });
  if ((await page.locator('link[rel="canonical"]').getAttribute('href')) !== 'https://structurevidence.org/technical-risk/record/amphenol-rf-095-725-134-006/') throw new Error('record canonical');
  if (!(await page.locator('body').innerText()).includes('PAPER != QUALIFIED')) throw new Error('qualification boundary');
  const recordOverflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  if (recordOverflow > 1) throw new Error(`record overflow ${recordOverflow}`);
  await page.screenshot({ path: '/tmp/cml-record-desktop.png', fullPage: true });
  await browser.close();
  console.log('CML_UI_QA_PASS');
})().catch((error) => { console.error(error); process.exit(1); });
