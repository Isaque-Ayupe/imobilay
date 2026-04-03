import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('BROWSER ERROR:', msg.text());
    }
  });

  page.on('pageerror', error => {
    console.log('PAGE ERROR:', error.message);
  });

  try {
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle0' });
    const content = await page.evaluate(() => document.getElementById('root')?.innerHTML);
    console.log('ROOT HTML:', content);
  } catch (err) {
    console.error('Navigation failed:', err);
  }

  await browser.close();
})();
