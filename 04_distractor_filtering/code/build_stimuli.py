"""Distractor-filtering stimuli.

`semantic` and `unrelated` share the distractor frame verbatim (`NAME lives in X.`)
and differ only in whether X is a country (which affords a competing answer through
the queried relation) or a dwelling (which does not). Candidate sets are identical
across all conditions, and every item exists at both distractor positions.
"""
import json, glob, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, OUT = os.path.join(ROOT, "data", "raw"), os.path.join(ROOT, "data", "processed")
SEED = 20260819
N_WRONG = 3          # never-mentioned candidates, alongside correct + decoy answer

FRAMES = {
    "country_capital_city":  "The capital of {who}'s country is",
    "country_currency":      "The official currency of {who}'s country is the",
    "country_language":      "People in {who}'s country speak",
    "country_largest_city":  "The largest city in {who}'s country is",
}
NAMES = """Sebastian Rowan Miriam Douglas Priya Halvard Anneke Tomasz Ingrid Rafael
Naledi Yusuf Camille Bjorn Leila Mateo Sinead Kwame Elena Viktor""".split()
DWELLINGS = """cottage bungalow apartment cabin farmhouse loft townhouse chalet
duplex penthouse""".split()


def main():
    rng = random.Random(SEED)
    stim = []
    for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        rel = os.path.basename(path)[:-5]
        d = json.load(open(path))
        pairs = [(s["subject"], s["object"]) for s in d["samples"]]
        objs = sorted({o for _, o in pairs})
        if len(pairs) < 4:
            continue
        for i, (country, answer) in enumerate(pairs):
            for rep in range(4):
                others = [(c, a) for c, a in pairs if c != country and a != answer]
                if not others:
                    continue
                dec_country, dec_answer = others[rng.randrange(len(others))]
                who, other_who = rng.sample(NAMES, 2)
                wrong = [o for o in objs if o not in (answer, dec_answer)]
                rng.shuffle(wrong)
                cands = [answer, dec_answer] + wrong[:N_WRONG]

                rel_s = f"{who} lives in {country}."
                dis = {
                    "semantic":  f"{other_who} lives in {dec_country}.",
                    "unrelated": f"{other_who} lives in a {rng.choice(DWELLINGS)}.",
                    "direct":    f"{other_who} visited {dec_answer}.",
                }
                query = FRAMES[rel].format(who=who)
                item = f"{rel}::{i}::{rep}"
                stim.append(dict(relation=rel, item=item, condition="base", position="na",
                                 prompt=f"{rel_s} {query}", correct=answer,
                                 decoy=dec_answer, candidates=cands))
                for cond, sent in dis.items():
                    for pos in ("before", "after"):
                        ctx = f"{sent} {rel_s}" if pos == "before" else f"{rel_s} {sent}"
                        stim.append(dict(relation=rel, item=item, condition=cond,
                                         position=pos, prompt=f"{ctx} {query}",
                                         correct=answer, decoy=dec_answer,
                                         candidates=cands))
    # decoy-association probe: does the model know Indonesia -> Jakarta at all?
    seen = set()
    for s in [x for x in stim if x["condition"] == "base"]:
        pass
    for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        rel = os.path.basename(path)[:-5]
        d = json.load(open(path))
        tmpl = d["prompt_templates"][0]
        for i, sm in enumerate(d["samples"]):
            key = (rel, sm["subject"])
            if key in seen:
                continue
            seen.add(key)
            stim.append(dict(relation=rel, item=f"decoy::{rel}::{i}", condition="decoy_probe",
                             position="na", prompt=tmpl.format(sm["subject"]),
                             correct=sm["object"], decoy=sm["object"],
                             candidates=[sm["object"]]))
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "stimuli.jsonl")
    with open(p, "w") as f:
        for s in stim:
            f.write(json.dumps(s) + "\n")
    n_items = len({s["item"] for s in stim if s["condition"] != "decoy_probe"})
    print(f"wrote {p}: {len(stim)} stimuli, {n_items} items, "
          f"{len([s for s in stim if s['condition']=='decoy_probe'])} decoy probes")
    for s in stim[:6]:
        print(f"  [{s['condition']:9s} {s['position']:6s}] {s['prompt']}")
        print(f"      correct={s['correct']!r} decoy={s['decoy']!r} cands={s['candidates']}")


if __name__ == "__main__":
    main()
