"""Build the contextual-entrainment stimuli from the LRE factual relations.

Every item yields five prompts (none / related / irrelevant / random /
counterfactual) and two candidates (gold, distractor). Nothing is hand-written:
subjects, objects and templates all come from LRE.
"""
import json, glob, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")
MAX_PER_RELATION = 40
SEED = 20260819

# Semantically inert single words for the `random` condition. Deliberately
# concrete, high-frequency and unrelated to any LRE relation domain.
RANDOM_WORDS = """
calculator envelope stapler blanket kettle ladder mattress napkin pebble saucer
thimble trolley umbrella wardrobe bucket candle drawer funnel hammer jigsaw
kayak lantern mirror nozzle ottoman pillow quilt ribbon shovel teapot
vacuum whistle anchor basket crayon doorknob easel feather goggles helmet
inkwell jacket kneepad lampshade magnet notebook oven paddle quiver rope
sandal tripod utensil vase wagon yardstick zipper apron bookmark canoe
""".split()


def load_relations():
    rels = []
    for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        d = json.load(open(path))
        samples = [(s["subject"], s["object"]) for s in d["samples"]
                   if s["subject"] and s["object"]]
        # LRE lists several templates; the first is the canonical one
        rels.append(dict(name=d["name"], template=d["prompt_templates"][0],
                         samples=samples))
    return rels


def main():
    rng = random.Random(SEED)
    os.makedirs(OUT, exist_ok=True)
    stim = []
    for rel in load_relations():
        tmpl, samples = rel["template"], rel["samples"]
        objects = sorted({o for _, o in samples})
        if len(objects) < 2 or len(samples) < 2:
            continue
        chosen = samples if len(samples) <= MAX_PER_RELATION else rng.sample(samples, MAX_PER_RELATION)
        for idx, (subj, gold) in enumerate(chosen):
            # counterfactual: a different object of the same relation, preferring
            # one of similar surface length so that K is not a length contrast
            alts = [o for o in objects if o != gold]
            if not alts:
                continue
            alts.sort(key=lambda o: (abs(len(o) - len(gold)), o))
            cf = alts[rng.randrange(0, min(5, len(alts)))]
            # irrelevant: a true fact about a different subject of the relation
            others = [(s2, o2) for s2, o2 in samples if s2 != subj and o2 != gold]
            if not others:
                continue
            s2, o2 = others[rng.randrange(len(others))]
            rand_w = RANDOM_WORDS[rng.randrange(len(RANDOM_WORDS))]
            # a second random noun that never enters any context: the control that
            # separates "this token was copied" from "random nouns got likelier"
            ctrl_w = rand_w
            while ctrl_w == rand_w:
                ctrl_w = RANDOM_WORDS[rng.randrange(len(RANDOM_WORDS))]

            query = tmpl.format(subj)
            stim.append(dict(
                relation=rel["name"], item=f"{rel['name']}::{idx}",
                subject=subj, gold=gold,
                query=query,
                contexts={
                    "none": "",
                    "related": f"{tmpl.format(subj)} {gold}.",
                    "irrelevant": f"{tmpl.format(s2)} {o2}.",
                    "random": f"{rand_w.capitalize()}.",
                    "counterfactual": f"{tmpl.format(subj)} {cf}.",
                },
                distractors={
                    "related": gold, "irrelevant": o2,
                    # capitalised so the candidate is the *same token* the
                    # context introduced -- otherwise "Crayon" vs " crayon" would
                    # measure something other than copying
                    "random": rand_w.capitalize(), "counterfactual": cf,
                },
                control=ctrl_w.capitalize(),
            ))
    path = os.path.join(OUT, "stimuli.jsonl")
    with open(path, "w") as f:
        for s in stim:
            f.write(json.dumps(s) + "\n")
    print(f"wrote {path}: {len(stim)} items over "
          f"{len({s['relation'] for s in stim})} relations")
    ex = stim[0]
    print("\nexample:")
    for k, v in ex["contexts"].items():
        d = ex["distractors"].get(k, "-")
        print(f"  {k:15s} {(v + ' ' + ex['query']).strip()!r}  gold={ex['gold']!r} distractor={d!r}")


if __name__ == "__main__":
    main()
