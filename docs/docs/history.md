---
sidebar_position: 2
---

# 更新日誌

本頁面收錄 Nolang 各版本的發布紀錄，與倉庫根目錄的 `HISTORY.md` 保持一致。


## v0.1.34

- feat(std): promote exit from the os module to a global builtin
- refactor(tools): run subcommands as top-level scripts instead of wrapping them in main
- refactor(notools): migrate command sources to D1 option arithmetic with explicit result unwrapping
- fix(noimg): replace removed number width-cast functions with f64/i64 to-i64/to-f64 methods
- fix(nojq): rename a colliding variable in main and move bi-code into the parser module for codegen
- fix(nonpm): bind indexed vec reads to plain locals so fs.is-dir and is-file marshal correctly
- refactor: remove redundant overflow annotations and explicit type annotations
- docs(design): mark the unified option-migration document as review-complete
- refactor(release): drop the dirty-tree blocker and use the history section as the commit message

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
- build(deps): pin the nolang compiler to v0.4.9 across the build matrix and package manifests to fix Windows cross-compile
- fix(ci): correct the build-nolang action ref double-v typo (vv0.3.17) that failed every build job at setup
- build(release): improve the release script and mirror HISTORY.md into the docs-site history pages
