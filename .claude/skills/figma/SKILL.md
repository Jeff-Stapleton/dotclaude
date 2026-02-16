# Figma Design System Integration

Interface with Figma API to read files, extract design tokens, export assets, and understand design systems to inform UI development.

## Description

This skill enables Claude to:
- Browse and read Figma files, pages, frames, and layers
- Extract design system tokens (colors, typography, spacing, shadows, etc.)
- Export assets and components as images
- Analyze design patterns to inform component development
- Read and understand component structures for code generation

## Features

### File Navigation
- List all files in a Figma project
- Read file structure including pages, frames, and layers
- Navigate component hierarchies

### Design Token Extraction
- Extract color palettes and color variables
- Parse typography styles (fonts, sizes, line heights, letter spacing)
- Get spacing and layout tokens
- Extract shadow and effect styles
- Retrieve border radius and other style properties

### Asset Export
- Export frames, components, and images in various formats (PNG, JPG, SVG)
- Batch export multiple assets
- Get URLs for exported assets

### Design System Analysis
- Identify design patterns and component structures
- Analyze consistency across design files
- Map design components to code requirements
- Generate component specifications from designs

## Usage

The skill requires a Figma API token set in the environment variable `FIGMA_API_TOKEN`.

Examples:
- "Show me the color palette from [file-key]"
- "Export all icons from [file-key]"
- "What typography styles are defined in [file-key]?"
- "List all components in [file-key]"
- "Analyze the button component structure in [file-key]"

## API Reference

The skill uses the Figma REST API with the following endpoints:
- GET /v1/files/:key - Get file data
- GET /v1/files/:key/nodes - Get specific nodes
- GET /v1/images/:key - Export images
- GET /v1/files/:key/components - Get file components
- GET /v1/files/:key/styles - Get file styles

## Requirements

- Figma API token with appropriate permissions
- Python 3.8+
- Required packages: requests, pillow (for image processing)
