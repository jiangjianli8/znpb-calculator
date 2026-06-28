#!/usr/bin/env python3
"""Fetch SHFE zinc and lead futures prices from Sina Finance."""
import json, urllib.request, os, re, sys
from datetime import datetime

SYMBOLS = {"ZN": "nf_ZN0", "PB": "nf_PB0"}
LABELS = {"ZN": "沪锌连续 (SHFE)", "PB": "沪铅连续 (SHFE)"}
DEFAULTS = {"ZN": 24420, "PB": 16260}

result = {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

for key, sym in SYMBOLS.items():
    try:
        url = f"https://hq.sinajs.cn/list={sym}"
        req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("gbk", errors="ignore")
        m = re.search(r'"([^"]*)"', raw)
        if m:
            parts = m.group(1).split(",")
            price = float(parts[3])
            if price > 0:
                result[key.lower()] = {"price": price, "source": LABELS[key], "unit": "元/吨"}
                print(f"{key}: {price:.0f} 元/吨")
                continue
    except Exception as e:
        print(f"{key} fetch error: {e}")
    # Fallback to default
    result[key.lower()] = {"price": DEFAULTS[key], "source": "默认参考价", "unit": "元/吨"}

out_path = os.path.join(os.path.dirname(__file__), "..", "data", "price.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"Saved to {out_path}")
