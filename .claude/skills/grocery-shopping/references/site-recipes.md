# Walmart and Sam's Club browser recipes

Both sites run on the same Walmart platform, so the same tricks work on each:

| | Walmart | Sam's Club |
|---|---|---|
| Search page | `https://www.walmart.com/search?q=<query>` | `https://www.samsclub.com/s/<query>` |
| Product page | `https://www.walmart.com/ip/<id>` | `https://www.samsclub.com/ip/x/<id>` (any slug works) |
| Cart | `https://www.walmart.com/cart` | `https://www.samsclub.com/cart` |
| Orders (unverified, confirm on first use) | `https://www.walmart.com/orders` | `https://www.samsclub.com/orders` |

`<id>` is the `usItemId`, which is what the tracker stores as **Store Item #**.

Everything below runs through `javascript_tool` on a tab already on that site, so `fetch` is
same-origin and reuses Jeff's signed-in session.

## Contents
1. Search many items quickly
2. Run long searches without timing out
3. Product details (net weight)
4. Add to cart and set quantity
5. Read the carts
6. Quirks seen so far

## 1. Search many items quickly

Search pages embed their results as JSON in `<script id="__NEXT_DATA__">`. Fetching and parsing
that is far faster than loading pages and reading them. Define this once per page load:

```js
window.__s = async (q, n = 8) => {
  const url = location.hostname.includes('samsclub') ? '/s/' + encodeURIComponent(q)
                                                     : '/search?q=' + encodeURIComponent(q);
  const h = await (await fetch(url, {credentials: 'include'})).text();
  const m = h.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  if (!m) return {q, err: 'no data'};
  const d = JSON.parse(m[1]);
  const items = (d.props.pageProps.initialData?.searchResult?.itemStacks || [])
    .flatMap(s => s.items || [])
    .filter(i => i.__typename === 'Product' && !i.isSponsoredFlag);
  // Walmart puts prices in priceDetails.priceLines; Sam's fills linePrice/unitPrice directly.
  const pl = (i, t) => (i.priceInfo?.priceDetails?.priceLines || [])
    .filter(l => l.lineType === t).flatMap(l => l.values.map(v => v.value)).join(' ');
  return items.slice(0, n).map(i => [
    i.name.slice(0, 85),
    i.priceInfo?.linePrice || pl(i, 'CURRENT_PRICE') || i.price,
    i.priceInfo?.unitPrice || pl(i, 'UNIT_PRICE'),
    i.usItemId,
    i.availabilityStatusV2?.value === 'IN_STOCK' ? '' : (i.availabilityStatusV2?.value || '?'),
  ].join(' | '));
};
```

Output per row: `name | price | unit price | id | stock flag`. Walmart prices come back without
`$` and Sam's with it. "Priced per pound" items (fresh meat) show the average package price,
and the unit price is per lb.

## 2. Run long searches without timing out

A `javascript_tool` call times out after about 45 s, and each search takes 2–3 s. For more than
about 12 queries, start a background loop and poll it:

```js
window.__res = {}; window.__done = false;
(async () => {
  for (const q of ['ground beef', 'boneless skinless chicken breast' /* , ... */]) {
    try { window.__res[q] = await window.__s(q, 7); } catch (e) { window.__res[q] = String(e); }
    await new Promise(r => setTimeout(r, 300));
  }
  window.__done = true;
})();
'started'
```

Poll with `({done: window.__done, n: Object.keys(window.__res).length, res: window.__done ? window.__res : null})`
and use `computer` `wait` (max 10 s each) between polls.

**Don't navigate a tab while its loop is running.** Navigating kills the loop. If you need to look
at something else meanwhile (a cart, say), open another tab.

Run the Walmart loop in a Walmart tab and the Sam's loop in a Sam's tab at the same time.

## 3. Product details (net weight)

When a listing doesn't give a size (e.g. a 3-pack of pizzas), fetch the product page:

```js
const h = await (await fetch('/ip/x/13629810294')).text();   // Sam's; Walmart uses /ip/<id>
const d = JSON.parse(h.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/)[1]);
const idml = d.props.pageProps.initialData?.data?.idml;
JSON.stringify(idml?.specifications || '').match(/Net weight[^<]*/i)
```

## 4. Add to cart and set quantity

Navigate to the product page, then click the buy-box button with JS. Matching the button's
aria-label to the page's `<h1>` avoids the many "Add" buttons in carousels lower on the page.
Walmart's label is `Add to cart`; Sam's is `Add to Cart`. This handles both:

```js
const sleep = ms => new Promise(r => setTimeout(r, ms)); let out = 'not found';
for (let i = 0; i < 20; i++) {
  const h1 = document.querySelector('h1')?.textContent.trim() || '';
  const b = [...document.querySelectorAll('button')].find(b =>
    /^Add to cart$/i.test(b.textContent.trim()) && h1 && (b.getAttribute('aria-label') || '').includes(h1.slice(0, 25)));
  if (b) { b.click(); out = 'clicked: ' + h1; break; }
  await sleep(300);
}
for (let i = 0; i < 20 && location.pathname !== '/pac'; i++) await sleep(300);
out + ' -> ' + location.pathname
```

Success redirects to `/pac` ("Added to cart"). To raise the quantity there (verified on Walmart;
Sam's `/pac` shows the same −/+ stepper but the label wasn't confirmed, so check with `find` the
first time):

```js
const target = 4; const sleep = ms => new Promise(r => setTimeout(r, ms)); let res = 'timeout';
for (let i = 0; i < 40; i++) {
  const inc = [...document.querySelectorAll('button')]
    .find(b => /^Increase quantity/.test(b.getAttribute('aria-label') || ''));
  if (!inc || location.pathname !== '/pac') { await sleep(300); continue; }
  const cur = +((inc.getAttribute('aria-label').match(/Current Quantity (\d+)/) || [])[1]);
  if (cur >= target) { res = inc.getAttribute('aria-label'); break; }
  inc.click(); await sleep(1200);
}
res
```

Batch 5–6 items per `browser_batch` call: `navigate` → add script → quantity script, repeated.
The quantity script's output names the item and its final quantity, which doubles as a check.

## 5. Read the carts

- **Walmart:** `get_page_text` on `/cart`. Cart lines come before "Add your essentials". Each
  shows `$line total, $each ea` with the quantity on its own line after "RemoveSave for later".
  The summary at the bottom reads `Items (N) … Savings -$X … Subtotal $Y`. (Returning the cart's
  `innerText` from `javascript_tool` got blocked by the output filter, so use `get_page_text`.)
- **Sam's:** items are grouped by fulfillment (Delivery / Pickup / Shipping) and the main group
  is collapsed. Click the "See details for N items" button (`find` it), then `get_page_text`.
  Everything after "Items you may like" is recommendations or "Saved for later", not the cart.
  Read the subtotal and shipping lines at the bottom.

## 6. Quirks seen so far

- A price-tracker browser extension sometimes overlays a "tips" panel on Walmart's buy box and
  swallows coordinate clicks. JS `.click()` isn't affected.
- Sam's search `unitPrice` is occasionally wrong (frozen chicken tenderloins showed 61¢/lb on a
  $21.97 6 lb bag). Sanity-check unit prices against price ÷ size.
- Sam's Plus: free shipping once shipped items reach $50. A single shipping-only item adds a fee
  (an $8.00 fee on a $8.98 cereal on 10/17/2026), so prefer an item that can be delivered.
  The membership banner on 10/17/2026 said it expires in 41 days (about 2026-11-27).
- Walmart cart: delivery windows show "Free with" (Walmart+) and express windows cost extra. The
  site warns about an order-minimum fee on small orders.
- Fresh meat and bananas are "final cost by weight"; the cart shows an average price.
