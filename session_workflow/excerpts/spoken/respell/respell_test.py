#!/usr/bin/env python3
"""TEST 2 - PHONETIC RESPELLINGS.

Spelled headword cell A vs respelled (ARPAbet -> Latin) cell B, two fixed schemes P and M,
metrics m1..m5, matched random control, the "hi" family, and the letter-sum difference distribution.

Seeds: control (b) draw d uses random.Random(1000 + d) for all-words pairing and
random.Random(2000 + d) for the non-identical-subset pairing, d = 1..5, per scheme offset
(scheme P +0, scheme M +10). Family control (c) uses random.Random(3000) (P/M: 3001, 3002).
Example sample uses random.Random(4000).
"""
import re, json, random, collections, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
CMU = "<scratchpad>/cmu/cmudict.dict"
TABLET = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json"

# ---------------------------------------------------------------- respelling schemes (fixed a priori)
SCHEME_P = {
    "AA": "O", "AE": "A", "AH": "U", "AO": "AW", "AW": "OW", "AY": "AI", "EH": "E", "ER": "ER",
    "EY": "AY", "IH": "I", "IY": "EE", "OW": "OH", "OY": "OY", "UH": "OO", "UW": "OO",
    "B": "B", "CH": "CH", "D": "D", "DH": "TH", "F": "F", "G": "G", "HH": "H", "JH": "J", "K": "K",
    "L": "L", "M": "M", "N": "N", "NG": "NG", "P": "P", "R": "R", "S": "S", "SH": "SH", "T": "T",
    "TH": "TH", "V": "V", "W": "W", "Y": "Y", "Z": "Z", "ZH": "ZH",
}
VOWELS = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"]
SCHEME_M = {}
for ph, sp in SCHEME_P.items():
    SCHEME_M[ph] = sp[0] if ph in VOWELS else None
SCHEME_M.update({"B": "B", "CH": "C", "D": "D", "DH": "D", "F": "F", "G": "G", "HH": "H", "JH": "J",
                 "K": "K", "L": "L", "M": "M", "N": "N", "NG": "N", "P": "P", "R": "R", "S": "S",
                 "SH": "S", "T": "T", "TH": "T", "V": "V", "W": "W", "Y": "Y", "Z": "Z", "ZH": "Z"})
assert all(v is not None and len(v) == 1 for v in SCHEME_M.values())
SCHEMES = {"P": SCHEME_P, "M": SCHEME_M}

# ---------------------------------------------------------------- field
P = 257
DLOG3 = [None] * P
x = 1
for k in range(256):
    DLOG3[x] = k
    x = x * 3 % P
assert all(DLOG3[n] is not None for n in range(1, P))
DLOG5 = [None] * P
x = 1
for k in range(256):
    DLOG5[x] = k
    x = x * 5 % P
assert all(DLOG5[n] is not None for n in range(1, P))  # 5 is a generator


def inv(n):
    return pow(n, 255, P)


def char(n):  # 0 = QR, 1 = QNR, None for 0
    return None if n == 0 else DLOG3[n] % 2


def ring(n):
    if n == 0:
        return None
    d = DLOG5[n] % 64
    r = min(d, 64 - d)
    d7 = (7 * DLOG3[n]) % 64
    assert r == min(d7, 64 - d7)
    return r


def gamma(x):
    if x == 137:
        return None
    return (x - 120) * inv((x + 120) % P) % P


REL_NAMES = ["sq", "neg", "inv", "x2", "half", "x17", "x5", "x3", "gamma"]


def images(x):
    return {
        "sq": x * x % P, "neg": (-x) % P, "inv": inv(x) if x else None, "x2": 2 * x % P,
        "half": 129 * x % P, "x17": 17 * x % P, "x5": 5 * x % P, "x3": 3 * x % P, "gamma": gamma(x),
    }


IMG = [images(x) for x in range(P)]
# REL[x][y] = set of relation names holding x->y or y->x
REL = [[set() for _ in range(P)] for _ in range(P)]
for a in range(P):
    for name, v in IMG[a].items():
        if v is not None:
            REL[a][v].add(name)
            REL[v][a].add(name)
LINKED = [[(a == b) or bool(REL[a][b]) for b in range(P)] for a in range(P)]

K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120, 128, 129, 136,
     137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
assert len(K) == 33

try:
    TAB = json.load(open(TABLET))
    NAME = {int(k): (v.get("words") or [""])[0] for k, v in TAB.items()}
except Exception:
    NAME = {}


def triple(word):
    vals = [ord(c) - 64 for c in word.upper() if "A" <= c.upper() <= "Z"]
    k = len(vals)
    s = sum(vals)
    b = sum((i + 1) * v for i, v in enumerate(vals))
    return k, s, b


# ---------------------------------------------------------------- metrics
def metrics(pairs):
    """pairs: list of (A, B) cells. Returns counts and rates for m1..m5 plus relation breakdown."""
    n = len(pairs)
    nz = [(a, b) for a, b in pairs if a != 0 and b != 0]
    m1 = sum(1 for a, b in nz if char(a) == char(b))
    m2 = sum(1 for a, b in nz if ring(a) == ring(b))
    m3 = sum(1 for a, b in pairs if LINKED[a][b])
    m3_neq = sum(1 for a, b in pairs if a != b and REL[a][b])
    m4 = sum(1 for a, b in pairs if b in K)
    m5 = sum(1 for a, b in pairs if a == b)
    rel = {r: sum(1 for a, b in pairs if r in REL[a][b]) for r in REL_NAMES}
    fd = sorted(min((a - b) % P, (b - a) % P) for a, b in pairs)
    out = {
        "n_pairs": n,
        "n_pairs_with_zero_cell": n - len(nz),
        "n_A_zero": sum(1 for a, b in pairs if a == 0),
        "n_B_zero": sum(1 for a, b in pairs if b == 0),
        "m1_same_char": [m1, len(nz), m1 / len(nz) if nz else None],
        "m2_same_ring": [m2, len(nz), m2 / len(nz) if nz else None],
        "m3_linked": [m3, n, m3 / n if n else None],
        "m4_B_in_K": [m4, n, m4 / n if n else None],
        "m5_same_cell": [m5, n, m5 / n if n else None],
        "extra_m3_linked_excluding_equal_cells": [m3_neq, n, m3_neq / n if n else None],
        "extra_relation_counts_either_direction": rel,
        "extra_folded_cell_distance": {"median": fd[len(fd) // 2] if fd else None,
                                       "share_le_10": sum(1 for d in fd if d <= 10) / len(fd) if fd else None},
    }
    return out


def summarize_draws(draws):
    keys = ["m1_same_char", "m2_same_ring", "m3_linked", "m4_B_in_K", "m5_same_cell",
            "extra_m3_linked_excluding_equal_cells"]
    return {k: {"rates": [d[k][2] for d in draws],
                "mean": statistics.mean(d[k][2] for d in draws),
                "min": min(d[k][2] for d in draws), "max": max(d[k][2] for d in draws)}
            for k in keys}


# ---------------------------------------------------------------- data
def load():
    prons = collections.defaultdict(dict)  # word -> {idx: [phones]}
    skipped = collections.Counter()
    n_lines = 0
    for line in open(CMU, encoding="utf-8"):
        n_lines += 1
        body = line.split("#", 1)[0].strip()
        if not body:
            skipped["blank_or_comment_only"] += 1
            continue
        parts = body.split()
        head, phones = parts[0], parts[1:]
        m = re.fullmatch(r"([a-z]+)(?:\((\d+)\))?", head)
        if not m:
            if "'" in head:
                skipped["apostrophe"] += 1
            elif re.search(r"\d", re.sub(r"\(\d+\)$", "", head)):
                skipped["digit_in_headword"] += 1
            else:
                skipped["other_non_alpha"] += 1
            continue
        w = m.group(1)
        idx = int(m.group(2)) if m.group(2) else 1
        prons[w][idx] = phones
    return prons, skipped, n_lines


def strip(ph):
    return re.sub(r"\d", "", ph)


def respell(phones, scheme):
    return "".join(scheme[strip(p)] for p in phones)


def main():
    prons, skipped, n_lines = load()
    words = sorted(prons)
    rows = []
    for w in words:
        first = prons[w][min(prons[w])]
        k, s, b = triple(w)
        row = {"word": w, "phones": " ".join(first), "k": k, "s": s, "b": b, "cell": s % P}
        for sc, table in SCHEMES.items():
            r = respell(first, table)
            rk, rs, rb = triple(r)
            row[sc] = {"resp": r, "k": rk, "s": rs, "b": rb, "cell": rs % P, "identical": r == w.upper()}
        rows.append(row)

    res = {"data": {"cmu_lines": n_lines, "headwords_used": len(rows),
                    "entries_skipped": dict(skipped),
                    "headwords_with_variant_pronunciations": sum(1 for w in words if len(prons[w]) > 1),
                    "spelled_cell_zero": [r["word"] for r in rows if r["cell"] == 0]},
           "schemes": {"P": SCHEME_P, "M": SCHEME_M}}

    # (a) observed
    res["a"] = {}
    for sc in SCHEMES:
        allp = [(r["cell"], r[sc]["cell"]) for r in rows]
        nonid = [(r["cell"], r[sc]["cell"]) for r in rows if not r[sc]["identical"]]
        ident = [r["word"] for r in rows if r[sc]["identical"]]
        res["a"][sc] = {
            "n_identical": len(ident), "share_identical": len(ident) / len(rows),
            "identical_words_first40": ident[:40],
            "respelled_cell_zero_count": sum(1 for r in rows if r[sc]["cell"] == 0),
            "respelled_cell_zero_words_first40": [r["word"] for r in rows if r[sc]["cell"] == 0][:40],
            "all": metrics(allp),
            "without_identical": metrics(nonid),
        }

    # (b) control
    res["b"] = {}
    for off, sc in ((0, "P"), (10, "M")):
        strata = collections.defaultdict(list)
        strata_ni = collections.defaultdict(list)
        for i, r in enumerate(rows):
            key = (r["k"], r[sc]["k"])
            strata[key].append(i)
            if not r[sc]["identical"]:
                strata_ni[key].append(i)
        singletons = sum(1 for i, r in enumerate(rows) if len(strata[(r["k"], r[sc]["k"])]) < 2)
        singletons_ni = sum(1 for i, r in enumerate(rows)
                            if not r[sc]["identical"] and len(strata_ni[(r["k"], r[sc]["k"])]) < 2)
        draws_all, draws_ni = [], []
        for d in range(1, 6):
            rng = random.Random(1000 + off + d)
            pairs = []
            for i, r in enumerate(rows):
                pool = strata[(r["k"], r[sc]["k"])]
                if len(pool) < 2:
                    continue
                j = i
                while j == i:
                    j = pool[rng.randrange(len(pool))]
                pairs.append((r["cell"], rows[j][sc]["cell"]))
            draws_all.append(metrics(pairs))
            rng = random.Random(2000 + off + d)
            pairs = []
            for i, r in enumerate(rows):
                if r[sc]["identical"]:
                    continue
                pool = strata_ni[(r["k"], r[sc]["k"])]
                if len(pool) < 2:
                    continue
                j = i
                while j == i:
                    j = pool[rng.randrange(len(pool))]
                pairs.append((r["cell"], rows[j][sc]["cell"]))
            draws_ni.append(metrics(pairs))
        res["b"][sc] = {
            "seeds_all": [1000 + off + d for d in range(1, 6)],
            "seeds_without_identical": [2000 + off + d for d in range(1, 6)],
            "words_unpairable_singleton_stratum_all": singletons,
            "words_unpairable_singleton_stratum_without_identical": singletons_ni,
            "draws_all": draws_all, "summary_all": summarize_draws(draws_all),
            "draws_without_identical": draws_ni, "summary_without_identical": summarize_draws(draws_ni),
        }
        bb = res["b"][sc]
        for tag, obsm, summ, dr in (("all", res["a"][sc]["all"], bb["summary_all"], draws_all),
                                    ("without_identical", res["a"][sc]["without_identical"],
                                     bb["summary_without_identical"], draws_ni)):
            z = {}
            for k, v in summ.items():
                o, n = obsm[k][2], obsm[k][1]
                mu = v["mean"]
                se = (mu * (1 - mu) / n) ** 0.5
                z[k] = {"observed": o, "control_mean": mu, "diff": o - mu, "binomial_se": se,
                        "z": (o - mu) / se if se else None}
            bb["z_" + tag] = z
            bb["mean_relation_counts_" + tag] = {r: statistics.mean(d["extra_relation_counts_either_direction"][r] for d in dr)
                                                 for r in REL_NAMES}
            bb["mean_folded_distance_" + tag] = {
                "median_mean": statistics.mean(d["extra_folded_cell_distance"]["median"] for d in dr),
                "share_le_10_mean": statistics.mean(d["extra_folded_cell_distance"]["share_le_10"] for d in dr)}

    # (c) the "hi" family
    fam = []
    near = []
    for w in words:
        for idx, ph in sorted(prons[w].items()):
            if ph == ["HH", "AY1"]:
                fam.append((w, idx))
            elif [strip(p) for p in ph] == ["HH", "AY"]:
                near.append((w, idx, " ".join(ph)))
    rowmap = {r["word"]: r for r in rows}

    def cellinfo(n):
        return {"cell": n, "name": NAME.get(n, ""), "dlog3": DLOG3[n] if n else None,
                "char": (None if n == 0 else ("QR" if char(n) == 0 else "QNR")), "ring": ring(n),
                "in_K": n in K}

    hi_P = respell(["HH", "AY1"], SCHEME_P)
    hi_M = respell(["HH", "AY1"], SCHEME_M)
    cP, cM = triple(hi_P)[1] % P, triple(hi_M)[1] % P
    by_len = collections.defaultdict(list)
    for r in rows:
        by_len[r["k"]].append(r)
    NDRAW = 10000
    keys = ["m1_same_char", "m2_same_ring", "m3_linked", "m4_B_in_K", "m5_same_cell"]

    def dist(vals, obsv):
        c = collections.Counter(round(v, 6) for v in vals if v is not None)
        return {"mean": statistics.mean(v for v in vals if v is not None),
                "share_draws_ge_observed": sum(1 for v in vals if v is not None and v >= obsv) / len(vals),
                "share_draws_le_observed": sum(1 for v in vals if v is not None and v <= obsv) / len(vals),
                "distribution": {str(k): c[k] / len(vals) for k in sorted(c)}}

    all_fam = sorted({w for w, _ in fam})
    first_fam = sorted({w for w, i in fam if i == min(prons[w])})
    res["c"] = {"entries_HH_AY1": [[w, i] for w, i in fam],
                "near_other_stress_not_in_family": [{"word": w, "idx": i, "pron": p,
                                                     **cellinfo(triple(w)[1] % P)} for w, i, p in near],
                "resp_P": {"resp": hi_P, "triple": triple(hi_P), **cellinfo(cP)},
                "resp_M": {"resp": hi_M, "triple": triple(hi_M), **cellinfo(cM)},
                "P_vs_M": {"relations": sorted(REL[cP][cM]), "metrics": metrics([(cP, cM)])}}
    for label, fam_words, seedbase in (("family_any_pronunciation", all_fam, 3000),
                                        ("family_first_pronunciation", first_fam, 3100)):
        fam_rows = []
        for w in fam_words:
            k, s, b = triple(w)
            fam_rows.append({"word": w, "pron_indices_HH_AY1": [i for ww, i in fam if ww == w],
                             "first_pron": " ".join(prons[w][min(prons[w])]),
                             "k": k, "s": s, "b": b, **cellinfo(s % P)})
        fcells = [(r["word"], r["cell"]) for r in fam_rows]
        ss_pairs = [(a, b) for wa, a in fcells for wb, b in fcells if wa != wb]
        fam_res = {
            "members": fam_rows,
            "pairwise_link_detail": [{"A": wa, "B": wb, "A_cell": a, "B_cell": b,
                                      "relations": sorted(REL[a][b]), "equal": a == b}
                                     for wa, a in fcells for wb, b in fcells if wa < wb],
            "member_vs_P_detail": [{"A": wa, "A_cell": a, "B_cell": cP, "relations": sorted(REL[a][cP])} for wa, a in fcells],
            "member_vs_M_detail": [{"A": wa, "A_cell": a, "B_cell": cM, "relations": sorted(REL[a][cM])} for wa, a in fcells],
            "metrics_spelled_vs_spelled_ordered_pairs": metrics(ss_pairs),
            "metrics_spelled_vs_P": metrics([(a, cP) for _, a in fcells]),
            "metrics_spelled_vs_M": metrics([(a, cM) for _, a in fcells]),
        }
        famset = set(all_fam)
        # control 1: random non-family words, one per member, same spelled length, distinct
        rng = random.Random(seedbase)
        acc = {k: [] for k in keys}
        for _ in range(NDRAW):
            pick = []
            for fr in fam_rows:
                pool = by_len[fr["k"]]
                while True:
                    c = pool[rng.randrange(len(pool))]
                    if c["word"] not in famset and c["word"] not in [p["word"] for p in pick]:
                        break
                pick.append(c)
            pc = [(c["word"], c["cell"]) for c in pick]
            m = metrics([(a, b) for wa, a in pc for wb, b in pc if wa != wb])
            for k in keys:
                acc[k].append(m[k][2])
        obs = fam_res["metrics_spelled_vs_spelled_ordered_pairs"]
        fam_res["control_spelled_vs_spelled"] = {
            "seed": seedbase, "draws": NDRAW,
            "note": "one random non-family word per member with the member's spelled length; ordered pairs among them",
            **{k: dist(acc[k], obs[k][2]) for k in keys}}
        # control 2: member spelled cell vs respelled cell of random non-family word with the
        # member's spelled length and the family respelling's length
        for sc, seed, respstr in (("P", seedbase + 1, hi_P), ("M", seedbase + 2, hi_M)):
            rng = random.Random(seed)
            acc = {k: [] for k in keys}
            obsm = fam_res["metrics_spelled_vs_" + sc]
            pools = {fr["word"]: [r for r in by_len[fr["k"]] if r[sc]["k"] == len(respstr) and r["word"] not in famset]
                     for fr in fam_rows}
            for _ in range(NDRAW):
                pairs = []
                for fr in fam_rows:
                    pool = pools[fr["word"]]
                    c = pool[rng.randrange(len(pool))]
                    pairs.append((fr["cell"], c[sc]["cell"]))
                m = metrics(pairs)
                for k in keys:
                    acc[k].append(m[k][2])
            fam_res["control_spelled_vs_" + sc] = {
                "seed": seed, "draws": NDRAW,
                "pool_sizes": {w: len(v) for w, v in pools.items()},
                "note": "B = respelled cell of a random non-family word with the member's spelled length and respelled length %d" % len(respstr),
                **{k: dist(acc[k], obsm[k][2]) for k in keys}}
        res["c"][label] = fam_res

    # (d) difference distribution
    res["d"] = {}
    for sc in SCHEMES:
        diffs = [r["s"] - r[sc]["s"] for r in rows]
        cnt = collections.Counter(diffs)
        diffs_ni = [r["s"] - r[sc]["s"] for r in rows if not r[sc]["identical"]]
        cnt_ni = collections.Counter(diffs_ni)
        cellcnt = collections.Counter(d % P for d in diffs)
        res["d"][sc] = {
            "n": len(diffs), "mean": statistics.mean(diffs), "median": statistics.median(diffs),
            "stdev": statistics.pstdev(diffs), "min": min(diffs), "max": max(diffs),
            "share_zero": cnt[0] / len(diffs),
            "top20": [[v, c, c / len(diffs)] for v, c in cnt.most_common(20)],
            "top20_without_identical": [[v, c, c / len(diffs_ni)] for v, c in cnt_ni.most_common(20)],
            "top10_mod257": [[v, c, c / len(diffs)] for v, c in cellcnt.most_common(10)],
            "examples_top5_values": {str(v): [r["word"] + ">" + r[sc]["resp"] for r in rows if r["s"] - r[sc]["s"] == v][:8]
                                     for v, _ in cnt.most_common(5)},
        }

    # examples
    rng = random.Random(4000)
    sample = rng.sample(rows, 12)
    fixed = ["knight", "psalm", "hour", "island", "debt", "write", "gnome", "listen", "colonel", "wednesday"]

    def ex(r):
        return {"word": r["word"], "phones": r["phones"], "spelled": [r["k"], r["s"], r["b"], r["cell"]],
                **{sc: [r[sc]["resp"], r[sc]["k"], r[sc]["s"], r[sc]["b"], r[sc]["cell"],
                        sorted(REL[r["cell"]][r[sc]["cell"]]) + (["equal"] if r["cell"] == r[sc]["cell"] else [])]
                   for sc in SCHEMES}}
    res["examples_random_seed4000"] = [ex(r) for r in sample]
    res["examples_fixed_silent_letter_list"] = [ex(rowmap[w]) for w in fixed if w in rowmap]

    json.dump(res, open(os.path.join(HERE, "respell_results.json"), "w"), indent=1, default=list)
    return res


if __name__ == "__main__":
    res = main()
    # compact console report
    def fmt(m):
        return " ".join("%s=%d/%d(%.5f)" % (k.split("_")[0], m[k][0], m[k][1], m[k][2])
                        for k in ["m1_same_char", "m2_same_ring", "m3_linked", "m4_B_in_K", "m5_same_cell",
                                  "extra_m3_linked_excluding_equal_cells"])
    print("DATA", json.dumps({k: v for k, v in res["data"].items()}))
    for sc in ("P", "M"):
        a = res["a"][sc]
        print("\n== scheme", sc, "identical", a["n_identical"], "%.5f" % a["share_identical"],
              "resp cell0", a["respelled_cell_zero_count"], a["respelled_cell_zero_words_first40"])
        print("identical words:", a["identical_words_first40"])
        print("(a) all   ", fmt(a["all"]), "zeroA", a["all"]["n_A_zero"], "zeroB", a["all"]["n_B_zero"])
        print("    rel   ", a["all"]["extra_relation_counts_either_direction"])
        print("(a) non-id", fmt(a["without_identical"]))
        print("    rel   ", a["without_identical"]["extra_relation_counts_either_direction"])
        b = res["b"][sc]
        print("(b) singletons", b["words_unpairable_singleton_stratum_all"], b["words_unpairable_singleton_stratum_without_identical"])
        for i, d in enumerate(b["draws_all"]):
            print("  ctl all  d%d" % (i + 1), fmt(d), "n", d["n_pairs"])
        for k, v in b["summary_all"].items():
            print("   mean", k, "%.5f [%.5f, %.5f]" % (v["mean"], v["min"], v["max"]))
        for i, d in enumerate(b["draws_without_identical"]):
            print("  ctl nonid d%d" % (i + 1), fmt(d), "n", d["n_pairs"])
        for k, v in b["summary_without_identical"].items():
            print("   mean", k, "%.5f [%.5f, %.5f]" % (v["mean"], v["min"], v["max"]))
        print("   ctl rel d1", b["draws_all"][0]["extra_relation_counts_either_direction"])
    c = res["c"]
    print("\n(c) entries", c["entries_HH_AY1"], "near", c["near_other_stress_not_in_family"])
    print("resp_P", c["resp_P"], "\nresp_M", c["resp_M"], "\nP_vs_M", c["P_vs_M"]["relations"])
    for label in ("family_any_pronunciation", "family_first_pronunciation"):
        f = c[label]
        print("\n--", label)
        for m in f["members"]:
            print("  ", m)
        print("  links", [(x["A"], x["B"], x["relations"]) for x in f["pairwise_link_detail"]])
        print("  vsP", [(x["A"], x["relations"]) for x in f["member_vs_P_detail"]], "vsM", [(x["A"], x["relations"]) for x in f["member_vs_M_detail"]])
        for t in ("spelled_vs_spelled_ordered_pairs", "spelled_vs_P", "spelled_vs_M"):
            print("  obs", t, fmt(f["metrics_" + t]))
        for t in ("spelled_vs_spelled", "spelled_vs_P", "spelled_vs_M"):
            ct = f["control_" + t]
            print("  ctl", t, "seed", ct["seed"], ct.get("pool_sizes", ""))
            for k in ["m1_same_char", "m2_same_ring", "m3_linked", "m4_B_in_K", "m5_same_cell"]:
                print("     ", k, "mean %.5f ge %.4f le %.4f" % (ct[k]["mean"], ct[k]["share_draws_ge_observed"], ct[k]["share_draws_le_observed"]), ct[k]["distribution"])
    for sc in ("P", "M"):
        bb = res["b"][sc]
        print("\nZ", sc)
        for tag in ("all", "without_identical"):
            for k, v in bb["z_" + tag].items():
                print("  ", tag, k, "obs %.5f ctl %.5f diff %+.5f se %.5f z %+.2f" % (v["observed"], v["control_mean"], v["diff"], v["binomial_se"], v["z"]))
            print("   relmean", tag, bb["mean_relation_counts_" + tag])
            print("   folded dist ctl", tag, bb["mean_folded_distance_" + tag], "obs", res["a"][sc][tag]["extra_folded_cell_distance"])
    for sc in ("P", "M"):
        d = res["d"][sc]
        print("\n(d)", sc, {k: v for k, v in d.items()})
    print("\nEXAMPLES random", json.dumps(res["examples_random_seed4000"]))
    print("EXAMPLES fixed", json.dumps(res["examples_fixed_silent_letter_list"]))
