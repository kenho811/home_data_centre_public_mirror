# Modified from https://github.com/marimo-team/marimo-gh-pages-template
#!/usr/bin/env python3

import os
import subprocess
import argparse
from typing import List
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def export_html_wasm_as_app(notebook_path: str, output_dir: str) -> bool:
    """Export a single marimo notebook to HTML format.

    Returns:
        bool: True if export succeeded, False otherwise
    """
    output_path = notebook_path.replace(".py", ".html")

    cmd = ["marimo", "export", "html-wasm"]

    print(f"Exporting {notebook_path} to {output_path} as app")
    cmd.extend(["--mode", "run"])

    try:
        output_file = os.path.join(output_dir, output_path)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        cmd.extend([notebook_path, "-o", output_file])
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error exporting {notebook_path}:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error exporting {notebook_path}: {e}")
        return False


def generate_index(all_notebooks: List[str], output_dir: str) -> None:
    """Generate the index.html file."""
    print("Generating index.html")

    index_path = os.path.join(output_dir, "index.html")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        template = env.get_template("index.j2")

        # Render the template with the notebooks data
        rendered_html = template.render(all_notebooks=all_notebooks)

        # Write the rendered HTML to file
        with open(index_path, "w") as f:
            f.write(rendered_html)
    except IOError as e:
        print(f"Error generating index.html: {e}")
    except Exception as e:
        print(f"Error rendering template: {e}")


def main(
        notebook_directories: List
) -> None:
    parser = argparse.ArgumentParser(description="Build marimo notebooks")
    parser.add_argument(
        "--output-dir", default="_site", help="Output directory for built files"
    )
    args = parser.parse_args()

    all_notebooks: List[str] = []
    for directory in notebook_directories:
        dir_path = Path('marimo').joinpath(directory)
        if not dir_path.exists():
            print(f"Warning: Directory not found: {dir_path}")
            continue

        all_notebooks.extend(str(path) for path in dir_path.rglob("*.py"))

    if not all_notebooks:
        print("No notebooks found!")
        return

    # Export notebooks sequentially
    for nb in all_notebooks:
        export_html_wasm_as_app(nb, args.output_dir)

    # Generate index only if all exports succeeded
    generate_index(all_notebooks, args.output_dir)


if __name__ == "__main__":
    notebook_directories = [
        'stock_trend',
        'ccass_correlation'
    ]
    main(notebook_directories)