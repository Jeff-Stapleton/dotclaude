---
name: grocery-shopping
description: Do Jeff's grocery shopping in Chrome across Walmart and Sam's Club. Compare price per lb/oz/count, fill both carts but never check out, then log what was ordered to the Grocery Tracker workbook (~/Documents/Groceries/Grocery Tracker.xlsx), which tracks price history and pantry inventory. Use this whenever Jeff pastes a shopping list or says things like "do my grocery shopping", "fill my Walmart / Sam's cart", "which store is cheaper for…", "restock", "what do we need", "log / update the grocery spreadsheet", "record what I ordered" or "update with the receipt", or asks how grocery prices have changed, even if neither store nor the spreadsheet is named.
---

# Grocery shopping

Jeff wants the best **price per unit** (per lb, oz or count) first and the total price second,
within a budget Jeff sets. The job has two halves: **shop** (price both stores, fill the carts,
report) and **log** (record what was actually ordered in the tracker so future trips get easier
and prices can be compared over time).

## Ground rules, and why

- **Fill the carts, then stop.** Jeff checks out: Jeff picks delivery or pickup, the time
  slot, fees and payment. Don't open checkout, choose slots or place orders. Adding and removing
  cart items is fine because it can be undone.
- **Leave items that were already in a cart alone.** On 10/17/2026 the Sam's cart already had a
  $198 Fitbit. List anything like that in the report and let Jeff decide what to do with it.
- **Use your own tabs** (`tabs_create_mcp`). Chrome shares the signed-in session, so you don't
  need Jeff's tabs. Close extra tabs when done, but leave the two cart tabs open if Jeff might
  check out from them.
- **Never enter payment or sign-in details.** If a site asks Jeff to sign in, stop and say so.

## Files

| What | Where |
|---|---|
| Tracker workbook | `~/Documents/Groceries/Grocery Tracker.xlsx` |
| Tracker script | `~/.claude/skills/grocery-shopping/scripts/tracker.py` (usage in its docstring) |
| Python with openpyxl | `~/.claude/skills/grocery-shopping/.venv/bin/python` |
| Browser recipes (search, add to cart, read carts) | `references/site-recipes.md`. Read it before touching the browser. |

If the `.venv` is missing: `python3 -m venv ~/.claude/skills/grocery-shopping/.venv && ~/.claude/skills/grocery-shopping/.venv/bin/pip install openpyxl`.
If the workbook is missing, `tracker.py init <path>` creates a blank one with the same layout.

Below, `PY` is the venv python, `T` is tracker.py and `XL` is the workbook path.

## Part 1: Shop

### 1. Start from what the tracker knows

Run `$PY $T catalog "$XL"`. For each item it gives the unit to compare in, preferred store, the
product and item number last bought, the latest price at each store, the best price per unit
seen, and whether it needs reordering. Use it to:
- go straight to known products by item number instead of searching from scratch (still
  re-check the price, because prices move);
- compare every item in its catalog unit, so this trip lines up with earlier ones;
- answer "what do we need?" from the reorder flags and the Usual Amount column, if Jeff asks
  for a list instead of giving one. Confirm that list with Jeff before shopping.

### 2. Look at both carts before adding anything

Note any items already there (to report, not to touch), which fulfillment mode is selected, and
any banners (Sam's membership expiry, order-minimum warnings).

### 3. Price every item at both stores

Use the in-page search recipe (recipes §1–2) to run the whole list against both stores at once.
For each item, pick like-for-like candidates and work out price per catalog unit.

How to choose:
- **Lowest price per unit wins, comparing like with like.** Compare name brand with name brand,
  and store brand with store brand. Swapping to a store brand is fine when it's plainly the same
  thing (canned corn, broth, water); for things with a taste preference (cereal, protein shakes),
  stick with the brand.
- **A bigger pack is fine** when it's no more than about twice the list amount, when it costs
  about the same as the smaller pack (carrots: 5 lb for $2.86 against 2 lb for $2.26), or when it
  keeps (meat for the freezer, frozen food, pantry goods). **Avoid big packs of produce that
  spoils fast** (16 oz of spinach for a 5 oz need).
- **Prefer what the household already buys.** Signals: Walmart's "Bought N times" badges and
  "Don't forget your usuals" row, Sam's "Saved for later" list, and `last_bought` in the
  catalog. On 10/17 these pointed to Grandma Sycamore's bread, Great Value sugar-free syrup,
  Capri Sun 40-pack and Frito-Lay Classic Mix.
- **If one store doesn't carry it, buy it at the other.** Sam's had no distilled water, no
  sugar-free syrup and no frozen peas & carrots.
- **Make sure it can come by the chosen method.** At Sam's, a shipping-only item adds a shipping
  fee unless the shipped items reach $50. Pick a deliverable alternative or point out the fee.
- **Items sold by weight** (fresh meat, bananas) show an estimated price; say so.
- Keep the grocery subtotal (excluding items already in the cart) under the budget.

### 4. Fill the carts

Use recipe §4 in `browser_batch` calls of 5–6 items (navigate → add → quantity). Each step's
output should say `clicked: <product>` and `/pac`, and the quantity step should end at the target
quantity. If a step fails, retry that item once, then report it rather than looping.

### 5. Check the carts and report

Read both carts (recipe §5) and check item counts and subtotals against your plan. Then report:
- which store wins overall and how many items each won;
- a table per store: item, product picked, price per unit at this store against the other;
- the grocery subtotal per store and in total, against the budget;
- where you departed from the list and why (bigger packs, substitutions, items skipped);
- flags: items already in the carts, shipping-only items and their fees, by-weight estimates,
  anything out of stock.

End by saying the carts are ready for Jeff to check out. Don't offer to do the checkout.

## Part 2: Log

### 6. Log the order once Jeff has checked out, or when asked to update the spreadsheet

**Read the carts or orders again first.** Jeff often changes things after you finish: on 10/17
the cereals were swapped and the peanut butter and jelly removed. Log what was actually ordered,
not your plan.

Write a JSON file in the scratchpad (schema in tracker.py's docstring) with:
- `purchases`: one per product, with `pack_size` in the catalog unit, `qty`, `price` (for one
  pack), `regular_price` if the site showed a was-price, the item number as `sku`, `by_weight`
  set to `"Y"` plus a note on the estimate, and a note for anything notable ("ships
  separately").
- `price_checks`: the runner-up from the other store for each item, plus anything Jeff swapped
  out. This is what makes the next comparison quick.
- `orders`: one per store per date with `fulfillment`, `status` ("Ordered") and any fees, tip,
  tax and order number known so far.
- `catalog`: new items only (item, category, unit, usual amount, preferred store).

Then run `$PY $T upsert "$XL" data.json` and `$PY $T summary "$XL" <date>`. Use the order date.
Rows are matched on date + store + item number, so running it again with corrected data
updates rows instead of duplicating them. Pass on any unit-mismatch warnings it prints.

Example purchase:
```json
{"date": "2026-10-17", "store": "Walmart", "fulfillment": "Delivery", "item": "Chicken breasts",
 "product": "Freshness Guaranteed Boneless Skinless Chicken Breasts, 2.75-7.0 lb Tray",
 "brand": "Freshness Guaranteed", "sku": "27935840", "pack_size": 5, "pack_unit": "lb",
 "qty": 2, "price": 11.15, "regular_price": 12.85, "by_weight": "Y",
 "notes": "Estimated 5 lb avg tray at $2.23/lb; final cost by weight"}
```

### 7. Reconcile with the receipt after delivery

When Jeff asks to update the spreadsheet with the real totals, open each store's orders page
(recipes table) and capture the order number, final weights and prices for by-weight items,
substitutions, out-of-stock items, fees, tip and tax. Upsert again with the same dates, stores
and item numbers so the existing rows update:
- **Substitution:** update that row's product, price and pack size, and say what was replaced in
  `notes`. If the item number changed, set `qty` to 0 on the old row and add the substitute as a
  new row.
- **Out of stock:** set `qty` to 0 and note it.
- **Order details:** `orders` with `order_number`, `fees`, `tip`, `tax`, `status: "Delivered"`.

## Workbook layout (for reference)

Purchase Log (one row per product) · Orders (one row per order: fees, tip, tax, status) ·
Summary (per store and category for a trip date, against the budget) · Item Catalog (one row per
recurring item, with On Hand and Reorder At for inventory) · Price Checks (prices seen but not
bought) · Read Me. Blue cells are values Jeff types, black cells are formulas, and yellow cells
are filled from the receipt. The script only writes input cells, so the formulas keep working.
