# Figma Design System Integration Skill

A custom Claude Code skill for interfacing with the Figma API to read files, extract design tokens, export assets, and understand design systems to inform UI development.

## Setup

### 1. Install Dependencies

The skill requires Python 3.8+ and the following packages:

```bash
pip install -r requirements.txt
```

### 2. Get a Figma API Token

1. Log in to your Figma account
2. Go to Settings → Account → Personal Access Tokens
3. Click "Generate new token"
4. Give it a descriptive name (e.g., "Claude Code Integration")
5. Copy the token

### 3. Set Environment Variable

Add your Figma API token to your environment:

```bash
export FIGMA_API_TOKEN="your-token-here"
```

Or add it to your `.env` file:

```
FIGMA_API_TOKEN=your-token-here
```

### 4. Enable the Skill

The skill is already enabled in `.claude/settings.local.json`. If you need to manually enable it:

```json
{
  "permissions": {
    "allow": [
      "Skill(figma)"
    ]
  }
}
```

## Usage

### Getting File Structure

Extract the file key from a Figma URL. For example:
- URL: `https://www.figma.com/file/ABC123/My-Design-File`
- File Key: `ABC123`

Then run:

```bash
python main.py get_file_structure ABC123
```

This will return:
- File name and metadata
- All pages in the file
- Top-level frames and their types

### Extracting Design Tokens

Extract colors and typography from a file:

```bash
python main.py extract_design_tokens ABC123
```

This returns:
- **Colors**: All fill and stroke colors found in the file
- **Typography**: Text styles including font families, weights, sizes, line heights, and letter spacing

### Exporting Assets

To export specific nodes as images, you need the node IDs. You can get these from the file structure or from the Figma URL when selecting an object.

```bash
# Export as PNG (default)
python main.py export_assets ABC123 "node-1,node-2,node-3"

# Export as SVG
python main.py export_assets ABC123 "node-1,node-2" svg

# Export at 2x scale
python main.py export_assets ABC123 "node-1" png 2.0
```

Supported formats:
- `png` (default)
- `jpg`
- `svg`
- `pdf`

### Analyzing Components

Get information about all components defined in a file:

```bash
python main.py analyze_components ABC123
```

Returns:
- Total component count
- Component names and descriptions
- Component keys for reference

## Integration with Claude Code

Once set up, you can ask Claude to help with design-related tasks:

- "Extract the color palette from my Figma file ABC123"
- "Show me the typography styles defined in [file-key]"
- "Export the icons from frame X in my Figma file"
- "What components are defined in this design file?"
- "Help me understand the spacing system in this Figma file"

Claude will use the Figma skill automatically when you reference Figma files or design system tasks.

## Common Use Cases

### 1. Building a Design System in Code

```
"Extract all design tokens from Figma file ABC123 and help me create a TypeScript theme file"
```

Claude will:
1. Extract colors, typography, and spacing
2. Generate a properly typed theme object
3. Organize tokens into a reusable structure

### 2. Implementing a Component

```
"Look at the Button component in Figma file ABC123 and help me implement it in React"
```

Claude will:
1. Analyze the component structure
2. Extract relevant styles and variants
3. Generate React component code with props matching the design

### 3. Asset Management

```
"Export all icons from the Icons page in ABC123 as SVGs"
```

Claude will:
1. Navigate to the Icons page
2. Identify icon frames
3. Export them as SVG files
4. Provide download URLs

## API Reference

### Commands

#### `get_file_structure <file_key>`
Returns the hierarchical structure of a Figma file.

**Output:**
```json
{
  "name": "Design System",
  "pages": [
    {
      "id": "0:1",
      "name": "Colors",
      "frames": [...]
    }
  ]
}
```

#### `extract_design_tokens <file_key>`
Extracts all design tokens from a file.

**Output:**
```json
{
  "colors": {
    "Primary Blue": "#0066ff",
    "Secondary Green": "#00cc66"
  },
  "typography": {
    "Heading 1": {
      "fontFamily": "Inter",
      "fontSize": 32,
      "fontWeight": 700
    }
  }
}
```

#### `export_assets <file_key> <node_ids> [format] [scale]`
Exports nodes as images.

**Arguments:**
- `file_key`: Figma file key
- `node_ids`: Comma-separated list of node IDs
- `format`: png, jpg, svg, or pdf (default: png)
- `scale`: Export scale multiplier (default: 1.0)

**Output:**
```json
{
  "node-1": "https://figma-alpha-api.s3.us-west-2.amazonaws.com/...",
  "node-2": "https://figma-alpha-api.s3.us-west-2.amazonaws.com/..."
}
```

#### `analyze_components <file_key>`
Analyzes component structure in a file.

**Output:**
```json
{
  "componentCount": 24,
  "components": [
    {
      "key": "component-key",
      "name": "Button/Primary",
      "description": "Primary action button"
    }
  ]
}
```

## Troubleshooting

### "Access denied" Error
- Check that your FIGMA_API_TOKEN is set correctly
- Verify the token has access to the file
- Ensure the file is not in a private team you don't have access to

### "Resource not found" Error
- Verify the file key is correct
- Check that the file hasn't been deleted
- Ensure you're using the file key, not the file URL

### Module Import Errors
- Run `pip install -r requirements.txt` to install dependencies
- Check that you're using Python 3.8 or later

## Limitations

- The Figma API has rate limits (check Figma's documentation)
- Complex files with thousands of nodes may take time to process
- Image export URLs are temporary and expire after a period
- Some Figma features (prototyping, etc.) are not accessible via API

## Contributing

To extend this skill:

1. Add new methods to the `FigmaClient` class for additional API endpoints
2. Create extractors for new token types in `DesignTokenExtractor`
3. Add new commands to the `FigmaSkill` class
4. Update the `main()` function to handle new commands
5. Document new features in this README

## Resources

- [Figma API Documentation](https://www.figma.com/developers/api)
- [Figma REST API Reference](https://www.figma.com/developers/api#get-files-endpoint)
- [Claude Code Skills Documentation](https://docs.anthropic.com/claude/docs/skills)
