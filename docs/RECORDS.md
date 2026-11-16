# Experiment record v1

The executable contract is `researchos_acoustics/records.py`. Duplicate JSON keys, NaN and Infinity are rejected. Booleans cannot replace numeric fields. Unknown metadata is retained.

| Field | Required content |
| --- | --- |
| schema_version | Integer 1 |
| id | 1–80 lowercase letters/digits/underscores/hyphens; starts alphanumeric |
| title, owner, hypothesis | Nonempty strings |
| protocol_reference | Nonempty versioned protocol/model reference |
| differentiation | Nonempty honest statement of novelty/overlap status |
| data_kind | synthetic, simulation, or experimental; describes inputs |
| seed | Integer 0 through 2³²−1 |
| link | Parameters below |
| ranging | Parameters below |
| measurements | Array, possibly empty for nonexperimental inputs |
| evidence | Array of declarations |

`link` requires positive `reference_distance_m`, `sound_speed_m_s`, `bit_rate_bps`; reference Eb/N0 `reference_ebn0_db` in [−60,60]; nonnegative `absorption_db_km`; integer `bits`; a nonempty `distances_m` array; and nonempty `assumption_reference`. See model bounds for total work and valid distances/received Eb/N0.

`ranging` requires integer `sample_rate_hz`, `pulse_samples`, `max_delay_samples`, `injected_delay_samples`, nonnegative `echo_gain` and `noise_std`, and nonempty `assumption_reference`. The sample delay is a synthetic ground-truth parameter, not a measurement inferred from data ingestion.

Each measurement has nonempty `metric`, `unit`, `method`; finite nonnegative `value` and `uncertainty`; and `evidence_ids` referencing declared evidence. Uncertainty interpretation, confidence/coverage, calibration and sampling should be documented in method/metadata. Negative-valued measurement quantities are not supported by this version. Experimental records require at least one measurement and evidence file, with evidence references on every measurement. This is traceability enforcement, not acquisition validation.

Each evidence declaration has unique `id`, unique relative `path`, lowercase 64-character `sha256`, and nonempty `description`. Paths cannot be absolute, drive paths, traversal or symlinks outside the record directory. Run `researchos-acoustics hash <file>` for a digest. The runner verifies and captures the original bytes, using generated bundle filenames mapped to original evidence IDs in the manifest.

The CLI refuses to overwrite run directories. Bundle verification checks hashes and recomputes numerical results, report and link CSV. Original files may be relocated after capture; the bundle retains their bytes. The browser exports record-compatible JSON and summary results, not a full CLI bundle.
