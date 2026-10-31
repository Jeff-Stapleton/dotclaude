#!/bin/bash
# Prints the Obsidian vault note tree for injection as session context.
VAULT="/Users/jeffstapleton/Documents/Obsidian/breeze"
[ -d "$VAULT" ] || exit 0

echo "## Second brain: Obsidian vault at $VAULT"
echo "Jeff's personal notes. Before answering questions on Breeze systems, aircraft/ACARS/ARINC, OCT/Flightdeck, partners, or team norms, read relevant notes (Grep/Read). Cite note names. Read-only unless Jeff asks to save (-> Claude-Inbox/). See the second-brain skill."
echo
echo "Notes (relative to vault):"
cd "$VAULT" && find . -name '*.md' \
  -not -path './.obsidian/*' -not -path './.git/*' -not -path './.claudian/*' -not -path './.trash/*' \
  | sed 's|^\./||' | sort
