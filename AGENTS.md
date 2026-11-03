# Version and technology references

- When code changes add, upgrade, replace, or remove a language runtime, framework, library, engine, external tool, or hardware/software requirement, update the relevant dependency/configuration files and user documentation in the same change.
- Keep pyproject.toml, requirements.txt, lockfiles, CI configuration, README, setup guides, and examples consistent where they describe the affected technology.
- Distinguish supported version ranges from versions observed in a specific environment. Record observed versions with the date and mark anything not installed or validated as pending; never infer exact versions or compatibility.
- When implementation behavior or commands change, update the related documentation and examples so they match the code.
