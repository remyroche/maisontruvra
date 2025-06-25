# ==============================================================================
# File: backend/utils/vite.py (NEW FILE)
# Description: This helper reads the Vite manifest file to inject the correct
#              versioned asset paths into the Jinja2 templates.
# ==============================================================================
import json
import os
from flask import current_app, Markup, url_for

def vite_asset(path):
    """
    Vite asset helper.
    Generates a <script> or <link> tag for a Vite asset.
    In development, it points to the Vite dev server.
    In production, it points to the built asset file.
    """
    manifest_path = os.path.join(current_app.static_folder, 'dist', 'manifest.json')
    
    # In development, Vite serves assets from its own server (HMR)
    if current_app.debug:
        # The base script for the dev server must be included.
        # This assumes your Vite dev server is running on localhost:5173
        dev_server_base = "http://localhost:5173"
        return Markup(f'<script type="module" src="{dev_server_base}/@vite/client"></script>\n'
                      f'<script type="module" src="{dev_server_base}/{path}"></script>')

    # In production, read from the manifest file
    if not os.path.exists(manifest_path):
        raise RuntimeError("Vite manifest not found. Did you run 'npm run build'?")

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    if path not in manifest:
        raise RuntimeError(f"Vite asset not found in manifest: {path}")

    asset_data = manifest[path]
    html = ""
    
    # Generate <script> tag for the main JS file
    if 'file' in asset_data:
        asset_url = url_for('static', filename=os.path.join('dist', asset_data['file']))
        html += f'<script type="module" src="{asset_url}"></script>\n'
    
    # Generate <link> tags for any associated CSS files
    if 'css' in asset_data:
        for css_file in asset_data['css']:
            css_url = url_for('static', filename=os.path.join('dist', css_file))
            html += f'<link rel="stylesheet" href="{css_url}">\n'
            
    return Markup(html)
