# net-config-guard

Network configuration backup and drift detection for a virtual lab.

A small 3-router network runs in Containerlab (Nokia SR Linux). A Python script logs into every
router over SSH with Netmiko, saves the running config, and compares it with a known-good
"golden" baseline. If anyone changes a router by hand, the tool shows exactly what changed.

## How it works

```
Containerlab lab (r1, r2, r3)
        |  SSH (Netmiko)
        v
 src/backup.py  -->  golden/           (known-good baseline)
                -->  backups/latest/   (current state)
                          |
                          v
                 src/drift.py  -->  drift-report.md + exit code (0 clean, 1 drift)
```

## Quick start

Requires Linux with Docker and [Containerlab](https://containerlab.dev/install/).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q

sudo containerlab deploy -t topology/lab.clab.yml   # wait about a minute for the routers to boot

pytho

The script exits with code 1 when drift is found, so it can fail a CI job.

Clean up the lab with `sudo containerlab destroy -t topology/lab.clab.yml --cleanup`.

## Project layout

| Path | Purpose |
|---|---|
| `topology/lab.clab.yml` | 3-node SR Linux ring topology |
| `src/devices.yml` | Device inventory and lab credentials |
| `src/backup.py` | Pulls configs over SSH and saves them |
| `src/drift.py` | Compares configs, writes the report, sets the exit code |
| `tests/` | Unit tests for the drift logic |

## Roadmap

- [ ] GitHub Actions workflow to run the check on a schedule
- [ ] Store config backups in Azure Blob Storage (Bicep for the storage account)
- [ ] Optional auto-remediation: push the golden config back when drift is detected
- [ ] CCNA-style lab: configure VLANs, OSPF and ACLs by script, then audit them

## Notes

Credentials in `src/devices.yml` are the public defaults for the lab image and are not real secrets.
