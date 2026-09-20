"""歌行 · 出塞书（淬纹：限流、重试、降级的 HTTP 客户端）

选配：歌行体 × 精诣档，三章三韵。
一韵 边塞咏限流，二韵山水咏重试，三韵赠别咏降级。
韵随章换，人格随韵换：更卒 → 渔父 → 驿吏。
"""
import time


class 风浪(Exception):
    pass


# ── 第一章 金柝 · 边塞韵 ──────────────────────
# 更鼓有期催过客，烽烟无警度流年
class 金柝:
    def __init__(self, 更速: float, 备更: int = 10):
        self.更速 = 更速
        self.备更 = 备更
        self.余更 = 备更
        self.上更 = time.monotonic()

    def 候更(self):
        while True:
            今 = time.monotonic()
            self.余更 = min(self.备更, self.余更 + (今 - self.上更) * self.更速)
            self.上更 = 今
            if self.余更 >= 1:
                self.余更 -= 1
                return
            time.sleep((1 - self.余更) / self.更速)


# ── 过变 · 渡口 ─────────────────────────────
# 书出关，下马登舟


# ── 第二章 垂纶 · 山水韵 ──────────────────────
# 空网不辞重下钓，斜风偏与慢收纶
def 垂纶(撒竿, 至多=5, 静候=1):
    for 静水 in range(至多):
        try:
            return 撒竿()
        except 风浪:
            if 静水 == 至多 - 1:
                raise
            time.sleep(静候 * 2 ** 静水)   # ← 诗眼


# ── 过变 · 折柳 ─────────────────────────────
# 山穷水尽，正堪话别


# ── 第三章 锦囊 · 赠别韵 ──────────────────────
# 此路关山行不得，锦囊分我一枝春
class 锦囊:
    def __init__(self, 柝: 金柝, 至多=5):
        self.柝 = 柝
        self.至多 = 至多
        self.旧书 = {}

    def 遣使(self, 正道, 名=None, 岔路=None):
        self.柝.候更()
        try:
            书 = 垂纶(正道, self.至多)
            if 名 is not None:
                self.旧书[名] = 书
            return 书
        except 风浪:
            if 岔路 is not None:
                return 岔路()
            if 名 in self.旧书:
                return self.旧书[名]
            raise
