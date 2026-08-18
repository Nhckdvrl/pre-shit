"""Build entity state-update stimuli from the PI-LLM category/value inventory.

Each trial fixes one queried key and varies how many states it has passed
through, against a length- and mention-matched control in which the *other*
sentences bind different keys and therefore never overwrite the query.

    update_1   The bird is emu.                                   -> emu
    update_2   The bird is emu. The bird is now kea.              -> kea, obsolete {emu}
    update_3   ... The bird is now ani.                           -> ani, obsolete {emu, kea}
    control_2  The material is wood. The bird is now kea.         -> kea, unbound {wood}
    control_3  The material is wood. The dessert is cake.
               The bird is now ani.                               -> ani, unbound {wood, cake}

Candidates are the current value, every obsolete/unbound value, and an equal
number of values from the same category that were never mentioned. Errors can
therefore be classified as interference (an obsolete binding) or as a plain miss.
"""
import json, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "pi_dict.json")
OUT = os.path.join(ROOT, "data", "processed")
TRIALS_PER_CATEGORY = 20
SEED = 20260819
MAX_WORDS = 2          # keep values short so scoring is not dominated by length


def main():
    rng = random.Random(SEED)
    inv = json.load(open(RAW))
    cats = sorted(inv)
    pool = {c: [v for v in inv[c] if len(v.split()) <= MAX_WORDS] for c in cats}
    pool = {c: v for c, v in pool.items() if len(v) >= 12}
    cats = sorted(pool)
    os.makedirs(OUT, exist_ok=True)

    stim = []
    for cat in cats:
        others = [c for c in cats if c != cat]
        for t in range(TRIALS_PER_CATEGORY):
            vals = rng.sample(pool[cat], 6)
            states, unmentioned = vals[:3], vals[3:]
            oc = rng.sample(others, 2)
            ov = [rng.choice(pool[c]) for c in oc]

            def query(c):
                return f"The {c} is currently"

            def upd(n):
                sents = [f"The {cat} is {states[0]}."]
                sents += [f"The {cat} is now {states[i]}." for i in range(1, n)]
                return " ".join(sents)

            def ctl(n):
                sents = [f"The {oc[i]} is {ov[i]}." for i in range(n - 1)]
                sents += [f"The {cat} is {states[n-1]}."]
                return " ".join(sents)

            for cond, n in [("update_1", 1), ("update_2", 2), ("update_3", 3),
                            ("control_2", 2), ("control_3", 3)]:
                if cond.startswith("update"):
                    ctx, current = upd(n), states[n - 1]
                    interferers = states[:n - 1]
                else:
                    ctx, current = ctl(n), states[n - 1]
                    interferers = ov[:n - 1]
                stim.append(dict(
                    category=cat, trial=f"{cat}::{t}", condition=cond, n_states=n,
                    prompt=f"{ctx} {query(cat)}",
                    current=current, interferers=interferers,
                    unmentioned=unmentioned[:max(1, len(interferers))],
                ))

    path = os.path.join(OUT, "stimuli.jsonl")
    with open(path, "w") as f:
        for s in stim:
            f.write(json.dumps(s) + "\n")
    print(f"wrote {path}: {len(stim)} stimuli, "
          f"{len({s['trial'] for s in stim})} trials, {len(cats)} categories")
    for s in stim[:5]:
        print(f"\n  [{s['condition']}] {s['prompt']}")
        print(f"     current={s['current']!r} interferers={s['interferers']} "
              f"unmentioned={s['unmentioned']}")


if __name__ == "__main__":
    main()
