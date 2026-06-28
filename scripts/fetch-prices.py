#!/usr/bin/env python3
"""Fetch SMM 1#铅锭 and 1#锌锭 spot prices via SMM AJAX API (no auth needed).
   Saves to data/price.json for GitHub Pages.
"""
import json, urllib.request, os
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)

end_date = now.strftime("%Y-%m-%d")
start_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")

# SMM product IDs
PRODUCTS = {
    "pb": {"id": "201102250211", "name": "SMM 1#铅锭", "default": 16050},
    "zn": {"id": "201102250418", "name": "SMM 1#锌锭", "default": 23660},
}

result = {"updated_at": now.strftime("%Y-%m-%d %H:%M:%S"), "source": "smm_ajax"}

for key, cfg in PRODUCTS.items():
    pid = cfg["id"]
    api_url = f"https://hq.smm.cn/ajax/spot/history/{pid}/{start_date}/{end_date}"
    try:
        req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": f"https://hq.smm.cn/lead/category/{pid}",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            smm = json.loads(resp.read().decode())
            if smm.get("code") == 0 and smm.get("data"):
                latest = smm["data"][-1]
                avg = latest.get("average", 0)
                if avg > 0:
                    result[key] = {
                        "price": int(avg),
                        "source": cfg["name"],
                        "unit": "元/吨",
                        "renew_date": latest.get("renew_date", ""),
                    }
                    print(f"{key.upper()}: {int(avg)} 元/吨 (updated: {latest.get('renew_date')})")
                    continue
    except Exception as e:
        print(f"{key.upper()} fetch error: {e}")

    # Fallback
    if key not in result:
        result[key] = {"price": cfg["default"], "source": "默认参考价", "unit": "元/吨"}
        print(f"{key.upper()}: fallback {cfg['default']} 元/吨")

out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "price.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"OK -> {out_path}")
