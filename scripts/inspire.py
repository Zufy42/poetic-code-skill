#!/usr/bin/env python3
"""灵感触发器 —— 今日诗词 API（https://www.jinrishici.com）

用法（淬纹前抽一句定调）：
    python scripts/inspire.py            # 随机一句 + 全诗
    python scripts/inspire.py --one      # 只要一句，不附全诗

免 key；网络不通时降级为内置离线句（按七场景卡各留一联）。
"""
import json
import sys
import urllib.request

API = "https://v2.jinrishici.com/one.json"

OFFLINE = [
    ("朔气传金柝，寒光照铁衣。", "《木兰诗》· 边塞"),
    ("小楼一夜听春雨，深巷明朝卖花声。", "陆游《临安春雨初霁》· 市井"),
    ("采菊东篱下，悠然见南山。", "陶渊明《饮酒》· 田园"),
    ("空山不见人，但闻人语响。", "王维《鹿柴》· 山水"),
    ("浪淘尽，千古风流人物。", "苏轼《念奴娇》· 怀古"),
    ("劝君更尽一杯酒，西出阳关无故人。", "王维《送元二使安西》· 赠别"),
    ("九天阊阖开宫殿，万国衣冠拜冕旒。", "王维《和贾至舍人早朝大明宫》· 应制"),
]


def main():
    one_only = "--one" in sys.argv
    try:
        req = urllib.request.Request(API, headers={"User-Agent": "Mozilla/5.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        d = data["data"]
        verse = d["content"]
        src = d["origin"]
        author = f"{src.get('dynasty', '')}·{src.get('author', '')}".strip("·")
        print(f"句：{verse}")
        print(f"出：{author}《{src.get('title', '')}》")
        if not one_only:
            body = "".join(src.get("content", []))
            print(f"全：{body}")
    except Exception:
        import random
        verse, src = random.choice(OFFLINE)
        print(f"句：{verse}")
        print(f"出：{src}（离线句库）")


if __name__ == "__main__":
    main()
