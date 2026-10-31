---
name: second-brain
description: Retrieve context from Jeff's Obsidian vault (his notes on Breeze systems, aircraft/ACARS/ARINC, OCT, Flightdeck, Collins partners, team norms) and save new notes to it. Use when Jeff says "check my notes", "what do I know about...", "save this to my vault", or asks about topics his notes likely cover.
---

# Second Brain

Vault: `/Users/jeffstapleton/Documents/Obsidian/breeze` (plain markdown, `[[wikilinks]]`, no frontmatter convention, many notes are short stubs).

## Retrieve
1. The session-start index lists every note. If it isn't in context, run `~/.claude/skills/second-brain/scripts/vault-index.sh`.
2. Grep the vault for the topic, including acronyms and synonyms (e.g. ACARS, AOC, ATSU, OCT, Flightdeck). Search case-insensitively.
3. Read the best matches. Follow `[[wikilinks]]` one hop; resolve them by filename anywhere in the vault.
4. Skip PDFs/video unless asked. For a PDF, use Read with `pages`.
5. Answer using the notes, and name the notes used. If the notes are thin or absent, say so rather than guessing. Notes may be stale, so flag conflicts with what Jeff said in this session.

## Capture (only when Jeff asks)
- Write a new file `Claude-Inbox/<YYYY-MM-DD> <title>.md` in the vault. Create the folder if needed.
- Frontmatter: `source: claude` and `date: <YYYY-MM-DD>`. Add `[[wikilinks]]` to related existing notes.
- Never edit, move, or delete existing notes. The vault auto-commits and pushes to git about every minute, so tell Jeff the note will sync.
