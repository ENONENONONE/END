"""TEST 1 - silent consonants by position. Reads aligned.json (from run_align.py).
Seeds: control C1 random.Random(257); control C2 random.Random(258). 20 draws per word each."""
import json, random, math, collections

D = "<scratchpad>/spoken/silent/"
TABLET = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json"
P, G = 257, 3
NDRAW = 20
SEED_C1, SEED_C2 = 257, 258
CONS_L = set("bcdfghjklmnpqrstvwxz")
CATS = list("bcdghklnpstw") + ["gh"]
K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120, 128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
assert len(K) == 33

# ---------------- field tables
DLOG3 = {}
x = 1
for e in range(256):
    DLOG3[x] = e
    x = x * G % P
assert len(DLOG3) == 256
INV55 = pow(55, -1, 256)
assert DLOG3[5] == 55


def ring(n):
    d = DLOG3[n] * INV55 % 256          # dlog5
    m = d % 64
    return min(m, 64 - m)


for n in range(1, P):                      # equivalence check with 7*dlog3
    m = 7 * DLOG3[n] % 64
    assert ring(n) == min(m, 64 - m)


def char(n):
    return DLOG3[n] % 2                    # 0 = QR, 1 = QNR


def gamma(x):
    return (x - 120) * pow((x + 120) % P, P - 2, P) % P


RELS = [("sq", lambda x: x * x % P), ("neg", lambda x: (-x) % P), ("inv", lambda x: pow(x, P - 2, P) if x else None),
        ("x2", lambda x: 2 * x % P), ("half", lambda x: 129 * x % P), ("x17", lambda x: 17 * x % P),
        ("x5", lambda x: 5 * x % P), ("x3", lambda x: 3 * x % P), ("gamma", lambda x: gamma(x) if x != 137 else None)]


def links(a, b):
    out = []
    if a == b:
        out.append("equal")
    for name, f in RELS:
        if f(a) == b:
            out.append(name + ":A->B")
        if f(b) == a:
            out.append(name + ":B->A")
    return out


def triple(w):
    vals = [ord(c) - 96 for c in w]
    return len(vals), sum(vals), sum((i + 1) * v for i, v in enumerate(vals))


def remove(w, idxs):
    s = set(idxs)
    return "".join(c for i, c in enumerate(w) if i not in s)


def metrics(A, B):
    """returns dict m1..m5 (m1, m2 None when a cell is 0)"""
    ok = A != 0 and B != 0
    return {"m1": (char(A) == char(B)) if ok else None,
            "m2": (ring(A) == ring(B)) if ok else None,
            "m3": bool(links(A, B)),
            "m4": B in K,
            "m5": A == B}


def pos_class(i, k):
    return "first" if i == 0 else ("last" if i == k - 1 else "middle")


tab = json.load(open(TABLET))


def name(n):
    return tab[str(n)]["words"][0] if tab.get(str(n), {}).get("words") else ""


# ---------------- load
data = json.load(open(D + "aligned.json"))
rows = data["rows"]
n_k1 = sum(1 for r in rows if len(r["w"]) == 1)
n_k1_sil = sum(1 for r in rows if len(r["w"]) == 1 and r["sil"])
rows = [r for r in rows if len(r["w"]) >= 2]
for r in rows:
    w = r["w"]
    k = len(w)
    allsil = set(r["allsil"])
    r["sounded"] = [i for i, c in enumerate(w) if c in CONS_L and i not in allsil]
    r["snd_first"] = 0 in r["sounded"]
    r["snd_last"] = (k - 1) in r["sounded"]
    r["snd_mid"] = [i for i in r["sounded"] if 0 < i < k - 1]

T = [r for r in rows if r["sil"]]
for r in T:
    w = r["w"]
    k = len(w)
    r["R"] = sorted(i for i, ch, cat in r["sil"])
    cls = [pos_class(i, k) for i in r["R"]]
    r["nf"], r["nm"], r["nl"] = cls.count("first"), cls.count("middle"), cls.count("last")
    kinds = {c for c in cls}
    r["wclass"] = (kinds.pop() + "-only") if len(kinds) == 1 else "mixed"
    r["spoken"] = remove(w, r["R"])
    kk, s, b = triple(w)
    k2, s2, b2 = triple(r["spoken"]) if r["spoken"] else (0, 0, 0)
    r["A"], r["B"] = s % P, s2 % P
    r["s"], r["b"], r["s2"], r["b2"] = s, b, s2, b2
    r["db"] = (b - b2) % P
    r["clean"] = (r["fb"] == 0 and r["ins"] == 0)

# ---------------- (a) counts
counts = {"words_aligned_k>=2": len(rows), "single_letter_headwords_excluded": n_k1,
          "single_letter_headwords_with_silent_consonant": n_k1_sil,
          "words_with_>=1_silent_consonant": len(T),
          "words_with_>=1_silent_consonant_fallback_free": sum(1 for r in T if r["clean"]),
          "silent_consonant_letters_total": sum(len(r["R"]) for r in T)}
cat_letters = collections.Counter()
cat_units = collections.Counter()
cat_pos = collections.defaultdict(collections.Counter)
for r in T:
    k = len(r["w"])
    seen_gh = set()
    for i, ch, cat in r["sil"]:
        cat_letters[cat] += 1
        cat_pos[cat][pos_class(i, k)] += 1
        if cat == "gh":
            if i - 1 not in seen_gh:
                cat_units["gh"] += 1
            seen_gh.add(i)
        else:
            cat_units[cat] += 1
pos_tot = collections.Counter()
for c in cat_pos:
    pos_tot.update(cat_pos[c])
nsil_dist = collections.Counter(len(r["R"]) for r in T)
wclass_dist = collections.Counter(r["wclass"] for r in T)
other_sil = collections.Counter(ch for r in rows for i, ch in r["other"])
words_other_only = sum(1 for r in rows if r["other"] and not r["sil"])
countsA = {"counts": counts,
           "by_category_units": {c: cat_units[c] for c in CATS},
           "by_category_letters": {c: cat_letters[c] for c in CATS},
           "category_x_position_letters": {c: {p: cat_pos[c][p] for p in ("first", "middle", "last")} for c in CATS},
           "position_totals_letters": {p: pos_tot[p] for p in ("first", "middle", "last")},
           "silent_letters_per_word": dict(sorted(nsil_dist.items())),
           "word_position_class": dict(wclass_dist),
           "other_silent_consonants_not_in_test_set": dict(other_sil),
           "words_with_only_other_silent_consonants": words_other_only,
           "spoken_form_empty": sum(1 for r in T if not r["spoken"]),
           "spelled_cell_zero": sum(1 for r in T if r["A"] == 0),
           "spoken_cell_zero": sum(1 for r in T if r["B"] == 0)}

# ---------------- controls
rng1 = random.Random(SEED_C1)
rng2 = random.Random(SEED_C2)
bylen = collections.defaultdict(list)
for idx, r in enumerate(rows):
    bylen[len(r["w"])].append(idx)
pool_cache = {}


def pool(k, needF, needL, nm):
    key = (k, needF, needL, nm)
    if key not in pool_cache:
        pool_cache[key] = [i for i in bylen[k]
                           if (not needF or rows[i]["snd_first"]) and (not needL or rows[i]["snd_last"])
                           and len(rows[i]["snd_mid"]) >= nm]
    return pool_cache[key]


widx = {r["w"]: i for i, r in enumerate(rows)}
verify_ctrl_fail = 0
verify_ctrl_steps = 0


def seq_remove_check(w, idxs):
    """remove idxs right-to-left; check each step b_before - b_after == j*v + sum(after j). returns (steps, fails)."""
    global verify_ctrl_fail, verify_ctrl_steps
    cur = w
    st = fl = 0
    for i in sorted(idxs, reverse=True):
        _, _, b0 = triple(cur)
        j = i + 1
        v = ord(cur[i]) - 96
        after = sum(ord(c) - 96 for c in cur[i + 1:])
        nxt = cur[:i] + cur[i + 1:]
        _, _, b1 = triple(nxt) if nxt else (0, 0, 0)
        st += 1
        if b0 - b1 != j * v + after:
            fl += 1
        cur = nxt
    return st, fl


for r in T:
    w = r["w"]
    k = len(w)
    # C1: same word, same position class
    r["C1"] = None
    if r["nf"] == 0 and r["nl"] == 0 and len(r["snd_mid"]) >= r["nm"]:
        draws = []
        for d in range(NDRAW):
            pick = rng1.sample(r["snd_mid"], r["nm"])
            sp = remove(w, pick)
            _, s2, b2 = triple(sp) if sp else (0, 0, 0)
            a, c = seq_remove_check(w, pick)
            verify_ctrl_steps += a
            verify_ctrl_fail += c
            draws.append({"B": s2 % P, "db": (r["b"] - b2) % P, "pick": pick})
        r["C1"] = draws
    # C2: other words of same length, same numbers removed per position class
    pl = pool(k, r["nf"] > 0, r["nl"] > 0, r["nm"])
    me = widx[w]
    cand = pl if not (len(pl) == 1 and pl[0] == me) else []
    draws = []
    if cand:
        for d in range(NDRAW):
            while True:
                oi = rng2.choice(cand)
                if oi != me:
                    break
            o = rows[oi]
            ow = o["w"]
            pick = []
            if r["nf"]:
                pick.append(0)
            if r["nl"]:
                pick.append(k - 1)
            if r["nm"]:
                pick += rng2.sample(o["snd_mid"], r["nm"])
            _, s1, b1 = triple(ow)
            sp = remove(ow, pick)
            _, s2, b2 = triple(sp) if sp else (0, 0, 0)
            a, c = seq_remove_check(ow, pick)
            verify_ctrl_steps += a
            verify_ctrl_fail += c
            draws.append({"w": ow, "A": s1 % P, "B": s2 % P, "db": (b1 - b2) % P, "pick": sorted(pick)})
    r["C2"] = draws if draws else None

# ---------------- metric aggregation


def agg_obs(sub):
    out = {}
    for m in ("m1", "m2", "m3", "m4", "m5"):
        vals = [metrics(r["A"], r["B"])[m] for r in sub]
        v = [x for x in vals if x is not None]
        out[m] = {"hits": sum(v), "n": len(v), "rate": round(sum(v) / len(v), 6) if v else None, "excluded_zero": len(vals) - len(v)}
    dbk = [r["db"] in K for r in sub]
    out["db_in_K"] = {"hits": sum(dbk), "n": len(dbk), "rate": round(sum(dbk) / len(dbk), 6) if dbk else None}
    out["A_in_K_context"] = {"hits": sum(r["A"] in K for r in sub), "n": len(sub)}
    return out


def agg_ctrl(sub, key):
    out = {}
    sub = [r for r in sub if r[key]]
    for m in ("m1", "m2", "m3", "m4", "m5"):
        hits = n = excl = 0
        per_draw = []
        for d in range(NDRAW):
            h = c = 0
            for r in sub:
                dr = r[key][d]
                A = dr.get("A", r["A"])
                v = metrics(A, dr["B"])[m]
                if v is None:
                    excl += 1
                    continue
                c += 1
                h += v
            hits += h
            n += c
            per_draw.append(h / c if c else float("nan"))
        mu = sum(per_draw) / len(per_draw)
        sd = math.sqrt(sum((x - mu) ** 2 for x in per_draw) / (len(per_draw) - 1)) if len(per_draw) > 1 else 0
        out[m] = {"hits": hits, "n": n, "rate": round(hits / n, 6) if n else None, "excluded_zero_draws": excl,
                  "per_draw_min": round(min(per_draw), 6), "per_draw_max": round(max(per_draw), 6), "per_draw_sd": round(sd, 6)}
    hits = n = 0
    per_draw = []
    for d in range(NDRAW):
        h = sum(r[key][d]["db"] in K for r in sub)
        hits += h
        n += len(sub)
        per_draw.append(h / len(sub) if sub else float("nan"))
    mu = sum(per_draw) / len(per_draw)
    sd = math.sqrt(sum((x - mu) ** 2 for x in per_draw) / (len(per_draw) - 1))
    out["db_in_K"] = {"hits": hits, "n": n, "rate": round(hits / n, 6) if n else None,
                      "per_draw_min": round(min(per_draw), 6), "per_draw_max": round(max(per_draw), 6), "per_draw_sd": round(sd, 6)}
    out["words"] = len(sub)
    if key == "C2":
        out["A_in_K_context"] = {"hits": sum(r[key][d]["A"] in K for r in sub for d in range(NDRAW)), "n": len(sub) * NDRAW}
    return out


def zscore(obs, ctrl):
    res = {}
    for m in ("m1", "m2", "m3", "m4", "m5", "db_in_K"):
        o, c = obs[m], ctrl[m]
        if not o["n"] or c["rate"] is None:
            res[m] = None
            continue
        p = c["rate"]
        if p <= 0 or p >= 1:
            res[m] = None
            continue
        res[m] = round((o["hits"] - o["n"] * p) / math.sqrt(o["n"] * p * (1 - p)), 3)
    return res


def block(sub):
    obs = agg_obs(sub)
    c1sub = [r for r in sub if r["C1"]]
    res = {"n_words": len(sub), "observed": obs}
    if c1sub:
        o1 = agg_obs(c1sub)
        c1 = agg_ctrl(c1sub, "C1")
        res["C1_same_word"] = {"n_words_eligible": len(c1sub), "observed_on_eligible": o1, "control": c1, "z_obs_vs_control": zscore(o1, c1)}
    else:
        res["C1_same_word"] = {"n_words_eligible": 0}
    c2sub = [r for r in sub if r["C2"]]
    o2 = agg_obs(c2sub)
    c2 = agg_ctrl(c2sub, "C2")
    res["C2_matched_words"] = {"n_words_eligible": len(c2sub), "observed_on_eligible": o2, "control": c2, "z_obs_vs_control": zscore(o2, c2)}
    return res


results = {"seeds": {"C1": SEED_C1, "C2": SEED_C2, "draws_per_word": NDRAW}, "a_counts": countsA}
results["b_c_all"] = block(T)
results["b_c_fallback_free"] = block([r for r in T if r["clean"]])
results["e_by_class"] = {c: block([r for r in T if r["wclass"] == c]) for c in ("first-only", "middle-only", "last-only", "mixed")}
results["e_by_category_single_unit_words"] = {}
for c in CATS:
    sub = [r for r in T if {x[2] for x in r["sil"]} == {c}]
    results["e_by_category_single_unit_words"][c] = {"n_words": len(sub), "observed": agg_obs(sub)} if sub else {"n_words": 0}

# relation breakdown for m3
rel_obs = collections.Counter()
for r in T:
    for l in links(r["A"], r["B"]):
        rel_obs[l] += 1
rel_c2 = collections.Counter()
nc2 = 0
for r in T:
    if r["C2"]:
        for dr in r["C2"]:
            nc2 += 1
            for l in links(dr["A"], dr["B"]):
                rel_c2[l] += 1
rel_c1 = collections.Counter()
nc1 = 0
for r in T:
    if r["C1"]:
        for dr in r["C1"]:
            nc1 += 1
            for l in links(r["A"], dr["B"]):
                rel_c1[l] += 1
results["m3_relation_breakdown"] = {"observed": dict(rel_obs), "observed_n": len(T), "C1": dict(rel_c1), "C1_n": nc1, "C2": dict(rel_c2), "C2_n": nc2}

# delta s distribution (sum of silent letters), context
ds = collections.Counter((r["s"] - r["s2"]) for r in T)
results["delta_s_top"] = ds.most_common(15)
dbc = collections.Counter(r["db"] for r in T if r["db"] in K)
results["db_in_K_observed_by_cell"] = dict(sorted(dbc.items()))

# ---------------- (d) verification
ver = {"steps": 0, "fails": 0, "single_first_words": 0, "single_first_ok": 0, "single_last_words": 0, "single_last_ok": 0,
       "first_letter_steps_in_multi": 0, "first_letter_steps_ok": 0}
for r in T:
    w = r["w"]
    a, c = seq_remove_check(w, r["R"])
    ver["steps"] += a
    ver["fails"] += c
    # closed form over the whole removal: b_spelled - b_spoken (integer)
    if len(r["R"]) == 1:
        i = r["R"][0]
        v = ord(w[i]) - 96
        if i == 0:
            ver["single_first_words"] += 1
            ver["single_first_ok"] += int(r["b"] - r["b2"] == r["s"])
        if i == len(w) - 1:
            ver["single_last_words"] += 1
            ver["single_last_ok"] += int(r["b"] - r["b2"] == len(w) * v)
    if 0 in r["R"] and len(r["R"]) > 1:
        # right-to-left: the first letter is removed last, from the string cur; check drop == s(cur)
        cur = remove(w, [i for i in r["R"] if i != 0])
        _, s_cur, b_cur = triple(cur)
        _, _, b_after = triple(cur[1:]) if len(cur) > 1 else (0, 0, 0)
        ver["first_letter_steps_in_multi"] += 1
        ver["first_letter_steps_ok"] += int(b_cur - b_after == s_cur)
ver["control_steps"] = verify_ctrl_steps
ver["control_fails"] = verify_ctrl_fail
results["d_verification"] = ver

# context: mean value of removed letters, observed vs controls
def mean(x):
    return round(sum(x) / len(x), 4) if x else None
obs_rm = [ord(r["w"][i]) - 96 for r in T for i in r["R"]]
c1_rm = [ord(r["w"][i]) - 96 for r in T if r["C1"] for dr in r["C1"] for i in dr["pick"]]
c2_rm = [ord(dr["w"][i]) - 96 for r in T if r["C2"] for dr in r["C2"] for i in dr["pick"]]
c1_obs_rm = [ord(r["w"][i]) - 96 for r in T if r["C1"] for i in r["R"]]
results["context_removed_letter_mean_value"] = {"observed_all": mean(obs_rm), "observed_C1_eligible": mean(c1_obs_rm),
    "C1": mean(c1_rm), "C2": mean(c2_rm)}
# examples: linked (m3) and db in K, fallback-free, alphabetical first 25 each
ex_link = [(r["w"], r["spoken"], r["A"], name(r["A"]), r["B"], name(r["B"]), links(r["A"], r["B"]), r["wclass"])
           for r in sorted(T, key=lambda r: r["w"]) if r["clean"] and links(r["A"], r["B"])]
ex_db = [(r["w"], r["spoken"], r["b"], r["b2"], r["db"], name(r["db"]), r["wclass"])
         for r in sorted(T, key=lambda r: r["w"]) if r["clean"] and r["db"] in K]
with open(D + "examples_linked_and_dbK.txt", "w") as f:
    f.write("# m3-linked words (fallback-free): word spoken A[name] B[name] relations class\n")
    for e in ex_link:
        f.write(f"{e[0]}\t{e[1]}\tA={e[2]}[{e[3]}]\tB={e[4]}[{e[5]}]\t{','.join(e[6])}\t{e[7]}\n")
    f.write("\n# db in K (fallback-free): word spoken b_spelled b_spoken db[name] class\n")
    for e in ex_db:
        f.write(f"{e[0]}\t{e[1]}\t{e[2]}\t{e[3]}\tdb={e[4]}[{e[5]}]\t{e[6]}\n")
results["n_examples_linked_fallback_free"] = len(ex_link)
results["n_examples_dbK_fallback_free"] = len(ex_db)
json.dump(results, open(D + "test1_results.json", "w"), indent=1, ensure_ascii=False)

# ---------------- sample of 40
SAMPLE = ["hour", "honest", "knight", "know", "gnome", "write", "psalm", "listen", "castle", "island", "debt", "doubt",
          "salmon", "calm", "walk", "half", "could", "autumn", "column", "hymn", "wednesday", "christ", "ghost", "rhythm",
          "sign", "answer", "sword", "whole", "light", "thought",
          "lamb", "knee", "wrong", "often", "receipt", "muscle", "subtle", "foreign", "phone", "church"]
EXPECT = {"hour": "h0", "honest": "h0", "knight": "k0 g3 h4", "know": "k0", "gnome": "g0", "write": "w0", "psalm": "p0",
          "listen": "t3", "castle": "t3", "island": "s1", "debt": "b2", "doubt": "b3", "salmon": "l2", "calm": "l2", "walk": "l2",
          "half": "l2", "could": "l3", "autumn": "n5", "column": "n5", "hymn": "n3", "wednesday": "d2", "christ": "", "ghost": "h1",
          "rhythm": "h1", "sign": "g2", "answer": "w3", "sword": "w1", "whole": "w0", "light": "g2 h3", "thought": "g4 h5",
          "lamb": "b3", "knee": "k0", "wrong": "w0", "often": "t2", "receipt": "p5", "muscle": "c3", "subtle": "b2",
          "foreign": "g5", "phone": "", "church": ""}
import sys
sys.path.insert(0, D)
from aligner import render
lines = []
agree = 0
full = {r["w"]: r for r in rows}
Tm = {r["w"]: r for r in T}
for w in SAMPLE:
    r = full[w]
    got = " ".join(f"{ch}{i}" for i, ch, cat in sorted(r["sil"]))
    ok = got == EXPECT[w]
    agree += ok
    st = [(a, b, tuple(s), t) for a, b, s, t in r["steps"]]
    k, s, b = triple(w)
    if w in Tm:
        t = Tm[w]
        A, B = t["A"], t["B"]
        mt = metrics(A, B)
        lk = links(A, B)
        extra = (f"spoken={t['spoken']} k,s,b=({k},{s},{b})->({len(t['spoken'])},{t['s2']},{t['b2']}) "
                 f"A={A}[{name(A)}] B={B}[{name(B)}] charA={'QR' if char(A)==0 else 'QNR'} charB={'QR' if char(B)==0 else 'QNR'} "
                 f"ringA={ring(A)} ringB={ring(B)} m1={int(mt['m1'])} m2={int(mt['m2'])} m3={int(mt['m3'])}{lk if lk else ''} "
                 f"m4={int(mt['m4'])} m5={int(mt['m5'])} db={t['db']}{' inK' if t['db'] in K else ''} class={t['wclass']}")
    else:
        extra = f"no silent consonant; k,s,b=({k},{s},{b}) A={s%P}[{name(s%P)}]"
    lines.append(f"{w:10s} | {r['ph']:22s} | {render(w, st)} | silent={got or '-'} | expected={EXPECT[w] or '-'} | {'agree' if ok else 'DISAGREE'} | {extra}")
open(D + "sample40.txt", "w").write("\n".join(lines) + f"\n\nagreement {agree}/40\n")
results["sample40_agreement"] = agree
json.dump(results, open(D + "test1_results.json", "w"), indent=1, ensure_ascii=False)
print("agreement", agree, "/40")
print(json.dumps(countsA, indent=1))
