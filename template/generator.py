#!/usr/bin/env python3
"""
Mission App Generator - Starter Template

Copy this file to your mission folder and customize the marked sections.

Usage:
    python generator.py input.xlsx output.html "Title"

Customization zones are marked with:
    # ============== CUSTOMIZE: Section Name ==============
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# Import shared functionality from base module
from generator_base import (
    generate_mission_app,
    read_excel_data,
    SAMPLE_POOLS,
)


# ============== CUSTOMIZE: Configuration ==============
# Define your entity types and their display settings

ENTITY_CONFIG = {
    'entities': [
        {
            'name': 'items',           # Internal name (lowercase, plural)
            'label': 'Items',          # Display label
            'sheet': 'Items',          # Excel sheet name
            'color': '#1976d2',        # Badge text color
            'bg_color': '#e3f2fd',     # Badge background color
        },
        # Add more entities as needed:
        # {
        #     'name': 'categories',
        #     'label': 'Categories',
        #     'sheet': 'Categories',
        #     'color': '#7b1fa2',
        #     'bg_color': '#f3e5f5',
        # },
    ],
    'title': 'Data Review Tool',
    'heading': 'Data Review',
    'subtitle': 'Search and explore your data',

    # Mission context - customize this for each mission
    'mission_context': 'Your goal is to review this data for accuracy and completeness. Flag any issues you find, add notes to explain the problem, then export your feedback when done.',

    # Welcome modal content - customize the features list for each mission
    'welcome_features': [
        {'icon': '🎯', 'title': 'Built for Right Now', 'desc': 'Pre-loaded with your current data snapshot - no login, no setup, just open and explore'},
        {'icon': '🔍', 'title': 'Search & Explore', 'desc': 'Find any record instantly by searching across all fields'},
        {'icon': '🚩', 'title': 'Flag Issues', 'desc': 'Spot something wrong? Flag it and add a note explaining the problem'},
        {'icon': '📤', 'title': 'Export Feedback', 'desc': 'When done, export your flagged records to share with the team'},
    ],
}

# Define which fields to display for each entity type
# 'field' = column name in data, 'label' = display label
FIELD_CONFIG = {
    'items': [
        {'field': 'Name', 'label': 'Name', 'is_title': True},
        {'field': 'Description', 'label': 'Description'},
        {'field': 'Category', 'label': 'Category'},
        {'field': 'Status', 'label': 'Status'},
    ],
    # Add field configs for other entities
}

# Define relationships between entities (optional)
# Example: {'from': 'items', 'to': 'categories', 'via': 'Category_ID', 'match': 'ID'}
RELATIONSHIPS = []

# ============== END CUSTOMIZE: Configuration ==============


# ============== Render Functions Generator ==============
# Auto-generates render functions from FIELD_CONFIG

def generate_render_functions():
    """Generate JavaScript render functions based on FIELD_CONFIG with highlighting"""

    # Helper functions included in output
    helpers = """
function formatCurrency(value) {
    if (!value && value !== 0) return '';
    const num = typeof value === 'number' ? value : parseFloat(value);
    if (isNaN(num)) return esc(String(value));
    return '$' + num.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0});
}

function formatPercent(value) {
    if (!value && value !== 0) return '';
    const num = typeof value === 'number' ? value : parseFloat(value);
    if (isNaN(num)) return esc(String(value));
    return num + '%';
}
"""

    functions = [helpers]

    for entity in ENTITY_CONFIG['entities']:
        name = entity['name']
        label = entity['label']
        singular = label.rstrip('s')  # Simple singularization
        fields = FIELD_CONFIG.get(name, [])

        # Find title field
        title_field = next((f['field'] for f in fields if f.get('is_title')), 'Name')

        # Build detail items with highlighting
        detail_items = []
        for f in fields:
            if f.get('is_title'):
                continue
            field_name = f['field']
            field_label = f['label']
            # Use appropriate formatter
            if f.get('format') == 'currency':
                value_expr = f"formatCurrency(item['{field_name}'])"
            elif f.get('format') == 'percent':
                value_expr = f"formatPercent(item['{field_name}'])"
            else:
                value_expr = f"highlight(item['{field_name}'])"

            detail_items.append(
                f"            ${{item['{field_name}'] ? `<div class=\"detail-item\">"
                f"<div class=\"detail-label\">{field_label}</div>"
                f"<div class=\"detail-value\">${{{value_expr}}}</div></div>` : ''}}"
            )

        func = rf"""
function render_{name.replace('-', '_')}(item) {{
    const name = item['{title_field}'] || 'Unknown {singular}';
    const recordId = '{name}-' + (item['ID'] || item['{title_field}'] || Math.random()).toString().replace(/[^a-z0-9]/gi, '_');
    recordLookup[recordId] = item;  // Store for export
    const isFlagged = flaggedRecords.some(f => f.id === recordId);
    const flaggedRec = flaggedRecords.find(f => f.id === recordId);

    return `<div class="result-item ${{isFlagged ? 'flagged' : ''}}">
        <div class="result-header">
            <div>
                <div class="result-title">${{highlight(name)}}</div>
                <span class="result-type" style="background: {entity['bg_color']}; color: {entity['color']}">{singular}</span>
            </div>
            <button class="flag-btn ${{isFlagged ? 'flagged' : ''}}" onclick="toggleFlag('${{recordId}}', '{singular}', \`${{esc(name)}}\`)">
                ${{isFlagged ? '🚩 Flagged' : '🏴 Flag Issue'}}
            </button>
        </div>
        <input type="text" class="flag-note-input ${{isFlagged ? 'active' : ''}}"
               placeholder="What's wrong with this record? (optional)"
               value="${{flaggedRec ? esc(flaggedRec.note) : ''}}"
               onchange="updateFlagNote('${{recordId}}', this.value)">
        <div class="result-details">
{chr(10).join(detail_items)}
        </div>
    </div>`;
}}
"""
        functions.append(func)

    return '\n'.join(functions)


def generate_search_function():
    """Generate the performSearch function based on entity config"""
    entity_names = [e['name'] for e in ENTITY_CONFIG['entities']]

    # Build results aggregation (always get all, then filter)
    all_results_lines = []
    for name in entity_names:
        all_results_lines.append(
            f"    allResults = allResults.concat(data.{name}.map(item => ({{ type: '{name}', data: item }})));"
        )

    # Build filtered results based on current filter
    filter_lines = []
    for name in entity_names:
        filter_lines.append(
            f"    if (currentFilter === 'all' || currentFilter === '{name}') "
            f"results = results.concat(filtered.filter(item => item.type === '{name}'));"
        )

    # Build count updates for each entity
    count_updates = []
    for name in entity_names:
        count_updates.append(
            f"    const {name}Filtered = filtered.filter(item => item.type === '{name}').length;\n"
            f"    document.getElementById('{name}Count').textContent = "
            f"{name}Filtered + ' of ' + totals.{name};"
        )

    # Build display routing
    display_lines = []
    for name in entity_names:
        display_lines.append(f"        if (item.type === '{name}') return render_{name.replace('-', '_')}(item.data);")

    # Build totals and updateStats
    total_lines = []
    for entity in ENTITY_CONFIG['entities']:
        name = entity['name']
        total_lines.append(f"    {name}: data.{name}.length,")

    init_lines = []
    for entity in ENTITY_CONFIG['entities']:
        name = entity['name']
        init_lines.append(f"    document.getElementById('{name}Count').textContent = data.{name}.length + ' of ' + data.{name}.length;")

    return f"""
const totals = {{
{chr(10).join(total_lines)}
}};

function updateStats() {{
{chr(10).join(init_lines)}
}}

let currentQuery = '';

function getSearchableText(obj) {{
    // Only search field VALUES, not keys
    return Object.values(obj).map(v => String(v || '')).join(' ').toLowerCase();
}}

function performSearch() {{
    currentQuery = searchInput.value.toLowerCase().trim();

    // Get all results first
    let allResults = [];
{chr(10).join(all_results_lines)}

    // Filter by search query (values only, not field names)
    const filtered = currentQuery
        ? allResults.filter(item => getSearchableText(item.data).includes(currentQuery))
        : allResults;

    // Update entity counts (filtered of total)
{chr(10).join(count_updates)}

    // Apply type filter for display
    let results = [];
{chr(10).join(filter_lines)}

    document.getElementById('resultCount').textContent = results.length;
    displayResults(results);
}}

function displayResults(results) {{
    const container = document.getElementById('resultsContainer');
    if (results.length === 0) {{
        container.innerHTML = '<div class="no-results"><div class="no-results-icon">🔍</div><div>No results found.</div></div>';
        return;
    }}
    container.innerHTML = results.map(item => {{
{chr(10).join(display_lines)}
        return '';
    }}).join('');
}}
"""

# ============== END Render Functions Generator ==============


# ============== Synthetic Data Generation ==============

def analyze_field_type(values):
    """Analyze a list of values to determine the field type and characteristics"""
    if not values:
        return {'type': 'string', 'pattern': 'generic'}

    # Sample up to 50 values for analysis
    sample = values[:50] if len(values) > 50 else values
    non_null = [v for v in sample if v is not None and str(v).strip()]

    if not non_null:
        return {'type': 'string', 'pattern': 'generic'}

    # Check if all numeric
    numeric_count = 0
    numeric_values = []
    for v in non_null:
        try:
            numeric_values.append(float(v))
            numeric_count += 1
        except (ValueError, TypeError):
            pass

    if numeric_count == len(non_null) and numeric_values:
        min_val = min(numeric_values)
        max_val = max(numeric_values)
        avg_val = sum(numeric_values) / len(numeric_values)

        # Detect currency (large numbers, often round)
        if avg_val > 1000:
            return {'type': 'number', 'pattern': 'currency', 'min': min_val, 'max': max_val}
        # Detect percentages (0-100)
        elif 0 <= min_val and max_val <= 100:
            return {'type': 'number', 'pattern': 'percent', 'min': min_val, 'max': max_val}
        # Detect IDs (sequential integers)
        elif all(v == int(v) for v in numeric_values):
            return {'type': 'number', 'pattern': 'id', 'min': int(min_val), 'max': int(max_val)}
        else:
            return {'type': 'number', 'pattern': 'decimal', 'min': min_val, 'max': max_val}

    # String analysis
    str_values = [str(v) for v in non_null]

    # Check for dates
    if any(all(p in s for p in ['-']) and len(s) == 10 for s in str_values[:5]):
        return {'type': 'date', 'pattern': 'iso'}

    # Check for emails
    if any('@' in s and '.' in s for s in str_values[:5]):
        return {'type': 'string', 'pattern': 'email'}

    # Check for phone numbers
    if any(s.replace('(', '').replace(')', '').replace('-', '').replace(' ', '').isdigit()
           and len(s) >= 10 for s in str_values[:5]):
        return {'type': 'string', 'pattern': 'phone'}

    # Check for URLs
    if any(s.startswith(('http://', 'https://', 'www.')) for s in str_values[:5]):
        return {'type': 'string', 'pattern': 'url'}

    # Check if it's an ID field (like ACC-00001)
    if any('-' in s and any(c.isdigit() for c in s) for s in str_values[:5]):
        prefixes = set()
        for s in str_values:
            if '-' in s:
                prefixes.add(s.split('-')[0])
        if len(prefixes) == 1:
            return {'type': 'string', 'pattern': 'prefixed_id', 'prefix': list(prefixes)[0]}

    # Check for limited set of values (enum-like)
    unique_values = list(set(str_values))
    if len(unique_values) <= 10:
        return {'type': 'string', 'pattern': 'enum', 'values': unique_values}

    # Check for names (title case, 1-3 words)
    if all(s.istitle() or ' ' in s for s in str_values[:5]):
        avg_words = sum(len(s.split()) for s in str_values) / len(str_values)
        if avg_words <= 3:
            return {'type': 'string', 'pattern': 'name'}
        else:
            return {'type': 'string', 'pattern': 'company'}

    return {'type': 'string', 'pattern': 'generic', 'sample': str_values[:5]}


def generate_synthetic_value(field_name, field_info, index):
    """Generate a synthetic value based on field analysis"""
    pattern = field_info.get('pattern', 'generic')
    field_lower = field_name.lower()

    # Use field name hints first
    if 'first' in field_lower and 'name' in field_lower:
        return random.choice(SAMPLE_POOLS['first_names'])
    if 'last' in field_lower and 'name' in field_lower:
        return random.choice(SAMPLE_POOLS['last_names'])
    if field_lower in ['name', 'contact_name', 'full_name']:
        return f"{random.choice(SAMPLE_POOLS['first_names'])} {random.choice(SAMPLE_POOLS['last_names'])}"
    if 'company' in field_lower or 'account' in field_lower and 'name' in field_lower:
        return random.choice(SAMPLE_POOLS['companies'])
    if 'street' in field_lower or 'address' in field_lower:
        return f"{random.randint(100, 9999)} {random.choice(SAMPLE_POOLS['streets'])}"
    if 'city' in field_lower:
        return random.choice(SAMPLE_POOLS['cities'])
    if 'state' in field_lower:
        return random.choice(SAMPLE_POOLS['states'])
    if 'zip' in field_lower or 'postal' in field_lower:
        return str(random.randint(10000, 99999))
    if 'industry' in field_lower:
        return random.choice(SAMPLE_POOLS['industries'])
    if 'status' in field_lower:
        return random.choice(SAMPLE_POOLS['statuses'])

    # Fall back to pattern-based generation
    if pattern == 'prefixed_id':
        prefix = field_info.get('prefix', 'ID')
        return f"{prefix}-{str(index + 1).zfill(5)}"
    elif pattern == 'id':
        return index + 1
    elif pattern == 'currency':
        min_val = field_info.get('min', 1000)
        max_val = field_info.get('max', 1000000)
        return round(random.uniform(min_val, max_val), 0)
    elif pattern == 'percent':
        return random.randint(0, 100)
    elif pattern == 'decimal':
        min_val = field_info.get('min', 0)
        max_val = field_info.get('max', 100)
        return round(random.uniform(min_val, max_val), 2)
    elif pattern == 'email':
        first = random.choice(SAMPLE_POOLS['first_names']).lower()
        last = random.choice(SAMPLE_POOLS['last_names']).lower()
        domain = random.choice(['example.com', 'sample.org', 'test.net', 'demo.io'])
        return f"{first}.{last}@{domain}"
    elif pattern == 'phone':
        return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
    elif pattern == 'url':
        company = random.choice(SAMPLE_POOLS['companies']).lower().replace(' ', '').replace('.', '')
        return f"www.{company}.com"
    elif pattern == 'date' or pattern == 'iso':
        days_ago = random.randint(0, 365)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime('%Y-%m-%d')
    elif pattern == 'enum':
        return random.choice(field_info.get('values', ['Value A', 'Value B']))
    elif pattern == 'name':
        return f"{random.choice(SAMPLE_POOLS['first_names'])} {random.choice(SAMPLE_POOLS['last_names'])}"
    elif pattern == 'company':
        return random.choice(SAMPLE_POOLS['companies'])
    else:
        # Generic string
        return f"Sample {field_name} {index + 1}"


def generate_sample_data(real_data, num_records=7):
    """Generate synthetic sample data based on real data schema"""
    sample_data = {}

    for entity_name, records in real_data.items():
        if not records:
            sample_data[entity_name] = []
            continue

        # Analyze each field
        field_info = {}
        all_fields = set()
        for record in records:
            all_fields.update(record.keys())

        for field in all_fields:
            values = [r.get(field) for r in records if field in r]
            field_info[field] = analyze_field_type(values)

        # Generate sample records
        sample_records = []
        for i in range(num_records):
            record = {}
            for field in all_fields:
                record[field] = generate_synthetic_value(field, field_info[field], i)
            sample_records.append(record)

        sample_data[entity_name] = sample_records

    return sample_data

# ============== END Synthetic Data Generation ==============


if __name__ == '__main__':
    generate_mission_app(
        entity_config=ENTITY_CONFIG,
        field_config=FIELD_CONFIG,
        render_functions=generate_render_functions(),
        search_function=generate_search_function(),
        generate_sample_data_fn=generate_sample_data,
        default_title='Data Review'
    )
