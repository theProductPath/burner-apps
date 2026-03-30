# Healthcare Data Review — Example Burner App

A working Burner App built from the Healthcare sample dataset. Use this to see what a generated Burner App looks like and to test the generator against a real dataset.

## Files

- `Healthcare_Sample_Data.xlsx` — sample dataset (patients, providers, claims, facilities)
- `generator.py` — configured generator for this dataset
- `healthcare_review.html` — pre-generated Burner App (current: SMJ design system — rebuild for tPP pending)
- `run-demo.sh` — regenerate the HTML from the Excel data
- `DEMO_SCRIPT.md` — walkthrough script for demos

## Regenerate

```bash
cd examples/healthcare
python3 generator.py Healthcare_Sample_Data.xlsx healthcare_review.html
```

## Status

Pre-generated HTML uses SMJ design system. Pending rebuild with tPP design system (Codey task).
