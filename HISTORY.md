# 更新日誌

## v0.1.33

- feat(noagent): add autonomous LLM agent CLI with chat session recovery and persistence
- feat(noimg): implement WebP VP8/VP8L decode, progressive JPEG, and BMP palette/RLE/16-bit decode
- fix(noimg): wrap PNG IDAT in an RFC 1950 zlib datastream
- feat(nogit): add recursive ls-tree -r and migrate object/refs/config readers to ?str option types
- fix(nogit): use fs.dir-entries in remove-tree to prevent climbing .. and deleting parent trees
- feat(nouv): implement the full registry JSON API with environment markers and Python version detection
- feat(core): support large payloads in the HTTP client and JSON parser
- refactor(notools): migrate to the v0.3.17 std API - qualify os.arg/os.args, convert math.floor/cos/sin to value methods, and unwrap ?i64 in pr option handling
- feat(notools): align the awk interpreter with BSD awk and port pr multicolumn layout (vertcol/horzcol/mulfile)
- docs(docs): add the history changelog page to the docs-site sidebar
- build(deps): pin the nolang compiler to v0.3.18 across the build matrix and package manifests to fix Windows cross-compile
- fix(ci): correct the build-nolang action ref double-v typo (vv0.3.17) that failed every build job at setup
- build(release): improve the release script and mirror HISTORY.md into the docs-site history pages

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
- build(ci): bump nolang compiler to v0.3.18 and include HISTORY.md section in release body
- build(makefile): fix sync-skills writing to temp dir instead of project skills directory
