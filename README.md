# ResearchOS TECT — Acoustic Communication and Sensing

Independent research workspace aligned with DARPA STO’s interest in acoustic communication and sensing, supporting novel concept development, reproducible modeling, experiment design, prototype evaluation, and evidence-linked assessment of technical feasibility, research risks, and differentiation from existing approaches.

## Working implementation

- Seeded ideal coherent BPSK/AWGN link simulation across declared distances, with geometric spreading and declared absorption.
- Approximate theoretical bit-error probability, finite-sample bit errors, propagation delay, and frame duration.
- Synthetic known-pulse single-echo correlation and round-trip range calculation with explicit ground truth.
- Strict experiment records, protocol and differentiation notes, declared measurements with uncertainty, and evidence references.
- Portable CLI bundles with captured evidence, SHA-256 checks, JSON/CSV/Markdown reports and numerical/report reproduction verification.
- A responsive browser app with experiment forms, link/error and correlation charts, local records, import, evidence hashing and exports.

The models are simplified research fixtures, not a novel acoustic method or validated prototype. No acoustic hardware, microphone, speaker, live sensing, operational deployment or field performance is implemented. No DARPA affiliation, award, endorsement, eligibility or submission is claimed. TECT remains the project identifier without an assumed expansion.

## Quick start

Python 3.10 or newer; no third-party runtime dependencies:

```bash
python -m researchos_acoustics validate examples/synthetic-acoustic.json
python -m researchos_acoustics run examples/synthetic-acoustic.json --output runs/demo
python -m researchos_acoustics verify runs/demo
python -m researchos_acoustics report runs/demo
python -m unittest discover -s tests -v
```

Optional installation:

```bash
python -m pip install .
researchos-acoustics --help
```

The synthetic example uses distances of 1, 2, 4 and 8 m. At 8 m the model produces 337 bit errors in 4,096 bits with seed 42. The injected echo delay is 96 samples and the recovered peak is 96 samples, corresponding to 0.343 m under the assumed 343 m/s sound speed and 48 kHz sampling. These are known-answer software fixtures, not measurements. Zero errors in a finite sample do not imply zero bit-error probability, and a correlation peak is not a validated detection.

## Browser app

Serve the `web/` directory with `python -m http.server 8000 --directory web`, then open `http://localhost:8000`. Use localhost or HTTPS for modules, workers and Web Crypto. Run web tests with `node web/tests/model.test.mjs`.

Simulation runs in a background worker. Records stay in this browser and origin; export regularly. No GitHub, CLI or cross-device synchronization is configured. Record JSON exports work with the CLI; browser result/report exports are summaries, not full CLI evidence bundles. Files used in the evidence checker are hashed locally, never uploaded or retained. Original evidence files must be preserved separately. Imported/reloaded records do not re-verify them.

The form creates synthetic/simulation records. Experimental records can be imported with measurements and evidence declarations; the model still produces separate synthetic results. Reusing an experimental record as a new parameter template changes its basis to simulation and omits original measurements/evidence, leaving the original saved record intact.

## Research workflow

1. Copy the example; assign an ID, owner, hypothesis, protocol reference and honest input basis.
2. Define the channel and ranging assumptions with units and versioned references. Check [model limits](docs/MODEL.md).
3. State the proposed differentiation honestly. Review existing literature, programs and solicitations before making novelty or nonduplication claims.
4. Add declared nonnegative measurements with method, unit, uncertainty and evidence IDs where available. Models do not fit or validate these measurements.
5. Put evidence below the record directory. Use `researchos-acoustics hash <file>` and declare its relative path, digest, description and unique ID.
6. Validate, run into a new output directory, verify, then review results and limitations. Existing output directories are rejected.

Source paths must remain inside the record directory, including after symlink resolution. Evidence bytes are captured in each bundle. Matching hashes do not establish authenticity, calibration or scientific validity. Local bundles are ignored by Git; keep unpublished partner data and credentials out of this public repository.

## Bundle contents

| File | Purpose |
| --- | --- |
| `record.json` | Exact original input bytes |
| `results.json` | Link sweep, symbol preview, full echo correlation, declared measurements and limitations |
| `link.csv` | Distance, loss, Eb/N0, delays and bit-error results |
| `report.md` | Human-readable model summary and differentiation notes |
| `evidence/0000.bin`, … | Captured original evidence bytes |
| `manifest.json` | Artifact digests, evidence mapping and Python version |

The verifier checks artifact hashes, evidence-to-record consistency, and recomputes results/report/CSV. Same inputs and runtime yield identical bundles. This is not a signed or tamper-proof audit service.

## Documentation and checks

- [Model equations and limitations](docs/MODEL.md)
- [Record contract](docs/RECORDS.md)
- [Research plan](docs/RESEARCH_PLAN.md)
- [Primary source context](docs/SOURCES.md)
- [Contributing](CONTRIBUTING.md)

CI checks JavaScript, web tests, Python tests, complete web/Python numerical parity, installed CLI execution and synthetic artifact upload across Python 3.10–3.13. The existing [license](LICENSE) is preserved.

Private hosted app: https://researchos-tect-acoustics.troturn31.chatgpt.site
