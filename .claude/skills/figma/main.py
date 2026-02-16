#!/usr/bin/env python3
"""
Figma Design System Integration Skill

This skill provides integration with the Figma API to read files,
extract design tokens, export assets, and analyze design systems.
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ExportFormat(str, Enum):
    """Supported export formats for Figma assets"""
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    PDF = "pdf"


@dataclass
class FigmaConfig:
    """Configuration for Figma API access"""
    api_token: str
    base_url: str = "https://api.figma.com/v1"

    @classmethod
    def from_env(cls) -> 'FigmaConfig':
        """Create config from environment variables"""
        token = os.getenv('FIGMA_API_TOKEN')
        if not token:
            raise ValueError("FIGMA_API_TOKEN environment variable not set")
        return cls(api_token=token)


class FigmaClient:
    """Client for interacting with the Figma API"""

    def __init__(self, config: FigmaConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-Figma-Token': config.api_token,
            'Content-Type': 'application/json'
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Figma API"""
        url = f"{self.config.base_url}/{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError(f"Access denied. Check your Figma API token permissions. {e}")
            elif e.response.status_code == 404:
                raise ValueError(f"Resource not found. Check the file key or node ID. {e}")
            else:
                raise ValueError(f"Figma API error: {e}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request failed: {e}")

    def get_file(self, file_key: str, depth: Optional[int] = None) -> Dict[str, Any]:
        """Get a Figma file's data

        Args:
            file_key: The Figma file key (from the URL)
            depth: How many levels deep to traverse (default: all levels)

        Returns:
            File data including document structure
        """
        params = {}
        if depth is not None:
            params['depth'] = depth

        return self._request('GET', f'files/{file_key}', params=params)

    def get_file_nodes(self, file_key: str, node_ids: List[str]) -> Dict[str, Any]:
        """Get specific nodes from a file

        Args:
            file_key: The Figma file key
            node_ids: List of node IDs to retrieve

        Returns:
            Node data for the specified nodes
        """
        params = {'ids': ','.join(node_ids)}
        return self._request('GET', f'files/{file_key}/nodes', params=params)

    def get_images(self, file_key: str, node_ids: List[str],
                   format: ExportFormat = ExportFormat.PNG,
                   scale: float = 1.0) -> Dict[str, str]:
        """Export images from a file

        Args:
            file_key: The Figma file key
            node_ids: List of node IDs to export
            format: Export format (png, jpg, svg, pdf)
            scale: Export scale (1.0 = 1x, 2.0 = 2x, etc.)

        Returns:
            Dictionary mapping node IDs to image URLs
        """
        params = {
            'ids': ','.join(node_ids),
            'format': format.value,
            'scale': str(scale)
        }
        result = self._request('GET', f'images/{file_key}', params=params)
        return result.get('images', {})

    def get_file_styles(self, file_key: str) -> Dict[str, Any]:
        """Get all styles defined in a file

        Args:
            file_key: The Figma file key

        Returns:
            Style data including colors, text styles, effects, etc.
        """
        return self._request('GET', f'files/{file_key}/styles')

    def get_file_components(self, file_key: str) -> Dict[str, Any]:
        """Get all components defined in a file

        Args:
            file_key: The Figma file key

        Returns:
            Component data
        """
        return self._request('GET', f'files/{file_key}/components')

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information including accessible teams

        Returns:
            User data including team memberships
        """
        return self._request('GET', 'me')

    def get_team_projects(self, team_id: str) -> Dict[str, Any]:
        """Get all projects for a specific team

        Args:
            team_id: The Figma team ID

        Returns:
            List of projects in the team
        """
        return self._request('GET', f'teams/{team_id}/projects')


class DesignTokenExtractor:
    """Extract design tokens from Figma files"""

    @staticmethod
    def extract_colors(node: Dict[str, Any], colors: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Extract color values from a node and its children

        Args:
            node: Figma node data
            colors: Existing color dictionary to add to

        Returns:
            Dictionary of color names/IDs to hex values
        """
        if colors is None:
            colors = {}

        # Check for fills
        if 'fills' in node:
            for fill in node['fills']:
                if fill.get('type') == 'SOLID' and 'color' in fill:
                    color = fill['color']
                    hex_color = DesignTokenExtractor._rgb_to_hex(
                        color.get('r', 0),
                        color.get('g', 0),
                        color.get('b', 0)
                    )
                    # Use node name as key if available
                    key = node.get('name', f"color_{len(colors)}")
                    colors[key] = hex_color

        # Check for strokes
        if 'strokes' in node:
            for stroke in node['strokes']:
                if stroke.get('type') == 'SOLID' and 'color' in stroke:
                    color = stroke['color']
                    hex_color = DesignTokenExtractor._rgb_to_hex(
                        color.get('r', 0),
                        color.get('g', 0),
                        color.get('b', 0)
                    )
                    key = f"{node.get('name', 'stroke')}_{len(colors)}"
                    colors[key] = hex_color

        # Recursively process children
        if 'children' in node:
            for child in node['children']:
                DesignTokenExtractor.extract_colors(child, colors)

        return colors

    @staticmethod
    def _rgb_to_hex(r: float, g: float, b: float) -> str:
        """Convert RGB (0-1) to hex color"""
        r_int = int(r * 255)
        g_int = int(g * 255)
        b_int = int(b * 255)
        return f"#{r_int:02x}{g_int:02x}{b_int:02x}"

    @staticmethod
    def extract_typography(node: Dict[str, Any], styles: Optional[Dict[str, Dict]] = None) -> Dict[str, Dict]:
        """Extract typography styles from a node and its children

        Args:
            node: Figma node data
            styles: Existing styles dictionary to add to

        Returns:
            Dictionary of text style names to their properties
        """
        if styles is None:
            styles = {}

        if node.get('type') == 'TEXT' and 'style' in node:
            style = node['style']
            style_name = node.get('name', f"text_style_{len(styles)}")

            styles[style_name] = {
                'fontFamily': style.get('fontFamily'),
                'fontWeight': style.get('fontWeight'),
                'fontSize': style.get('fontSize'),
                'lineHeight': style.get('lineHeightPx'),
                'letterSpacing': style.get('letterSpacing'),
                'textAlign': style.get('textAlignHorizontal'),
            }

        # Recursively process children
        if 'children' in node:
            for child in node['children']:
                DesignTokenExtractor.extract_typography(child, styles)

        return styles

    @staticmethod
    def extract_spacing(node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract spacing and layout information from a node

        Args:
            node: Figma node data

        Returns:
            Dictionary of spacing properties
        """
        spacing = {}

        if 'paddingLeft' in node:
            spacing['paddingLeft'] = node['paddingLeft']
        if 'paddingRight' in node:
            spacing['paddingRight'] = node['paddingRight']
        if 'paddingTop' in node:
            spacing['paddingTop'] = node['paddingTop']
        if 'paddingBottom' in node:
            spacing['paddingBottom'] = node['paddingBottom']
        if 'itemSpacing' in node:
            spacing['gap'] = node['itemSpacing']

        return spacing


class FigmaSkill:
    """Main skill class for Figma integration"""

    def __init__(self):
        self.config = FigmaConfig.from_env()
        self.client = FigmaClient(self.config)
        self.extractor = DesignTokenExtractor()

    def get_file_structure(self, file_key: str) -> Dict[str, Any]:
        """Get the structure of a Figma file

        Args:
            file_key: The Figma file key from the URL

        Returns:
            Structured data about the file including pages and top-level frames
        """
        file_data = self.client.get_file(file_key, depth=2)

        structure = {
            'name': file_data.get('name'),
            'lastModified': file_data.get('lastModified'),
            'version': file_data.get('version'),
            'pages': []
        }

        document = file_data.get('document', {})
        for child in document.get('children', []):
            if child.get('type') == 'CANVAS':
                page = {
                    'id': child.get('id'),
                    'name': child.get('name'),
                    'frames': []
                }

                for frame in child.get('children', []):
                    page['frames'].append({
                        'id': frame.get('id'),
                        'name': frame.get('name'),
                        'type': frame.get('type')
                    })

                structure['pages'].append(page)

        return structure

    def extract_design_tokens(self, file_key: str) -> Dict[str, Any]:
        """Extract all design tokens from a file

        Args:
            file_key: The Figma file key

        Returns:
            Dictionary containing colors, typography, and spacing tokens
        """
        file_data = self.client.get_file(file_key)
        document = file_data.get('document', {})

        tokens = {
            'colors': self.extractor.extract_colors(document),
            'typography': self.extractor.extract_typography(document),
        }

        return tokens

    def export_assets(self, file_key: str, node_ids: List[str],
                     format: str = 'png', scale: float = 1.0) -> Dict[str, str]:
        """Export assets from a Figma file

        Args:
            file_key: The Figma file key
            node_ids: List of node IDs to export
            format: Export format (png, jpg, svg, pdf)
            scale: Export scale multiplier

        Returns:
            Dictionary mapping node IDs to download URLs
        """
        export_format = ExportFormat(format.lower())
        return self.client.get_images(file_key, node_ids, export_format, scale)

    def analyze_components(self, file_key: str) -> Dict[str, Any]:
        """Analyze component structure in a file

        Args:
            file_key: The Figma file key

        Returns:
            Component analysis data
        """
        components_data = self.client.get_file_components(file_key)

        analysis = {
            'componentCount': len(components_data.get('meta', {}).get('components', [])),
            'components': []
        }

        for component in components_data.get('meta', {}).get('components', []):
            analysis['components'].append({
                'key': component.get('key'),
                'name': component.get('name'),
                'description': component.get('description'),
            })

        return analysis

    def list_teams(self, org_name: Optional[str] = None) -> Dict[str, Any]:
        """List all teams accessible to the current user

        Args:
            org_name: Optional organization name to filter by

        Returns:
            List of teams and their details
        """
        user_data = self.client.get_user_info()
        teams = []

        # Get teams from user data
        for team in user_data.get('teams', []):
            team_info = {
                'id': team.get('id'),
                'name': team.get('name'),
            }

            # If org_name is specified, only include matching teams
            if org_name is None or org_name.lower() in team.get('name', '').lower():
                # Get projects for this team
                try:
                    projects_data = self.client.get_team_projects(team.get('id'))
                    team_info['projects'] = []
                    for project in projects_data.get('projects', []):
                        team_info['projects'].append({
                            'id': project.get('id'),
                            'name': project.get('name'),
                        })
                except Exception as e:
                    team_info['projects_error'] = str(e)

                teams.append(team_info)

        result = {
            'teamCount': len(teams),
            'teams': teams
        }

        if org_name:
            result['filteredBy'] = org_name

        return result

    def get_team_info(self, team_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific team including all projects

        Args:
            team_id: The Figma team ID

        Returns:
            Team information and list of projects
        """
        projects_data = self.client.get_team_projects(team_id)

        result = {
            'teamId': team_id,
            'projectCount': len(projects_data.get('projects', [])),
            'projects': []
        }

        for project in projects_data.get('projects', []):
            result['projects'].append({
                'id': project.get('id'),
                'name': project.get('name'),
            })

        return result


def main():
    """Main entry point for the skill"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Usage: python main.py <command> [args...]',
            'commands': [
                'get_file_structure <file_key>',
                'extract_design_tokens <file_key>',
                'export_assets <file_key> <node_id1,node_id2,...> [format] [scale]',
                'analyze_components <file_key>',
                'list_teams [org_name]',
                'get_team_info <team_id>'
            ]
        }))
        sys.exit(1)

    command = sys.argv[1]
    skill = FigmaSkill()

    try:
        if command == 'get_file_structure':
            if len(sys.argv) < 3:
                raise ValueError("file_key required")
            result = skill.get_file_structure(sys.argv[2])

        elif command == 'extract_design_tokens':
            if len(sys.argv) < 3:
                raise ValueError("file_key required")
            result = skill.extract_design_tokens(sys.argv[2])

        elif command == 'export_assets':
            if len(sys.argv) < 4:
                raise ValueError("file_key and node_ids required")
            file_key = sys.argv[2]
            node_ids = sys.argv[3].split(',')
            format = sys.argv[4] if len(sys.argv) > 4 else 'png'
            scale = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
            result = skill.export_assets(file_key, node_ids, format, scale)

        elif command == 'analyze_components':
            if len(sys.argv) < 3:
                raise ValueError("file_key required")
            result = skill.analyze_components(sys.argv[2])

        elif command == 'list_teams':
            org_name = sys.argv[2] if len(sys.argv) > 2 else None
            result = skill.list_teams(org_name)

        elif command == 'get_team_info':
            if len(sys.argv) < 3:
                raise ValueError("team_id required")
            result = skill.get_team_info(sys.argv[2])

        else:
            raise ValueError(f"Unknown command: {command}")

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
