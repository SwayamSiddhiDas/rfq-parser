# RFQ Parser

Rule-based parser that turns messy English/Hinglish RFQ messages into six fields: category, quantity, unit, gsm, micron, location.

## Run
pip install -r requirements.txt
python score.py my_tests.jsonl

## Files
- parse.py: parse_rfq()
- my_tests.jsonl: 45 labelled test messages
- NOTE.md: approach, score, 3 wrong messages, plan with 1,000 labelled examples, and tools used
- blind_tests.jsonl, fresh_tests.jsonl, extra_tests.jsonl: extra held-out and fresh sets
- show_fails.py: helper that lists wrong messages
- score.py: provided by Kypson, unchanged

See NOTE.md for the full write-up.
