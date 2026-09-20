#!/usr/bin/env python3
"""平仄校验器 —— 律联镣铐自检

用法：
    python scripts/pingze.py "更鼓有期催过客，烽烟无警度流年"
    python scripts/pingze.py poem.txt        # 多联逐联检查
    echo "上句，下句" | python scripts/pingze.py

依赖：pip install pypinyin

规则（对齐 references/cipai.md 律联速查）：
  - 声调 1/2 = 平，3/4 = 仄
  - 入声字一律为仄（表内为普通话读平声的高频入声字，仅此类会误判）
  - 平仄两读字标"中"，不判违规，人工定夺
  - 联检：上句尾仄、下句尾平；节奏点（五言2,4；七言2,4,6）句内交替、上下相对
"""
import re
import sys

# 入声字表：平水韵入声十七部全 1653 字中，普通话读 1/2 声的 735 字（只收此类，
# 因声调法会将其误判为平）。数据源：charlesix59/chinese_word_rhyme 平水韵 JSON
# （github.com/charlesix59/chinese_word_rhyme），筛选脚本见 data 来源说明。
RUSHENG = set(
    "㱩䥽䦆一七乏习亟亳什仆仡伋伏伐伯佛佶佸侄侠俗倏倔倢倬值傕僰儿八决凸出击凿则刜别刮"
    "刷刹削剌剔剟剥剫剭割劂劈劫劼劾勃勒勰勺匐匝匣匼十协卒卓博即压厥及发叔叠叭吃合吉吸"
    "呷呾咄咈咭哭哲哳唧唰唶啄啧啯喀喋喌喔喝嗋嗑嗒嗝嘎噎噢噱嚃嚄嚼国圾垤埴堀堞堲塉塌塞"
    "塾墣壳壹夕失夹夺妯妲姞婕婠嫉嫡孑学孰宅实寔察尼局屈屋屐岊岌峃峡崒崛嶷巀帖帛席帻帼"
    "幅弗彴得德忽怗怛急怫息悉惚惜惵愶憰懪戄戚戛戢截扎扑托执扱扴批抇抉折押抾拂拆拉拍拔"
    "拙拨择拮拽拾挟挶捉捌捏捔捷捽掇掏掐掖掘接掬掴插揖揭揲搏搕搭搰摘摭摸撅撇撮撷擖擘擢"
    "擿攃攉攫敌斛斫斲族昔昨昳晰暍曰曲曷服札朳杀杂杓杰极析柙栝核格桀桷棁棘椄椊植椓椟楅"
    "楔楫楬楶榼槢槭槲樀樧樴橇橐橘橛橶檄檡欂欱欻歇歊殖殛毄毒毼汁汃汋汐汲沓没沰沷泊泏泬"
    "泶泼泽洁洑活浃浊浞浡涤涸涿淅淑淴渎渤湒湜湿滆滑滴漆潗潝澓激濈濮濯灂灼烛焯熄熟燋爝"
    "爵牍牒犆犊犦犮狄狎独狭猲猾獦玃玦玨琢璞瓝瓞疌疖疙疾瘃瘚瘠白盍盒直督睫睾瞂瞌瞎瞥矍"
    "石矻硖碡碣磍磔磕祏祓祫福秃秫积秸稙穛穴穵穸突窋窟窣竭竹竺笈笛笪笮筏答箔箙箦簙籍籴"
    "粥絜絷綍緆縠纀纥约级绂织绋结绖绝缉缩缪缬缺罚罬羍羯翕翛翟翮耋耤职聒肋肸胁胠脊脖脱"
    "腌腯膈膊膌膜膝臄臿舌舳舴舶艓艴节芍芨苶茀茁茇茯茿荚荻莌菊菔菝菥菨菽葍葖葛蒲蒺蔱蕀"
    "蕝蕨蕺薂薄薛藉虙虢虱蚀蚻蛣蛤蛰蛱蜥蝈蝍蝎蝠蝪蝶螖蟨蠈蠋衱袭袯袷袺裰裻褋褡襋襗襭襮"
    "觉觋觌觖觡觳詄詟諿謈謵讟讦诀识诎诘说读诼谍谪谲豁豰貉貜责贴贼赎赜足趹趿跋跌跖跫跲"
    "跼踔踕踖踘踢踣踤踯踱蹀蹐蹢蹩蹶躅躇躩軷輂輵轕轴辄辐辑辖辙达迪迭迮逐逴逼邋郃郏郭鄎"
    "酌醭鑮钵钹铎铗铦铩锡锸镈镝镞镤镯闸阀阁阖阘阙隔隰集雥雹霓霫霵霹革靮靼鞄鞠鞨鞫韐韣"
    "韨顼颉颊颓额飑食饦饽馘馞馰驳骰骼髆髑鬲魃魠鱍鲒鲽鳖鴶鵊鵙鵩鵫鵴鷢鸐鸭鸴鸹鸽鹁鹖鹡"
    "麧麹黑黠黩黻鼫齱龁龙𪨗𫏋𫔎𫘝𬂩"
)

# 平仄两读字（标"中"）
LIANGDU = set("看过望忘听思醒凭论叹教应乘兴行重从衣冠胜漫当称障藏更骑")


def pingze_of(char: str) -> str:
    if char in RUSHENG:
        return "仄"
    if char in LIANGDU:
        return "中"
    from pypinyin import pinyin, Style
    py = pinyin(char, style=Style.TONE3, errors="ignore")
    if not py or not py[0][0]:
        return "？"  # 非汉字
    tone = int(py[0][0][-1]) if py[0][0][-1].isdigit() else 0
    if tone in (1, 2):
        return "平"
    return "仄"


def annotate(line: str):
    chars = [c for c in line if not re.match(r"[\s，。、！？；：,.;:!?]", c)]
    marks = [pingze_of(c) for c in chars]
    return chars, marks


def check_line(line: str):
    chars, marks = annotate(line)
    n = len(chars)
    beats = [1, 3] if n == 5 else ([1, 3, 5] if n == 7 else [])
    beat_marks = [marks[i] for i in beats] if beats else []
    # 句内节奏点交替
    alt = all(
        beat_marks[i] in "中?" or beat_marks[i + 1] in "中?" or beat_marks[i] != beat_marks[i + 1]
        for i in range(len(beat_marks) - 1)
    )
    return chars, marks, beat_marks, alt


def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ("-",) and not sys.argv[1].startswith("--"):
        arg = sys.argv[1]
        import os
        if os.path.isfile(arg):
            text = open(arg, encoding="utf-8").read()
        else:
            text = arg
    else:
        text = sys.stdin.read()

    # 切联：按句号/分号分句，两句一联
    sentences = [s.strip() for s in re.split(r"[。；\n]", text) if s.strip()]
    pairs = []
    for s in sentences:
        parts = [p.strip() for p in re.split(r"[，,]", s) if p.strip()]
        for i in range(0, len(parts) - 1, 2):
            pairs.append((parts[i], parts[i + 1]))

    all_ok = True
    for up, down in pairs:
        ok = True
        for sent in (up, down):
            chars, marks, beats, alt = check_line(sent)
            mark_str = "".join(marks)
            note = f"节奏点（{''.join(beats)}）{''.join(beats)} {'✓交替' if alt else '✗失替'}" if beats else "（非五七言）"
            print(f"{sent}  {mark_str}  {note}")
            if not alt:
                ok = False
        # 联检：上仄收下平收 + 节奏点相对
        _, um, ub, _ = check_line(up)
        _, dm, db, _ = check_line(down)
        if um and dm:
            if um[-1] not in "仄中":
                print("  ✗ 上句应收仄（律联上仄收）"); ok = False
            if dm[-1] not in "平":
                print("  ✗ 下句应收平（律联下平收）"); ok = False
        if ub and db and len(ub) == len(db):
            opp = all(a in "中" or b in "中" or a != b for a, b in zip(ub, db))
            print(f"  联对节奏点相对：{'✓' if opp else '✗失对'}")
            if not opp:
                ok = False
        print(f"  —— {'✓ 合律' if ok else '✗ 出律'}\n")
        all_ok = all_ok and ok

    print("总判：", "全部合律 ✓" if all_ok else "有出律 ✗")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
