# noNpm

Pure Nolang implementation of **pnpm** — a fast, disk-efficient package manager for Node.js.

## Features

- **Virtual Store** — Content-addressable store on disk, each package version stored only once
- **Isolated `node_modules`** — Symlink-based structure, no phantom dependencies
- **Semantic Versioning** — Full SemVer 2.0.0 range matching (`^`, `~`, `>=`, `<=`, `>`, `<`, `*`)
- **Workspace Support** — Monorepo management with `pnpm-workspace.yaml`
- **Lockfile** — Deterministic installs with `pnpm-lock.yaml`
- **Script Runner** — Run scripts from `package.json` with `nonpm run`
- **Package Publishing** — Pack and publish to npm registry
- **Binary Links** — Automatic `.bin` symlinks for CLI tools
- **Peer Dependencies** — Auto-install peer dependencies
- **Hoisting** — Optional shamefully-hoist mode for compatibility

## Installation

```bash
# Build and install
no build nonpm -o nonpm
no install nonpm

# Or run directly
no run nonpm <command>
```

## Commands

### Install Dependencies

```bash
# Install all dependencies from package.json
nonpm install

# Install with options
nonpm install --frozen-lockfile
nonpm install --prod
nonpm install --shamefully-hoist
```

### Add / Remove Packages

```bash
# Add a production dependency
nonpm add express

# Add with specific version
nonpm add express@4.17.1

# Add a dev dependency
nonpm add -D typescript

# Remove a dependency
nonpm remove express
```

### Run Scripts

```bash
# List available scripts
nonpm run

# Run a script
nonpm run build
nonpm run test -- --verbose
```

### Update Dependencies

```bash
# Update all dependencies
nonpm update

# Update specific packages
nonpm update express lodash
```

### Inspect Packages

```bash
# List installed packages
nonpm list

# Check for outdated packages
nonpm outdated

# Show why a package is installed
nonpm why express
```

### Create New Project

```bash
# Initialize a new project
nonpm init my-project

# Or in current directory
nonpm init
```

### Publish Packages

```bash
# Create a tarball
nonpm pack

# Publish to registry
nonpm publish

# Login to registry
nonpm login

# Check current user
nonpm whoami
```

### Execute Commands

```bash
# Run a command with node_modules/.bin in PATH
nonpm exec tsc

# Run a package in a temporary environment
nonpm dlx create-react-app my-app
```

### Linking

```bash
# Link a local package
nonpm link ../my-local-package

# Unlink
nonpm unlink my-local-package
```

### Cache Management

```bash
# Clean cache
nonpm cache clean

# Show cache directory
nonpm cache dir

# Prune stale entries
nonpm cache prune
```

## Configuration

### `.npmrc`

Configuration is read from:

1. **Global**: `~/.nonpm/config`
2. **Project**: `.npmrc` in project root
3. **Environment**: `NONPM_*` environment variables

```ini
# .npmrc example
registry=https://registry.npmjs.org/
shamefully-hoist=true
auto-install-peers=true
network-concurrency=16
node-linker=isolated
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `NONPM_REGISTRY` | Override registry URL |
| `NONPM_STORE_DIR` | Override store directory |
| `NONPM_CACHE_DIR` | Override cache directory |
| `NPM_TOKEN` | Auth token for publishing |
| `NONPM_TOKEN` | Alternative auth token |

## Architecture

### Virtual Store Structure

```
node_modules/
  .nonpm/                          ← Virtual store
    express@4.17.1/
      package/                      ← Extracted package
      node_modules/                 ← Package's own deps (symlinks)
    lodash@4.17.21/
      package/
      node_modules/
  express → .nonpm/express@4.17.1/package    ← Symlink
  lodash  → .nonpm/lodash@4.17.21/package     ← Symlink
  .bin/                             ← Binary links
    express
```

### Module Structure

| Module | Description |
|--------|-------------|
| `main.no` | CLI entry point and command dispatcher |
| `src/utils.no` | Utility functions (string, file, path, process) |
| `src/json.no` | JSON parsing and generation helpers |
| `src/semver.no` | SemVer 2.0.0 parsing, comparison, range matching |
| `src/config.no` | `.npmrc` configuration management |
| `src/registry.no` | npm registry HTTP interaction |
| `src/resolver.no` | Dependency resolution and conflict resolution |
| `src/installer.no` | Package installation and `node_modules` management |
| `src/linker.no` | Symlink management (pnpm isolated structure) |
| `src/lockfile.no` | `pnpm-lock.yaml` generation and reading |
| `src/tarball.no` | Tarball download and extraction |
| `src/workspace.no` | Workspace multi-package management |
| `src/run.no` | Script runner |
| `src/publish.no` | Package publishing |

## Testing

```bash
# Run all tests
no test

# Run specific test
no test tests/test-semver.no
```

## License

MIT
