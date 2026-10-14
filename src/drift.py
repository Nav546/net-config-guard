"""Compare current configs with golden baselines. Exit 0 = clean, 1 = drift."""
import argparse, difflib, pathlib, re, sys

NOISE = [re.compile(p) for p in (r"^\s*$", r"last-?(configuration|change)", r"^\s*#", r"timestamp")]


def normalise(text):
    return [l.rstrip() for l in text.splitlines() if not any(p.search(l) for p in NOISE)]


def compare(golden_dir, current_dir):
    results = {}
    for g in sorted(pathlib.Path(golden_dir).glob("*.cfg")):
        c = pathlib.Path(current_dir) / g.name
        if not c.exists():
            results[g.stem] = ["<< current config missing >>"]; continue
        results[g.stem] = list(difflib.unified_diff(normalise(g.read_text()), normalise(c.read_text()),
                                                    "golden", "current", lineterm="", n=1))
    return results


def report(results):
    drifted = {h: d for h, d in results.items() if d}
    lines = ["# Config drift report", "",
             f"**{len(results) - len(drifted)} of {len(results)} devices match baseline.**", ""]
    for h, d in drifted.items():
        lines += [f"## {h}", "```diff", *d, "```", ""]
    return "\n".join(lines), bool(drifted)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default="golden")
    ap.add_argument("--current", default="backups/latest")
    ap.add_argument("--report", default="drift-report.md")
    a = ap.parse_args()
    results = compare(a.golden, a.current)
    if not results:
        print("No golden configs found. Run: python src/backup.py --out golden", file=sys.stderr); sys.exit(1)
    text, drift = report(results)
    pathlib.Path(a.report).write_text(text)
    print(text)
    sys.exit(1 if drift else 0)


if __name__ == "__main__":
    main()
