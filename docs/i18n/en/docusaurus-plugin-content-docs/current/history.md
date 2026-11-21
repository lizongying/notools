---
sidebar_position: 2
---

# Changelog

This page collects Nolang release records for each version, kept consistent with the root `HISTORY.md`.


## v0.1.36

- fix(notools): reject zip-slip archive paths and cap single-entry size in unzip and tar
- fix(notools): replace str option index writes with concatenation in od, xxd, blake2bx and mcookie
- fix(notools): refuse recursive delete on symlinks and forbidden roots in rm, and propagate read/write failures in cp, install and yes
- fix(nogit): validate ref names, add ref resolution depth limit, and reject path traversal in packed-refs and index extraction
- fix(nogit): fix hex output corruption from dynamic str index writes across util, oid, pack and index
- fix(nogit): propagate loose-object and config write failures, and add read-only git index v4 support
- fix(nonpm): reject unsafe archive paths, cap extracted size, and fail closed on missing or malformed integrity hashes
- fix(nouv): reject unsafe wheel and sdist paths, cap download and extraction size, and verify downloaded hashes
- fix(noimg): validate image dimensions and chunk lengths in bmp, gif, jpeg, png and webp decoders to prevent OOM
- fix(noagent): enforce path containment on file tools and fix streaming tool-call slot expansion
- fix(nojq): correct eval semantics and option handling
- chore(skills): sync .agents/rules via Makefile and remove legacy nolang helper skills

## v0.1.35

- fix(notools): repair md5 digest returning 32 control bytes by replacing str option index writes with string concatenation in md5x
- fix(notools): apply the same str index-write fix to sha1x/sha224x/sha256x/sha384x/sha512x hex output
- fix(notools): use std crypto sha384-hex/sha512-hex for sha384, sha384sum and hmac-sha512 to bypass a legacy u64 compression bug

## v0.1.34

- feat(std): promote exit from the os module to a global builtin
- refactor(tools): run subcommands as top-level scripts instead of wrapping them in main
- refactor(notools): migrate command sources to D1 option arithmetic with explicit result unwrapping
- fix(noimg): replace removed number width-cast functions with f64/i64 to-i64/to-f64 methods
- fix(nojq): rename a colliding variable in main and move bi-code into the parser module for codegen
- fix(nonpm): bind indexed vec reads to plain locals so fs.is-dir and is-file marshal correctly
- fix(ci): repoint build-nolang to main and bump the pinned compiler to v0.4.27
- refactor: remove redundant overflow annotations and explicit type annotations
- docs(design): mark the unified option-migration document as review-complete
- refactor(release): drop the dirty-tree blocker and use the history section as the commit message
- fix(checker): include nested block statements in filterByExports
- fix(projects): resolve implicit option-unwrap compile errors in subprojects
- fix(compiler-issues): convert C-style comments to semicolon comments
- fix(notools): improve module safety and restore the eprint diagnostic in timeout
- refactor(notools): migrate index writes to option form and replace set-byte usage
- docs(skills): update stdlib docs and skill references for noml format and syntax changes
- fix(noimg): repair VP8L color-index decode for multi-color WebP images
- fix(nogit): adapt oid hex encoding and SHA-1 helpers to v0.4.27 option and char semantics
- fix(nogit): simplify string range slicing with plain integer bounds
- fix(nogit): bind value-match results to locals before passing them to hexdigit
- fix(noimg): unwrap co-o option into a variable to avoid the co coroutine keyword
- fix(notools): gate timeout-run by platform and stub it on Windows for waitpid-nohang

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
