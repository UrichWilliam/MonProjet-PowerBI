#!/usr/bin/env python3
"""
generate_mermaid.py — Auto-génération de diagrammes Mermaid depuis un projet PBIP.
Usage : python scripts/generate_mermaid.py
Output : docs/model-diagram.md
"""

import re
from pathlib import Path

# ─── CONFIGURATION ─────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent

semantic_folders = list(PROJECT_ROOT.glob('*.SemanticModel'))
if not semantic_folders:
    raise FileNotFoundError('Aucun dossier .SemanticModel trouvé.')
SEMANTIC_MODEL = semantic_folders[0]

TMDL_DEFINITION = SEMANTIC_MODEL / 'definition'
TABLES_DIR = TMDL_DEFINITION / 'tables'
MODEL_TMDL = TMDL_DEFINITION / 'model.tmdl'
OUTPUT_DIR = PROJECT_ROOT / 'docs'
OUTPUT_FILE = OUTPUT_DIR / 'model-diagram.md'

EXCLUDE_TABLES = {'DateTableTemplate', 'LocalDateTable', '__Unused__'}


# ─── NORMALISER LES NOMS ───────────────────────────────────────────

def mermaid_id(name: str) -> str:
    """Nettoie un nom pour qu'il soit compatible avec Mermaid."""
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


def mermaid_attr(name: str) -> str:
    """Nettoie un nom d'attribut pour Mermaid."""
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


def parse_name(match: re.Match) -> str:
    """Récupère le nom capturé par le regex, qu'il soit entre quotes ou pas."""
    return next(g for g in match.groups() if g is not None).strip()


# ─── PARSEURS TMDL ─────────────────────────────────────────────────

def parse_table(tmdl_path: Path) -> dict:
    """Parse un fichier .tmdl de table -> dict avec colonnes et mesures."""
    text = tmdl_path.read_text(encoding='utf-8')

    table_name_match = re.search(
        r'^table\s+(?:"([^"]+)"|\'([^\']+)\'|([^\s{]+))(?:\s*\{|$)',
        text,
        re.MULTILINE,
    )
    if not table_name_match:
        print(f'⚠️  Impossible de parser table dans {tmdl_path.name}')
        return None

    table_name = parse_name(table_name_match)
    print(f'  📋 Parsing table : {table_name}')

    is_fact = bool(re.search(r'^\s*measure\s+', text, re.MULTILINE))

    columns = []
    '''col_pattern = re.compile(
        r'^\s*(?:column|calculatedColumn)\s+'
        r'(?:"([^"]+)"|\'([^\']+)\'|([^\s{]+))\s*(?:\{|\n)',
        re.MULTILINE,
    )'''
    col_pattern = re.compile(
        r'^\s*(?:column|calculatedColumn)\s+'
        r'(?:"([^"]+)"|\'([^\']+)\'|([^\s{]+))\s*(?:\{|\n)',
        re.MULTILINE,
    )

    for col_match in col_pattern.finditer(text):
        col_name = parse_name(col_match)
        start = col_match.end()

        depth = 1
        pos = start
        while pos < len(text) and depth > 0:
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
            pos += 1

        block = text[start:pos - 1]

        #data_type_match = re.search(r'dataType:\s*([^\s\}]+)', block)
        data_type_match = re.search(
            r'dataType:\s*["\']?([^"\'}\s]+)["\']?',
            block,
            re.IGNORECASE,
        )
        data_type = data_type_match.group(1).strip() if data_type_match else 'unknown'

        dtype_map = {
            'int64': 'int',
            'int32': 'int',
            'decimal': 'decimal',
            'double': 'decimal',
            'string': 'string',
            'dateTime': 'date',
            'boolean': 'bool',
            'binary': 'binary',
        }
        col_type = dtype_map.get(data_type, data_type)
        is_key = bool(re.search(r'isKey:\s*true', block, re.IGNORECASE))

        columns.append(
            {
                'name': col_name,
                'type': col_type,
                'is_key': is_key,
            }
        )

    measures = []
    measure_pattern = re.compile(
        r'^\s*measure\s+(?:"([^"]+)"|\'([^\']+)\'|([^\s{]+))',
        re.MULTILINE,
    )
    for m in measure_pattern.finditer(text):
        measures.append(parse_name(m))

    print(f'      → {len(columns)} colonnes, {len(measures)} mesures')
    return {
        'name': table_name,
        'is_fact': is_fact,
        'columns': columns,
        'measures': measures,
    }

def parse_column_ref(column_ref: str) -> tuple[str, str]:
    """Sépare Table.Col ou 'Table Name'.Col en table / colonne."""
    column_ref = column_ref.strip()
    match = re.match(r"""^(['"])(.+?)\1\.(.+)$""", column_ref)
    if match:
        return match.group(2).strip(), match.group(3).strip().strip("'\"")
    if '.' in column_ref:
        table, col = column_ref.split('.', 1)
        return table.strip().strip("'\""), col.strip().strip("'\"")
    return None, None


def parse_relationships(definition_dir: Path) -> list:
    """Parse les relations depuis tous les fichiers .tmdl du dossier definition."""
    relationships = []
    if not definition_dir.exists():
        print(f'⚠️  Dossier non trouvé : {definition_dir}')
        return []

    for tmdl_path in sorted(definition_dir.glob('*.tmdl')):
        text = tmdl_path.read_text(encoding='utf-8')
        rel_blocks = re.findall(
            r'^relationship\s+[^\n]+\n(?:[ \t]+[^\n]+\n)*',
            text,
            re.MULTILINE | re.IGNORECASE,
        )
        for block in rel_blocks:
            from_match = re.search(
                r'^\s*fromColumn:\s*["\']?(.+?)["\']?\s*$',
                block,
                re.MULTILINE | re.IGNORECASE,
            )
            to_match = re.search(
                r'^\s*toColumn:\s*["\']?(.+?)["\']?\s*$',
                block,
                re.MULTILINE | re.IGNORECASE,
            )
            if not from_match or not to_match:
                continue

            from_table, from_col = parse_column_ref(from_match.group(1))
            to_table, to_col = parse_column_ref(to_match.group(1))
            if from_table and from_col and to_table and to_col:
                relationships.append(
                    {
                        'fromTable': from_table,
                        'fromCol': from_col,
                        'toTable': to_table,
                        'toCol': to_col,
                    }
                )

    unique = []
    seen = set()
    for rel in relationships:
        key = (rel['fromTable'], rel['fromCol'], rel['toTable'], rel['toCol'])
        if key not in seen:
            seen.add(key)
            unique.append(rel)

    print(f'  📄 Relations trouvées : {len(unique)}')
    for rel in unique:
        print(f'    🔗 {rel["fromTable"]}.{rel["fromCol"]} → {rel["toTable"]}.{rel["toCol"]}')

    return unique


# ─── GÉNÉRATEURS MERMAID ───────────────────────────────────────────

def gen_er_diagram(tables: list, relationships: list) -> str:
    """Génère un erDiagram du modèle en étoile."""
    lines = ['erDiagram']

    for t in tables:
        tid = mermaid_id(t["name"])
        lines.append(f'    {tid} {{')

        for col in t['columns'][:8]:
            pk = ' PK' if col['is_key'] else ''
            attr = mermaid_attr(col["name"])
            lines.append(f'        {col["type"]} {attr}{pk}')

        if len(t['columns']) > 8:
            remaining = len(t['columns']) - 8
            lines.append(f'        string __{remaining}_more__')

        lines.append('    }')

    table_names = {t['name'] for t in tables}
    for r in relationships:
        if r['fromTable'] in table_names and r['toTable'] in table_names:
            to_t = mermaid_id(r["toTable"])
            from_t = mermaid_id(r["fromTable"])
            to_c = mermaid_attr(r["toCol"])
            from_c = mermaid_attr(r["fromCol"])
            lines.append(f'    {to_t} ||--o{{ {from_t} : "{to_c} -> {from_c}"')

    return '\n'.join(lines)


def gen_flowchart(tables: list, relationships: list) -> str:
    """Génère un flowchart montrant la structure étoile avec types de tables."""
    lines = ['flowchart TD']

    fact_tables = [t for t in tables if t['is_fact']]
    dim_tables = [t for t in tables if not t['is_fact']]

    lines.append('    subgraph Dims["Dimensions"]')
    for t in dim_tables:
        n_cols = len(t['columns'])
        tid = mermaid_id(t["name"])
        label = t["name"]
        lines.append(f'        {tid}["{label}\n{n_cols} colonnes"]')
    lines.append('    end')

    lines.append('    subgraph Facts["Tables de Faits"]')
    for t in fact_tables:
        n_meas = len(t['measures'])
        tid = mermaid_id(t["name"])
        label = t["name"]
        lines.append(f'        {tid}[/"{label}\n{n_meas} mesures"/]')
    lines.append('    end')

    table_names = {t['name'] for t in tables}
    for r in relationships:
        if r['fromTable'] in table_names and r['toTable'] in table_names:
            to_t = mermaid_id(r["toTable"])
            from_t = mermaid_id(r["fromTable"])
            label = mermaid_attr(r["toCol"])
            lines.append(f'    {to_t} -->|{label}| {from_t}')

    for t in fact_tables:
        tid = mermaid_id(t["name"])
        lines.append(f'    style {tid} fill:#FAEEDA,stroke:#854F0B')
    for t in dim_tables:
        tid = mermaid_id(t["name"])
        lines.append(f'    style {tid} fill:#EBF3FB,stroke:#185FA5')
    lines.append('    style Facts fill:#FBF5E4,stroke:#C9A84C')
    lines.append('    style Dims fill:#E8F0FB,stroke:#1B4F8A')

    return '\n'.join(lines)


def gen_measures_diagram(tables: list) -> str:
    """Génère un classDiagram avec les mesures DAX."""
    if not any(t['measures'] for t in tables):
        return """classDiagram
    class _No_DAX_Measures_ {
        +info Aucune mesure DAX détectée
    }
"""

    lines = ['classDiagram']
    for t in tables:
        if not t['measures']:
            continue

        tid = mermaid_id(t["name"])
        lines.append(f'    class {tid} {{')

        for col in t['columns'][:4]:
            col_id = mermaid_attr(col["name"])
            lines.append(f'        +{col["type"]} {col_id}')

        for m in t['measures']:
            m_id = mermaid_attr(m)
            lines.append(f'        +measure {m_id}()')

        lines.append('    }')
    return '\n'.join(lines)


# ─── ASSEMBLAGE DU FICHIER MARKDOWN ────────────────────────────────

def generate_markdown(tables, relationships, model_name) -> str:
    """Assemble le fichier Markdown complet."""
    er_diagram = gen_er_diagram(tables, relationships)
    flowchart = gen_flowchart(tables, relationships)
    measures = gen_measures_diagram(tables)

    total_columns = sum(len(t['columns']) for t in tables)
    total_measures = sum(len(t['measures']) for t in tables)

    md = f'''<!-- filepath: {OUTPUT_FILE} -->
# Documentation du Modèle — {model_name}

> 🤖 Fichier généré automatiquement par `scripts/generate_mermaid.py`.
> Ne pas modifier manuellement — toute modification sera écrasée.

## Statistiques

| Élément | Nombre |
| --- | --- |
| Tables | {len(tables)} |
| Relations | {len(relationships)} |
| Colonnes | {total_columns} |
| Mesures DAX | {total_measures} |

## Schéma en étoile (erDiagram)

```mermaid
{er_diagram}
```

## Architecture du modèle (flowchart)

```mermaid
{flowchart}
```

## Catalogue des mesures DAX (classDiagram)

```mermaid
{measures}
```
'''
    return md

def main():
    """Charge toutes les tables et génère le Markdown."""
    print('\n🔄 Chargement des tables...')
    tables = []

    if not TABLES_DIR.exists():
        print(f'⚠️  Dossier tables non trouvé : {TABLES_DIR}')
        return

    for tmdl_file in sorted(TABLES_DIR.glob('*.tmdl')):
        table = parse_table(tmdl_file)
        if table and table['name'] not in EXCLUDE_TABLES:
            tables.append(table)

    print(f'\n✅ {len(tables)} tables chargées')

    print('\n🔄 Chargement des relations...')
    relationships = parse_relationships(TMDL_DEFINITION)

    print('\n🔄 Génération du Markdown...')
    model_name = SEMANTIC_MODEL.name.replace('.SemanticModel', '')
    markdown = generate_markdown(tables, relationships, model_name)

    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(markdown, encoding='utf-8')
    print(f'\n✅ Fichier généré : {OUTPUT_FILE}')


# ─── MAIN ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    main()

