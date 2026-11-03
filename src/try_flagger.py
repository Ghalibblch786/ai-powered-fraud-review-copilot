from datetime import datetime
import flagger

customers = {"C1": {"home_location": "Lahore", "typical_spend_max": 100}}
merchants = {"M1": {"category": "groceries"}, "M2": {"category": "travel"}}

purchases = [
  {"customer_id":"C1","merchant_id":"M1","amount":50, "location":"Lahore","_timestamp":datetime(2026,1,1,10)},
  {"customer_id":"C1","merchant_id":"M1","amount":60, "location":"Lahore","_timestamp":datetime(2026,1,5,10)},
  {"customer_id":"C1","merchant_id":"M2","amount":50, "location":"Lahore","_timestamp":datetime(2026,1,10,10)},
  {"customer_id":"C1","merchant_id":"M1","amount":500,"location":"Dubai", "_timestamp":datetime(2026,1,10,12)},
  {"customer_id":"C1","merchant_id":"M1","amount":500,"location":"Lahore","_timestamp":datetime(2026,1,20,10)},
]

out, counts = flagger.flag_transactions(purchases, customers, merchants)
for p in out:
    print(p["_timestamp"], p["amount"], p["location"], "->", p["flag_reason"] or "(no flag)")
