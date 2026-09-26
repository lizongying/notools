# 更新日誌

## v0.1.32

- feat(nonpm): add Nolang Node.js package manager with semver comparison and comprehensive tests
- feat(nouv): add Nolang Python package manager with zip/wheel extraction and virtual environment management
- feat(tools): add cross-platform support and refactor stdbuf implementation
- feat(release): add release-failure detection and force re-push workflow to nolang-release skill
- feat(skills): sync nolang-builtin, nolang-docs-i18n, nolang-path-resolution and nolang-vet skills from upstream
- fix(nogit): resolve config-get crash and index binary read errors
- fix(noimg): unify data types and fix numeric precision in image calculations
- fix(ci): check out repo in release job so history.sh can build the release body
- docs(xargs): update comment describing the vec.push codegen fix
- build(ci): bump nolang compiler to 0.3.8 and include HISTORY.md section in release body
- build(makefile): fix sync-skills writing to temp dir instead of project skills directory
