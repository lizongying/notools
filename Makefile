# notools Makefile
# Build, test, and skill sync utilities for the notools workspace.

# --- Config ---
NO_LANG_REPO   := https://github.com/lizongying/nolang.git
NO_LANG_BRANCH := main
SKILLS_DIR     := .agents/skills
REMOTE_PATH    := .agents/skills

# --- Default ---
.PHONY: help
help:
	@echo "notools Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  sync-skills   Sync .agents/skills from $(NO_LANG_REPO) ($(NO_LANG_BRANCH))"
	@echo "  help          Show this help"

# --- Skill Sync (sparse checkout) ---
# Uses git sparse-checkout to fetch only .agents/skills from the nolang repo.
# Local-only files (not in the remote repo) are preserved.
# Note: the checkout happens inside the temp dir via --work-tree; the copy
# always writes to an absolute project path (never "../", which would resolve
# relative to the temp dir's parent).
.PHONY: sync-skills
sync-skills:
	@echo "==> Fetching skills from $(NO_LANG_REPO) ($(NO_LANG_BRANCH))..."
	@tmp=$$(mktemp -d); \
		dst=$$(pwd)/$(SKILLS_DIR); \
		mkdir -p $$tmp/repo && \
		cd $$tmp/repo && \
		git init -q && \
		git remote add origin $(NO_LANG_REPO) && \
		git config core.sparseCheckout true && \
		echo "$(REMOTE_PATH)/" > .git/info/sparse-checkout && \
		git fetch -q --depth=1 origin $(NO_LANG_BRANCH) && \
		git --work-tree=. checkout -q FETCH_HEAD -- $(REMOTE_PATH) && \
		echo "==> Syncing skills to $(SKILLS_DIR)/..." && \
		mkdir -p "$$dst" && \
		find $(REMOTE_PATH) -type f | while read f; do \
			dest="$$dst/$${f#$(REMOTE_PATH)/}"; \
			mkdir -p "$$(dirname "$$dest")"; \
			cp "$$f" "$$dest"; \
		done; \
		rm -rf $$tmp
	@echo "==> Done. Skills synced to $(SKILLS_DIR)/"
	@ls -1 $(SKILLS_DIR)/
