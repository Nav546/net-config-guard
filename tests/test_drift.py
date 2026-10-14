import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))
from drift import compare, report


def mk(tmp):
    g, c = tmp / "g", tmp / "c"; g.mkdir(); c.mkdir(); return g, c


def test_no_drift_ignores_noise(tmp_path):
    g, c = mk(tmp_path)
    (g / "r1.cfg").write_text("set / interface e1 admin-state enable\n# last-change 1\n")
    (c / "r1.cfg").write_text("set / interface e1 admin-state enable\n# last-change 2\n\n")
    assert not report(compare(g, c))[1]


def test_detects_change(tmp_path):
    g, c = mk(tmp_path)
    (g / "r1.cfg").write_text("set / interface e1 admin-state enable\n")
    (c / "r1.cfg").write_text("set / interface e1 admin-state disable\n")
    text, drift = report(compare(g, c))
    assert drift and "admin-state disable" in text


def test_missing_current(tmp_path):
    g, c = mk(tmp_path)
    (g / "r1.cfg").write_text("x\n")
    assert report(compare(g, c))[1]
