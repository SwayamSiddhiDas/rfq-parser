# RFQ Parser: Note

## Approach
`parse_rfq()` is rule-based, with no model and no API. Each field has its own small function. Before reading the quantity, the code strips out numbers that are not an order quantity: gsm, microns, dimensions (12x10x8), ply counts, fill weights ("25 kg bag"), capacities ("1000 kg capacity", "rating"), and phone numbers. Indian number words and formats (lakh, lac, hazaar, k, 1,50,000, ek lakh) are converted to numbers. Quantity is chosen by a simple score (has a unit, has a scale word, is large). On a tie, a count unit (pcs, bags) beats a weight unit for bags, boxes and pouches. Category uses ordered keyword lists. Location looks up cities and countries in `geonamescache` (offline). If nothing matches, it takes the capitalised word after "to / in / at / delivery / dispatch" and skips words that are not places (such as WhatsApp or Sir).

## Score
| File | Result |
|---|---|
| `my_tests.jsonl` (45) | 45/45 all fields (I tuned on this file) |
| Held-out set (35) | 35/35 (not fully blind: I fixed two failures from it) |
| Fresh set, 24 new messages, first run before any fix | **22/24 (91.7%)**, the honest unseen number |
| Fresh set after fixes | 24/24 (tuned on it, so not unseen any more) |

Runtime is about 0.02 s for 45 messages.

## Three messages it got wrong, and why
1. "...rate chahiye 9820123456 par call karo": returned the phone number as quantity. A 10-digit number scored highest because nothing else was a candidate. Fixed by removing phone numbers before quantity parsing.
2. "...20k bags 85 gsm send via WhatsApp 9437012345": returned "WhatsApp" as the location. The capitalised-word fallback accepted any capitalised word. Fixed with a list of non-place words.
3. "woven bori plain white 50 kg grain packing 35000 pcs ...": returned 50 kg as the quantity. The fill weight and the real quantity scored the same, and the first one won. Fixed with a count-unit tie-break.

## What I would do with 1,000 real labelled examples
- Keep them as a held-out set and never tune on it. Report errors per field, not just one overall number.
- Group the errors by cause (fill weights, number formats, unseen towns) and fix the groups that matter most.
- Check whether a small local classifier does better than keyword lists on category, and keep rules for numbers, where they are exact.
- Build a list of the real towns and spellings buyers use.

## How I would know it works in production
- Log every parse and have people check a weekly random sample.
- Track how often buyers or suppliers correct a field, and how often a field comes back empty.
- Watch downstream: buyer-to-supplier matches that need manual fixes.

## Tools used
- Gemini (Argon model) wrote the first draft of `parse.py` and the first test messages. ChatGPT and Claude (chat) were used for planning, labelling the test files and reviewing fixes. [EDIT: keep only the tools you actually used.]
- I ran every score myself, read the code, checked the labels, and made the fixes above. [EDIT: change this to what is true.]
