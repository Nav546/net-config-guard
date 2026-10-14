"""Pull running configs from every device in devices.yml and save them to disk."""
import argparse, datetime as dt, pathlib, sys
import yaml
from netmiko import ConnectHandler


def load_inventory(path):
    data = yaml.safe_load(open(path))
    d = data["defaults"]
    for dev in data["devices"]:
        yield {**d, **dev}


def fetch(dev):
    conn = ConnectHandler(device_type=dev["device_type"], host=dev["host"],
                          username=dev["username"], password=dev["password"], timeout=30)
    try:
        return conn.send_command(dev["show_command"])
    finally:
        conn.disconnect()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="src/devices.yml")
    ap.add_argument("--out", default="backups/latest")
    ap.add_argument("--archive", action="store_true")
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    failed = 0
    for dev in load_inventory(a.inventory):
        try:
            cfg = fetch(dev)
        except Exception as e:
            print(f"[FAIL] {dev['host']}: {e}", file=sys.stderr); failed += 1; continue
        (out / f"{dev['host']}.cfg").write_text(cfg + "\n")
        if a.archive:
            h = pathlib.Path("backups/history") / stamp; h.mkdir(parents=True, exist_ok=True)
            (h / f"{dev['host']}.cfg").write_text(cfg + "\n")
        print(f"[ OK ] {dev['host']} ({len(cfg.splitlines())} lines)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
