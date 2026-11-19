# Experiments

Store experiment specifications, immutable configs, run manifests, analysis code, and reports here.

Suggested layout:

```text
experiments/
  pilot_factorial/
    protocol.yaml
    configs/
    manifests/
    raw/              # normally external artifact storage; never rewrite in place
    derived/
    reports/
```

Do not commit secrets, private user data, or large raw provider payloads. If raw data is stored externally, commit the exact artifact identifier, checksum, schema, and access instructions.
