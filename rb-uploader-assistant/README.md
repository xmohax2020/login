# rb-uploader-assistant (MVP Skeleton)

A starter implementation for a semi-automated Redbubble preparation workflow.

## Quick start

```bash
cd rb-uploader-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/sync_db.py
python scripts/prepare.py --input input_designs --output exports --metadata data/designs.csv --niche general
python scripts/validate.py --metadata data/designs.csv
uvicorn app.main:app --reload --port 8080
```

## What is included

- Image resize/export pipeline from `configs/sizes.yaml`
- SHA256 dedupe utility
- Metadata generation + validation
- SQLite storage and basic REST API
- Minimal HTML dashboard for review/status updates

## Safety note

This tool is intentionally built for **prep + assist** only. Final publishing remains manual.
