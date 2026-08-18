"""Entity-matched control: the decisive test of overwrite-specificity.

The category control in `build_stimuli.py` changes several things at once, so a
rising PI cost could partly reflect the model learning category type constraints.
Here everything is held fixed except *who the earlier statements were about*:

  update   Alice's bird is emu.  Alice's bird is now kea.  Alice's bird is now ani.
  control  Bob's bird is emu.    Carol's bird is now kea.  Alice's bird is now ani.
                                          query:  Alice's bird is currently

Identical in both: sentence count, surface frames (`is` then `is now`), the value
category, the candidate set, and the final sentence. The only difference is
whether the earlier bindings were of the *queried entity* or of other entities.

One asymmetry cannot be removed: the queried key appears three times in `update`
and once in `control`. That works *against* the hypothesis — repeating the key
makes the query more predictable — so any positive PI cost here is conservative.
"""
import json, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "pi_dict.json")
OUT = os.path.join(ROOT, "data", "processed")
TRIALS_PER_CATEGORY = 20
SEED = 20260819
MAX_WORDS = 2

NAMES = """Alice Bob Carol David Emma Frank Grace Henry Irene Jack Karen Liam
Mary Nathan Olivia Peter Quinn Rachel Samuel Tina Victor Wendy""".split()


def main():
    rng = random.Random(SEED)
    inv = json.load(open(RAW))
    pool = {c: [v for v in inv[c] if len(v.split()) <= MAX_WORDS] for c in sorted(inv)}
    pool = {c: v for c, v in pool.items() if len(v) >= 12}
    cats = sorted(pool)
    os.makedirs(OUT, exist_ok=True)

    stim = []
    for cat in cats:
        for t in range(TRIALS_PER_CATEGORY):
            vals = rng.sample(pool[cat], 6)
            states, unmentioned = vals[:3], vals[3:]
            who = rng.sample(NAMES, 3)
            owner, other1, other2 = who[0], who[1], who[2]

            def sent(person, val, first):
                return f"{person}'s {cat} is {val}." if first else f"{person}'s {cat} is now {val}."

            query = f"{owner}'s {cat} is currently"
            for n in (2, 3):
                # same entity throughout -> genuine overwrites
                upd = [sent(owner, states[0], True)]
                upd += [sent(owner, states[i], False) for i in range(1, n)]
                # (a) every earlier value bound to a *distinct* other entity, so
                #     the context contains no overwrite at all
                distinct = [other1, other2][:max(1, n - 1)]
                ctl_d = [sent(distinct[0], states[0], True)]
                ctl_d += [sent(distinct[min(i, len(distinct) - 1)], states[i], False)
                          for i in range(1, n - 1)]
                ctl_d += [sent(owner, states[n - 1], False)]
                # (b) the earlier values overwrite *one other* entity: same number of
                #     overwrites as `update`, just not of the queried entity
                ctl_o = [sent(other1, states[0], True)]
                ctl_o += [sent(other1, states[i], False) for i in range(1, n - 1)]
                ctl_o += [sent(owner, states[n - 1], False)]

                for cond, sents in [(f"update_e{n}", upd),
                                    (f"control_distinct_e{n}", ctl_d),
                                    (f"control_other_e{n}", ctl_o)]:
                    stim.append(dict(
                        category=cat, trial=f"{cat}::{t}", condition=cond, n_states=n,
                        prompt=" ".join(sents) + " " + query,
                        current=states[n - 1], interferers=states[:n - 1],
                        unmentioned=unmentioned[:max(1, n - 1)],
                    ))

    path = os.path.join(OUT, "stimuli_entity.jsonl")
    with open(path, "w") as f:
        for s in stim:
            f.write(json.dumps(s) + "\n")
    print(f"wrote {path}: {len(stim)} stimuli over {len(cats)} categories")
    for s in stim[:4]:
        print(f"\n  [{s['condition']}] {s['prompt']}")
        print(f"     current={s['current']!r} interferers={s['interferers']} "
              f"unmentioned={s['unmentioned']}")


if __name__ == "__main__":
    main()
