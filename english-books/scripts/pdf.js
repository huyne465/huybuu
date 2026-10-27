// Print an HTML file to PDF with Chromium.
// Usage: node pdf.js <in.html> <out.pdf> [footerLabel]   (no footerLabel = no footer, full bleed)
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [input, output, footer] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle', timeout: 600000 });
  await page.evaluate(() => document.fonts.ready);
  const opts = { path: output, format: 'A4', printBackground: true, preferCSSPageSize: true, timeout: 600000 };
  if (footer) {
    Object.assign(opts, {
      displayHeaderFooter: true,
      headerTemplate: '<span></span>',
      footerTemplate: `<div style="width:100%;font-family:sans-serif;font-size:8px;color:#8a8aa0;
        padding:0 14mm;display:flex;justify-content:space-between;">
        <span>${footer}</span><span class="pageNumber"></span></div>`,
    });
  }
  await page.pdf(opts);
  await browser.close();
})();
