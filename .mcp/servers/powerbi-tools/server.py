from mcp.server import Server
import subprocess

server = Server("powerbi-tools")

@server.tool()
def generate_mermaid() -> str:
    """Génère la documentation Mermaid Power BI"""
    subprocess.run(["python", "scripts/generate_mermaid.py"], check=True)
    return "Mermaid généré avec succès"

@server.tool()
def read_doc() -> str:
    """Lit le Markdown généré"""
    with open("docs/model-diagram.md", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    server.run()
