# 更新日誌

## v0.1.32

- feat(nonpm): add Nolang Node.js package manager with semver comparison and comprehensive tests
- feat(nouv): add Nolang Python package manager with zip/wheel extraction and virtual environment management
- feat(release): add release-failure detection and force re-push workflow to nolang-release skill
- feat(skills): sync nolang-builtin, nolang-docs-i18n, nolang-path-resolution and nolang-vet skills from upstream
- fix(nogit): resolve config-get crash and index binary read errors
- fix(noimg): unify data types and fix numeric precision in image calculations
- build(ci): bump nolang compiler to 0.3.5 and include HISTORY.md section in release body
- build(makefile): fix sync-skills writing to temp dir instead of project skills directory
- chore(all): format sources and restore required overflow annotations
- docs: add READMEs and usage documentation for nonpm and nouv
