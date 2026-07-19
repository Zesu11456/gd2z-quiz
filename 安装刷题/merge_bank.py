# -*- coding: utf-8 -*-
import json, os, re, glob, random

BASE = "F:/AI文件/WorkBuddy/2026-07-05-17-38-52/刷题/题库"
random.seed(20260706)

def norm(s):
    s = (s or "").lower()
    s = re.sub(r"[\s\u3000]+", "", s)
    s = re.sub(r"[，。、；：？！,.?!~～\-\—_()（）\[\]【】\"'“”’]", "", s)
    return s

def valid(q):
    if not isinstance(q, dict): return False
    for k in ("id","date","chapter","type","stem","options","answer","analysis","tags","source"):
        if k not in q: return False
    if q["type"] not in ("single","multiple"): return False
    if not isinstance(q["options"], dict) or not q["options"]: return False
    ans = q["answer"]
    if not isinstance(ans, list) or not ans: return False
    if q["type"]=="single" and len(ans)!=1: return False
    if q["type"]=="multiple" and not (2<=len(ans)<=4): return False
    for a in ans:
        if a not in q["options"]: return False
    if not (1<=int(q["chapter"][2:])<=14): return False
    return True

# 加载现有题库
existing = json.load(open(os.path.join(BASE,"all_questions.json"),encoding="utf-8"))
print("现有 all_questions 数:", len(existing))

# 加载 14 个章节生成文件
gen_files = sorted(glob.glob(os.path.join(BASE,"gen_ch*.json")))
print("发现章节文件数:", len(gen_files))
allq = list(existing)
ch_counts = {}
for f in gen_files:
    try:
        d = json.load(open(f,encoding="utf-8"))
    except Exception as e:
        print("读取失败", f, e); continue
    if isinstance(d, list):
        allq += d
    elif isinstance(d, dict) and "questions" in d:
        allq += d["questions"]
    ch = os.path.basename(f)
    ch_counts[ch] = len(d) if isinstance(d,list) else 0
print("合并前总数(含重复):", len(allq))

# 去重 + 校验
seen = set()
merged = []
dropped_dup = 0
dropped_bad = 0
for q in allq:
    if not valid(q):
        dropped_bad += 1
        continue
    n = norm(q["stem"])
    if n in seen:
        dropped_dup += 1
        continue
    seen.add(n)
    merged.append(q)

print("去重后有效题数:", len(merged))
print("丢弃-重复:", dropped_dup, " 丢弃-无效:", dropped_bad)

# 章节统计（merged 中实际 chapter 分布）
stat = {}
for q in merged:
    stat[q["chapter"]] = stat.get(q["chapter"],0)+1
print("各章实际题数:")
for c in sorted(stat):
    print(f"  {c}: {stat[c]}")
print("合计:", sum(stat.values()))

# 写出合并题库
out_all = os.path.join(BASE,"all_questions.json")
json.dump(merged, open(out_all,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("已写出 all_questions.json:", len(merged))

# 写今日练习：分层抽样 60 题（每章至少1题，其余随机）
by_ch = {}
for q in merged:
    by_ch.setdefault(q["chapter"], []).append(q)
today = []
for c in sorted(by_ch):
    today.append(by_ch[c][0])
rest = []
for c in sorted(by_ch):
    rest += by_ch[c][1:]
random.shuffle(rest)
need = 60 - len(today)
today += rest[:need]
random.shuffle(today)
json.dump(today, open(os.path.join(BASE,"today.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("已写出 today.json:", len(today))

# 章节映射
chapters = {
 "ch01":"第1章 安装工程的分类、特点及基本工作内容",
 "ch02":"第2章 安装工程常用材料",
 "ch03":"第3章 安装工程施工方法与工艺流程",
 "ch04":"第4章 常用施工机械及检测仪表",
 "ch05":"第5章 施工组织设计",
 "ch06":"第6章 安装工程识图",
 "ch07":"第7章 安装工程计量计价标准",
 "ch08":"第8章 计算机辅助工程量计算",
 "ch09":"第9章 施工图预算的编制",
 "ch10":"第10章 最高投标限价的编制",
 "ch11":"第11章 投标报价的编制",
 "ch12":"第12章 工程价款结算与合同价款调整",
 "ch13":"第13章 竣工决算编制",
 "ch14":"第14章 安装工程计量与计价应用",
}
index = {
 "lastDate":"2026-07-06",
 "lastCount":len(today),
 "totalCount":len(merged),
 "updatedAt":"2026-07-06",
 "chapters":chapters,
 "chapterStat":stat,
}
json.dump(index, open(os.path.join(BASE,"index.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("已写出 index.json")
