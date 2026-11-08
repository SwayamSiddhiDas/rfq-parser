"""Lists every message the parser gets wrong. Usage: python show_fails.py my_tests.jsonl"""
import json, sys
from parse import parse_rfq
from score import same, FIELDS

path = sys.argv[1] if len(sys.argv) > 1 else "my_tests.jsonl"
rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
bad = 0
for r in rows:
    out = parse_rfq(r["text"])
    wrong = [f for f in FIELDS if not same(f, out.get(f), r["expected"][f])]
    if wrong:
        bad += 1
        print("TEXT:", r["text"])
        for f in wrong:
            print(f"   {f}: got {out.get(f)!r}  expected {r['expected'][f]!r}")
        print()
print(f"{bad} wrong out of {len(rows)}")
