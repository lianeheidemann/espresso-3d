# Version and technology references

- When code changes add, upgrade, replace, or remove a language runtime, framework, library, engine, external tool, or hardware/software requirement, update the relevant dependency/configuration files and user documentation in the same change.
- Keep pyproject.toml, requirements.txt, lockfiles, CI configuration, README, setup guides, and examples consistent where they describe the affected technology.
- Distinguish supported version ranges from versions observed in a specific environment. Record observed versions with the date and mark anything not installed or validated as pending; never infer exact versions or compatibility.
- When implementation behavior or commands change, update the related documentation and examples so they match the code.

## Compatibility and engines

- Preserve the Python version range declared in pyproject.toml (currently Python 3.10 or newer). Avoid syntax, APIs, or dependency versions that break that range; if the supported range changes, update configuration and documentation together.
- Add or change generation engines through the `Engine` interface in `src/espresso3d/engines/` and register them in `ENGINES`. Do not bypass the registry used by the UI and pipeline.
- Keep engine-specific packages and model weights optional. An unavailable or unconfigured engine must not prevent the base interface from starting; report its availability accurately and document its setup and requirements.