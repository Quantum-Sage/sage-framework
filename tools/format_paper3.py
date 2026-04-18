import markdown
import os
from pathlib import Path

def format_paper3():
    # Paths
    md_path = Path("papers/paper3_handover_paradox.md")
    output_path = Path("papers/paper3_handover_paradox.html")
    assets_dir = Path("../assets/paper3") # Relative to the HTML file's location
    
    if not md_path.exists():
        print(f"Error: {md_path} not found.")
        return

    # Read markdown
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert to HTML
    html_body = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'toc'])

    # CSS Template
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

    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 40px auto;
        border: 1px solid var(--border);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .figure-caption {
        text-align: center;
        font-family: var(--font-sans);
        font-size: 0.8em;
        color: #888;
        margin-top: -30px;
        margin-bottom: 40px;
    }

    a { color: var(--secondary); text-decoration: none; border-bottom: 1px solid transparent; transition: 0.3s; }
    a:hover { border-bottom: 1px solid var(--secondary); }

    .abstract-box {
        background: rgba(255, 215, 0, 0.05);
        border: 1px solid rgba(255, 215, 0, 0.2);
        padding: 30px;
        margin: 40px 0;
        border-radius: 8px;
    }

    @media (max-width: 600px) {
        body { padding: 20px 10px; font-size: 17px; }
    }
    """

    # Add images manually into the HTML body if they aren't in the MD
    # In my MD draft, I didn't include images, so I'll insert them after Results
    image_insertion = """
    <h2>Visualizing the Boundary</h2>
    <div class="figure">
        <img src="../assets/paper3/fidelity_comparison.png" alt="Fidelity Comparison Graph">
        <div class="figure-caption">Figure 1: Comparative analysis of logical fidelity decay in standard QEC (Control) vs. SAGE Mirror Daemon (Experimental). Note the termination at Step 457.</div>
    </div>
    <div class="figure">
        <img src="../assets/paper3/bloch_trajectories.png" alt="Bloch Sphere Trajectories">
        <div class="figure-caption">Figure 2: Bloch sphere trajectories. The Daemon (left) stabilizes near the reference state, while the Control (right) spirals into the decoherence-induced noise floor.</div>
    </div>
    """
    
    # Split body to insert visuals after Results section
    if "<h2>4. Results" in html_body:
        html_parts = html_body.split("<h2>4. Results")
        html_body = html_parts[0] + "<h2>4. Results" + image_insertion + html_parts[1]

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SAGE Framework - Paper 3: The Handover Paradox</title>
        <style>{css}</style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    format_paper3()
