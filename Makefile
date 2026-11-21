# notools Makefile
# Build, test, and skill/rule sync utilities for the notools workspace.

# --- Config ---
NO_LANG_REPO      := https://github.com/lizongying/nolang.git
NO_LANG_BRANCH    := main
SKILLS_DIR        := .agents/skills
SKILLS_REMOTE     := .agents/skills
RULES_DIR         := .agents/rules
RULES_REMOTE      := .agents/rules

# --- Default ---
.PHONY: help
help:
	@echo "notools Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  sync-skills   Sync .agents/skills & .agents/rules from $(NO_LANG_REPO) ($(NO_LANG_BRANCH))"
	@echo "  help          Show this help"

# --- Skill & Rule Sync (sparse checkout) ---
# Uses git sparse-checkout to fetch only .agents/skills and .agents/rules
# from the nolang repo. Local-only files (not in the remote repo) are preserved.
# Note: the checkout happens inside the temp dir via --work-tree; the copy
# always writes to absolute project paths (never "../", which would resolve
# relative to the temp dir's parent).
.PHONY: sync-skills
sync-skills:
	@echo "==> Fetching skills & rules from $(NO_LANG_REPO) ($(NO_LANG_BRANCH))..."
	@tmp=$$(mktemp -d); \
		dst_skills=$$(pwd)/$(SKILLS_DIR); \
		dst_rules=$$(pwd)/$(RULES_DIR); \
		mkdir -p $$tmp/repo && \
		cd $$tmp/repo && \
		git init -q && \
		git remote add origin $(NO_LANG_REPO) && \
		git config core.sparseCheckout true && \
		printf '%s/\n%s/\n' "$(SKILLS_REMOTE)" "$(RULES_REMOTE)" > .git/info/sparse-checkout && \
		git fetch -q --depth=1 origin $(NO_LANG_BRANCH) && \
		git --work-tree=. checkout -q FETCH_HEAD -- $(SKILLS_REMOTE) $(RULES_REMOTE) && \
		echo "==> Syncing to $(SKILLS_DIR)/ and $(RULES_DIR)/..." && \
		for spec in "$(SKILLS_REMOTE)@$$dst_skills" "$(RULES_REMOTE)@$$dst_rules"; do \
			src="$${spec%%@*}"; dest_root="$${spec#*@}"; \
			mkdir -p "$$dest_root"; \
			find "$$src" -type f | while read f; do \
				dest="$$dest_root/$${f#$$src/}"; \
				mkdir -p "$$(dirname "$$dest")"; \
				cp "$$f" "$$dest"; \
			done; \
		done; \
		rm -rf $$tmp
	@echo "==> Done. Skills -> $(SKILLS_DIR)/, rules -> $(RULES_DIR)/"
	@ls -1 $(SKILLS_DIR)/
	@ls -1 $(RULES_DIR)/
