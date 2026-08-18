"""Build a unified stimulus file from SyntaxGym NP/Z + MV/RR and the external
Christianson-2001 / Alternates-2022 garden-path sets.

Output: data/processed/stimuli.jsonl, one line per (suite, item, condition).
Each line carries the surface string plus *word-level* indices for the
disambiguating region and the post-disambiguation recovery window, so that all
downstream comparisons are region-aligned and never tokenizer-aligned.
"""
import json, csv, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")
NO_SPACE_BEFORE = set(",.;:!?%)")

# 2x2 factor coding shared by both SyntaxGym suites:
#   ambiguity: 'ambig'   = the misleading local parse is available
#              'unambig' = it is not
#   cue:       'absent'  = no early disambiguating cue (comma / unreduced RC)
#              'present' = early cue blocks the garden path
SG_FACTORS = {
    "npz_ambig": {
        "ambig_nocomma":   ("ambig",   "absent"),
        "ambig_comma":     ("ambig",   "present"),
        "unambig_nocomma": ("unambig", "absent"),
        "unambig_comma":   ("unambig", "present"),
    },
    "mvrr": {
        "reduced_ambig":     ("ambig",   "absent"),
        "unreduced_ambig":   ("ambig",   "present"),
        "reduced_unambig":   ("unambig", "absent"),
        "unreduced_unambig": ("unambig", "present"),
    },
}
RECOVERY_WINDOW = 3


def join_regions(regions):
    """Concatenate SyntaxGym regions into a surface string.

    Returns (text, spans) where spans maps region_number -> (start, end) char
    offsets. Empty regions are dropped and contribute no span.
    """
    s = ""
    spans = {}
    for num, content in regions:
        c = " ".join(content.split())
        if not c:
            continue
        if s and c[0] not in NO_SPACE_BEFORE:
            s += " "
        spans[num] = (len(s), len(s) + len(c))
        s += c
    return s, spans


def word_spans(text):
    return [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]


def region_of_word(wspan, spans):
    """Region a word belongs to, keyed on its first character."""
    for num, (a, b) in spans.items():
        if a <= wspan[0] < b:
            return num
    return None


def build_syntaxgym(suite):
    d = json.load(open(os.path.join(RAW, suite + ".json")))
    out = []
    for item in d["items"]:
        for cond in item["conditions"]:
            name = cond["condition_name"]
            regions = [(r["region_number"], r["content"]) for r in cond["regions"]]
            text, spans = join_regions(regions)
            ws = word_spans(text)
            regs = [region_of_word(w, spans) for w in ws]
            crit = [i for i, r in enumerate(regs) if r == 5]
            assert crit, (suite, item["item_number"], name)
            post = list(range(crit[-1] + 1, min(crit[-1] + 1 + RECOVERY_WINDOW, len(ws))))
            amb, cue = SG_FACTORS[suite][name]
            out.append(dict(
                suite=suite, item=int(item["item_number"]), condition=name,
                ambiguity=amb, cue=cue, text=text,
                words=[text[a:b] for a, b in ws],
                word_char_spans=ws,
                crit_idx=crit, post_idx=post, n_post=len(post),
            ))
    return out


def build_external(name):
    """Christianson_2001 / Alternates_2022: OT/RAT are garden paths, DOT/DRAT
    are their comma-delimited controls. Pairing key is (Index, base label)."""
    rows = list(csv.DictReader(open(os.path.join(RAW, name + ".tsv")), delimiter="\t"))
    out = []
    for r in rows:
        lab = r["Label"]
        base = lab[1:] if lab.startswith("D") else lab
        cue = "present" if lab.startswith("D") else "absent"
        text = " ".join(r["Sentence"].split())
        ws = word_spans(text)
        words = [text[a:b] for a, b in ws]
        # The disambiguator is the matrix verb: the first word after the
        # subordinate-clause NP. In these stimuli every sentence has the form
        #   While <subj> <verb>[,] the <N> that was <adj> and <adj> <MATRIX V> ...
        # so we locate it as the word following the "that was/were A and B" RC.
        low = [w.lower().strip(".,") for w in words]
        try:
            k = low.index("and")
        except ValueError:
            raise AssertionError("no 'and' in: " + text)
        crit = [k + 2]  # 'and' + adjective + matrix verb
        assert crit[0] < len(words), text
        post = list(range(crit[-1] + 1, min(crit[-1] + 1 + RECOVERY_WINDOW, len(ws))))
        out.append(dict(
            suite=name, item=int(r["Index"]), condition=lab,
            ambiguity="ambig", cue=cue, pair_key=f"{base}-{r['Index']}",
            text=text, words=words, word_char_spans=ws,
            crit_idx=crit, post_idx=post, n_post=len(post),
        ))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    stim = []
    for s in ["npz_ambig", "mvrr"]:
        stim += build_syntaxgym(s)
    for s in ["Christianson_2001", "Alternates_2022"]:
        stim += build_external(s)
    path = os.path.join(OUT, "stimuli.jsonl")
    with open(path, "w") as f:
        for s in stim:
            f.write(json.dumps(s) + "\n")
    print("wrote", path, len(stim), "stimuli")
    for suite in ["npz_ambig", "mvrr", "Christianson_2001", "Alternates_2022"]:
        sub = [s for s in stim if s["suite"] == suite]
        items = len({s["item"] for s in sub})
        npost = {}
        for s in sub:
            npost[s["n_post"]] = npost.get(s["n_post"], 0) + 1
        print(f"  {suite}: {len(sub)} stimuli / {items} items / n_post dist {dict(sorted(npost.items()))}")


if __name__ == "__main__":
    main()
