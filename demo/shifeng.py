"""试锋：铸坯与淬纹两版跑同一组行为测试，语义应完全一致"""
import sys, time
sys.path.insert(0, r"D:\大三上\poetic-code-demo")

import zhubu
import gexing

cases = []

def 验(名, 得, 望):
    ok = 得 == 望
    cases.append(ok)
    print(f"{'✓' if ok else '✗'} {名}: {得!r}")

# ── 铸坯版 ──────────────────────
print("── 铸坯 zhubu ──")
lim = zhubu.RateLimiter(rate=50, capacity=3)
lim.acquire(); lim.acquire(); lim.acquire()          # 耗尽令牌
t0 = time.monotonic(); lim.acquire(); dt0 = time.monotonic() - t0
验("限流补充耗时>0.015s", round(dt0, 2) >= 0.015, True)

tries = []
def flaky():
    tries.append(1)
    if len(tries) < 3: raise zhubu.TransientError()
    return "ok"
验("重试三次成功", zhubu.request_with_retry(flaky, retries=5, base_delay=0), "ok")
验("重试次数", len(tries), 3)

def always_fail(): raise zhubu.TransientError()
client = zhubu.Client(zhubu.RateLimiter(rate=1000), retries=2)
try:
    client.get("a", always_fail)
    验("无降级时上抛", "未抛", "抛了")
except zhubu.TransientError:
    验("无降级时上抛", "抛了", "抛了")
client.cache["b"] = "cached"
验("缓存降级", client.get("b", always_fail), "cached")
验("函数降级", client.get("c", always_fail, fallback=lambda: "fb"), "fb")

# ── 淬纹版（同一测试） ──────────
print("── 淬纹 gewhang ──")
tries2 = []
def flaky2():
    tries2.append(1)
    if len(tries2) < 3: raise gexing.风浪()
    return "ok"
验("重试三次成功", gexing.垂纶(flaky2, 至多=5, 静候=0), "ok")
验("重试次数", len(tries2), 3)

柝 = gexing.金柝(更速=50, 备更=3)
柝.候更(); 柝.候更(); 柝.候更()
t1 = time.monotonic(); 柝.候更(); dt1 = time.monotonic() - t1
验("限流补充耗时>0.015s", round(dt1, 2) >= 0.015, True)

def 常败(): raise gexing.风浪()
囊 = gexing.锦囊(gexing.金柝(更速=1000), 至多=2)
try:
    囊.遣使(常败, 名="a")
    验("无降级时上抛", "未抛", "抛了")
except gexing.风浪:
    验("无降级时上抛", "抛了", "抛了")
囊.旧书["b"] = "cached"
验("旧书降级", 囊.遣使(常败, 名="b"), "cached")
验("岔路降级", 囊.遣使(常败, 名="c", 岔路=lambda: "fb"), "fb")

print(f"\n{'全部通过' if all(cases) else '有失败!'}：{sum(cases)}/{len(cases)}")
sys.exit(0 if all(cases) else 1)
