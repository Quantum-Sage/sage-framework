import markdown
from pathlib import Path

def format_universal():
    # Paths
    # Note: Using the absolute path to ensure we hit the correct draft
    md_path = Path(r"c:/Users/tylor/Desktop/the apex signel/(not for github)/drop box/paper3_universal_stochastic_penalty.md")
    output_path = Path("papers/paper3_universal_stochastic_penalty.html")
    
    if not md_path.exists():
        print(f"Error: {md_path} not found.")
        return

    # Read markdown
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert to HTML
    html_body = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'toc'])

    # CSS Template (Shared with Paper 3 for consistency)
    css = """
    :root {
        --bg: #050505;
        --text: #e0e0e0;
        --accent: #ffd700;
        --secondary: #00ffcc;
        --border: #333;
        --surface: #111;
        --font-serif: 'Times New Roman', serif;
        --font-sans: 'Inter', -apple-system, system-ui, sans-serif;
    }

    body {
        background: var(--bg);
        color: var(--text);
        font-family: var(--font-serif);
        line-height: 1.7;
        max-width: 900px;
        margin: 0 auto;
        padding: 50px 20px;
        font-size: 19px;
    }

    h1, h2, h3 {
        font-family: var(--font-sans);
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px;
        margin-top: 50px;
    }

    h1 { font-size: 2.5em; text-align: center; border: none; }
    
    .metadata {
        text-align: center;
        font-family: var(--font-sans);
        color: var(--secondary);
        margin-bottom: 50px;
        font-size: 0.9em;
    }

    hr { border: 0; border-top: 1px solid var(--border); margin: 40px 0; }

    code {
        font-family: 'Courier New', monospace;
        background: var(--surface);
        padding: 2px 5px;
        border-radius: 4px;
        color: var(--secondary);
    }

    pre {
        background: var(--surface);
        padding: 20px;
        border-left: 4px solid var(--accent);
        overflow-x: auto;
    }

    blockquote {
        border-left: 4px solid var(--secondary);
        padding-left: 20px;
        margin: 30px 0;
        font-style: italic;
        color: #aaa;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 30px 0;
        font-family: var(--font-sans);
        font-size: 0.9em;
    }

    th, td {
        border: 1px solid var(--border);
        padding: 12px;
        text-align: left;
    }

    th {
        background: var(--surface);
        color: var(--accent);
    }

    @media (max-width: 600px) {
        body { padding: 20px 10px; font-size: 17px; }
    }
    """

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SAGE Framework - Universal Stochastic Penalty</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="abstract-box" style="background: rgba(0, 255, 204, 0.05); border: 1px solid rgba(0, 255, 204, 0.2); padding: 20px; margin-bottom: 30px; border-radius: 8px; font-family: var(--font-sans); font-size: 0.85em;">
            <strong>Note:</strong> This document represents a theoretical mathematical extension of the SAGE Framework applied to classical logistics. Empirical validation for non-quantum domains is ongoing.
        </div>
        {html_body}
    </body>
    </html>
    """

    # Ensure output dir exists
    Path("papers").mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    format_universal()
