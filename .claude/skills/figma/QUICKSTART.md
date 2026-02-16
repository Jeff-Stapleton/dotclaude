# Figma Skill Quick Start

Get started with the Figma skill in 3 steps:

## 1. Install Dependencies

```bash
cd .claude/skills/figma
pip install -r requirements.txt
```

Or install globally:
```bash
pip install requests pillow
```

## 2. Get Your Figma API Token

1. Go to https://www.figma.com/
2. Log in to your account
3. Go to **Settings** → **Account** → **Personal Access Tokens**
4. Click **"Generate new token"**
5. Give it a name (e.g., "Claude Code")
6. Copy the token

## 3. Set the Environment Variable

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export FIGMA_API_TOKEN="your-token-here"
```

Or add to your project's `.env` file:

```
FIGMA_API_TOKEN=your-token-here
```

## Quick Test

1. Find a Figma file URL: `https://www.figma.com/file/ABC123/My-File`
2. Extract the file key: `ABC123`
3. Test the skill:

```bash
cd .claude/skills/figma
python main.py get_file_structure ABC123
```

## Using with Claude Code

Once set up, just ask Claude:

- "Show me the colors from Figma file ABC123"
- "Extract design tokens from my Figma file"
- "Export icons from [file-key]"
- "What components are in this design file?"

Claude will automatically use the Figma skill!

## Need Help?

See the full [README.md](README.md) for detailed documentation.
