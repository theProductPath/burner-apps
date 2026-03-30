#!/usr/bin/env python3
"""
Healthcare Mission App Generator

A burner app for clinical staff to review patient records, appointments,
prescriptions, and flag issues for follow-up.

Usage:
    python generator.py Healthcare_Sample_Data.xlsx healthcare_review.html "Patient Record Review"
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

from generator_base import (
    generate_mission_app,
    read_excel_data,
    SAMPLE_POOLS,
)


# ============== CUSTOMIZE: Configuration ==============

ENTITY_CONFIG = {
    'entities': [
        {
            'name': 'patients',
            'label': 'Patients',
            'sheet': 'Patients',
            'color': '#1565c0',
            'bg_color': '#e3f2fd',
        },
        {
            'name': 'doctors',
            'label': 'Doctors',
            'sheet': 'Doctors',
            'color': '#2e7d32',
            'bg_color': '#e8f5e9',
        },
        {
            'name': 'appointments',
            'label': 'Appointments',
            'sheet': 'Appointments',
            'color': '#7b1fa2',
            'bg_color': '#f3e5f5',
        },
        {
            'name': 'prescriptions',
            'label': 'Prescriptions',
            'sheet': 'Prescriptions',
            'color': '#e65100',
            'bg_color': '#fff3e0',
        },
        {
            'name': 'medical_history',
            'label': 'Medical History',
            'sheet': 'Medical_History',
            'color': '#c62828',
            'bg_color': '#ffebee',
        },
    ],
    'title': 'Healthcare Record Review',
    'heading': 'Patient Records',
    'subtitle': 'Review patient data, appointments, and prescriptions',

    'mission_context': 'Review patient records for completeness and accuracy. Flag any records with missing information, scheduling conflicts, or prescription issues that need follow-up.',

    'welcome_features': [
        {'icon': '🏥', 'title': 'Complete Patient View', 'desc': 'See patients, their appointments, prescriptions, and medical history in one place'},
        {'icon': '🔍', 'title': 'Smart Search', 'desc': 'Find any record by patient name, doctor, medication, or condition'},
        {'icon': '🚩', 'title': 'Flag for Follow-up', 'desc': 'Mark records that need attention and add notes explaining the issue'},
        {'icon': '📋', 'title': 'Export Review', 'desc': 'Generate a report of all flagged items for your team'},
    ],
}

FIELD_CONFIG = {
    'patients': [
        {'field': 'Patient_ID', 'label': 'Patient ID'},
        {'field': 'First_Name', 'label': 'First Name', 'is_title': True, 'combine_with': 'Last_Name'},
        {'field': 'Last_Name', 'label': 'Last Name'},
        {'field': 'Date_of_Birth', 'label': 'DOB'},
        {'field': 'Age', 'label': 'Age'},
        {'field': 'Gender', 'label': 'Gender'},
        {'field': 'Blood_Type', 'label': 'Blood Type'},
        {'field': 'Phone', 'label': 'Phone'},
        {'field': 'Email', 'label': 'Email'},
        {'field': 'Insurance_Provider', 'label': 'Insurance'},
        {'field': 'City', 'label': 'City'},
        {'field': 'State', 'label': 'State'},
    ],
    'doctors': [
        {'field': 'Doctor_ID', 'label': 'Doctor ID'},
        {'field': 'First_Name', 'label': 'First Name', 'is_title': True, 'combine_with': 'Last_Name', 'prefix': 'Title'},
        {'field': 'Last_Name', 'label': 'Last Name'},
        {'field': 'Title', 'label': 'Title'},
        {'field': 'Specialization', 'label': 'Specialization'},
        {'field': 'Department', 'label': 'Department'},
        {'field': 'License_Number', 'label': 'License #'},
        {'field': 'Phone', 'label': 'Phone'},
        {'field': 'Office_Location', 'label': 'Office'},
        {'field': 'Years_Experience', 'label': 'Experience'},
    ],
    'appointments': [
        {'field': 'Appointment_ID', 'label': 'Appt ID'},
        {'field': 'Patient_ID', 'label': 'Patient', 'is_title': True},
        {'field': 'Doctor_ID', 'label': 'Doctor'},
        {'field': 'Appointment_Date', 'label': 'Date'},
        {'field': 'Appointment_Time', 'label': 'Time'},
        {'field': 'Type', 'label': 'Type'},
        {'field': 'Status', 'label': 'Status'},
        {'field': 'Duration_Minutes', 'label': 'Duration'},
        {'field': 'Reason', 'label': 'Reason'},
        {'field': 'Notes', 'label': 'Notes'},
    ],
    'prescriptions': [
        {'field': 'Prescription_ID', 'label': 'Rx ID'},
        {'field': 'Medication_Name', 'label': 'Medication', 'is_title': True},
        {'field': 'Patient_ID', 'label': 'Patient'},
        {'field': 'Doctor_ID', 'label': 'Prescriber'},
        {'field': 'Dosage', 'label': 'Dosage'},
        {'field': 'Frequency', 'label': 'Frequency'},
        {'field': 'Quantity', 'label': 'Qty'},
        {'field': 'Refills_Allowed', 'label': 'Refills'},
        {'field': 'Start_Date', 'label': 'Start'},
        {'field': 'End_Date', 'label': 'End'},
        {'field': 'Status', 'label': 'Status'},
    ],
    'medical_history': [
        {'field': 'Record_ID', 'label': 'Record ID'},
        {'field': 'Patient_ID', 'label': 'Patient', 'is_title': True},
        {'field': 'Condition', 'label': 'Condition'},
        {'field': 'Diagnosis_Date', 'label': 'Diagnosed'},
        {'field': 'Status', 'label': 'Status'},
        {'field': 'Severity', 'label': 'Severity'},
        {'field': 'Notes', 'label': 'Notes'},
    ],
}

# Relationships allow cross-referencing (optional enhancement)
RELATIONSHIPS = [
    {'from': 'appointments', 'to': 'patients', 'via': 'Patient_ID', 'match': 'Patient_ID'},
    {'from': 'appointments', 'to': 'doctors', 'via': 'Doctor_ID', 'match': 'Doctor_ID'},
    {'from': 'prescriptions', 'to': 'patients', 'via': 'Patient_ID', 'match': 'Patient_ID'},
    {'from': 'prescriptions', 'to': 'doctors', 'via': 'Doctor_ID', 'match': 'Doctor_ID'},
    {'from': 'medical_history', 'to': 'patients', 'via': 'Patient_ID', 'match': 'Patient_ID'},
]

# ============== END CUSTOMIZE: Configuration ==============


# ============== Render Functions Generator ==============

def generate_render_functions():
    """Generate JavaScript render functions based on FIELD_CONFIG"""

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
        singular = label.rstrip('s') if not label.endswith('ry') else label  # Handle "History"
        fields = FIELD_CONFIG.get(name, [])

        # Find title field and check for combine_with
        title_field = next((f['field'] for f in fields if f.get('is_title')), 'Name')
        title_config = next((f for f in fields if f.get('is_title')), {})
        combine_field = title_config.get('combine_with')
        prefix_field = title_config.get('prefix')

        # Build title expression
        if prefix_field and combine_field:
            title_expr = f"(item['{prefix_field}'] || '') + ' ' + (item['{title_field}'] || '') + ' ' + (item['{combine_field}'] || '')"
        elif combine_field:
            title_expr = f"(item['{title_field}'] || '') + ' ' + (item['{combine_field}'] || '')"
        else:
            title_expr = f"item['{title_field}'] || 'Unknown {singular}'"

        # Build detail items
        detail_items = []
        skip_fields = {title_field, combine_field, prefix_field} if combine_field else {title_field}

        for f in fields:
            if f['field'] in skip_fields:
                continue
            field_name = f['field']
            field_label = f['label']

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
    const name = ({title_expr}).trim();
    const recordId = '{name}-' + (item['ID'] || item['{title_field}'] || Math.random()).toString().replace(/[^a-z0-9]/gi, '_');
    recordLookup[recordId] = item;
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
               placeholder="What's the issue with this record? (optional)"
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

    all_results_lines = []
    for name in entity_names:
        all_results_lines.append(
            f"    allResults = allResults.concat(data.{name.replace('-', '_')}.map(item => ({{ type: '{name}', data: item }})));"
        )

    filter_lines = []
    for name in entity_names:
        filter_lines.append(
            f"    if (currentFilter === 'all' || currentFilter === '{name}') "
            f"results = results.concat(filtered.filter(item => item.type === '{name}'));"
        )

    count_updates = []
    for name in entity_names:
        safe_name = name.replace('-', '_')
        count_updates.append(
            f"    const {safe_name}Filtered = filtered.filter(item => item.type === '{name}').length;\n"
            f"    document.getElementById('{name}Count').textContent = "
            f"{safe_name}Filtered + ' of ' + totals.{safe_name};"
        )

    display_lines = []
    for name in entity_names:
        display_lines.append(f"        if (item.type === '{name}') return render_{name.replace('-', '_')}(item.data);")

    total_lines = []
    for entity in ENTITY_CONFIG['entities']:
        name = entity['name']
        safe_name = name.replace('-', '_')
        total_lines.append(f"    {safe_name}: data.{safe_name}.length,")

    init_lines = []
    for entity in ENTITY_CONFIG['entities']:
        name = entity['name']
        safe_name = name.replace('-', '_')
        init_lines.append(f"    document.getElementById('{name}Count').textContent = data.{safe_name}.length + ' of ' + data.{safe_name}.length;")

    return f"""
const totals = {{
{chr(10).join(total_lines)}
}};

function updateStats() {{
{chr(10).join(init_lines)}
}}

let currentQuery = '';

function getSearchableText(obj) {{
    return Object.values(obj).map(v => String(v || '')).join(' ').toLowerCase();
}}

function performSearch() {{
    currentQuery = searchInput.value.toLowerCase().trim();

    let allResults = [];
{chr(10).join(all_results_lines)}

    const filtered = currentQuery
        ? allResults.filter(item => getSearchableText(item.data).includes(currentQuery))
        : allResults;

{chr(10).join(count_updates)}

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
    """Analyze a list of values to determine the field type"""
    if not values:
        return {'type': 'string', 'pattern': 'generic'}

    sample = values[:50] if len(values) > 50 else values
    non_null = [v for v in sample if v is not None and str(v).strip()]

    if not non_null:
        return {'type': 'string', 'pattern': 'generic'}

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

        if avg_val > 1000:
            return {'type': 'number', 'pattern': 'currency', 'min': min_val, 'max': max_val}
        elif 0 <= min_val and max_val <= 100:
            return {'type': 'number', 'pattern': 'percent', 'min': min_val, 'max': max_val}
        elif all(v == int(v) for v in numeric_values):
            return {'type': 'number', 'pattern': 'id', 'min': int(min_val), 'max': int(max_val)}
        else:
            return {'type': 'number', 'pattern': 'decimal', 'min': min_val, 'max': max_val}

    str_values = [str(v) for v in non_null]

    if any(all(p in s for p in ['-']) and len(s) == 10 for s in str_values[:5]):
        return {'type': 'date', 'pattern': 'iso'}

    if any('@' in s and '.' in s for s in str_values[:5]):
        return {'type': 'string', 'pattern': 'email'}

    if any(s.replace('(', '').replace(')', '').replace('-', '').replace(' ', '').isdigit()
           and len(s) >= 10 for s in str_values[:5]):
        return {'type': 'string', 'pattern': 'phone'}

    if any('-' in s and any(c.isdigit() for c in s) for s in str_values[:5]):
        prefixes = set()
        for s in str_values:
            if '-' in s:
                prefixes.add(s.split('-')[0])
        if len(prefixes) == 1:
            return {'type': 'string', 'pattern': 'prefixed_id', 'prefix': list(prefixes)[0]}

    unique_values = list(set(str_values))
    if len(unique_values) <= 10:
        return {'type': 'string', 'pattern': 'enum', 'values': unique_values}

    if all(s.istitle() or ' ' in s for s in str_values[:5]):
        avg_words = sum(len(s.split()) for s in str_values) / len(str_values)
        if avg_words <= 3:
            return {'type': 'string', 'pattern': 'name'}

    return {'type': 'string', 'pattern': 'generic', 'sample': str_values[:5]}


def generate_synthetic_value(field_name, field_info, index):
    """Generate a synthetic value based on field analysis"""
    pattern = field_info.get('pattern', 'generic')
    field_lower = field_name.lower()

    # Field name hints
    if 'first' in field_lower and 'name' in field_lower:
        return random.choice(SAMPLE_POOLS['first_names'])
    if 'last' in field_lower and 'name' in field_lower:
        return random.choice(SAMPLE_POOLS['last_names'])
    if field_lower in ['name', 'contact_name', 'full_name']:
        return f"{random.choice(SAMPLE_POOLS['first_names'])} {random.choice(SAMPLE_POOLS['last_names'])}"
    if 'city' in field_lower:
        return random.choice(SAMPLE_POOLS['cities'])
    if 'state' in field_lower:
        return random.choice(SAMPLE_POOLS['states'])
    if 'zip' in field_lower:
        return str(random.randint(10000, 99999))

    # Pattern-based generation
    if pattern == 'prefixed_id':
        prefix = field_info.get('prefix', 'ID')
        return f"{prefix}-{str(index + 1).zfill(6)}"
    elif pattern == 'id':
        return index + 1
    elif pattern == 'email':
        first = random.choice(SAMPLE_POOLS['first_names']).lower()
        last = random.choice(SAMPLE_POOLS['last_names']).lower()
        domain = random.choice(['example.com', 'sample.org', 'test.net'])
        return f"{first}.{last}@{domain}"
    elif pattern == 'phone':
        return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
    elif pattern == 'date' or pattern == 'iso':
        days_ago = random.randint(0, 365)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime('%Y-%m-%d')
    elif pattern == 'enum':
        return random.choice(field_info.get('values', ['Value A', 'Value B']))
    elif pattern == 'name':
        return f"{random.choice(SAMPLE_POOLS['first_names'])} {random.choice(SAMPLE_POOLS['last_names'])}"
    else:
        return f"Sample {field_name} {index + 1}"


def generate_sample_data(real_data, num_records=7):
    """Generate synthetic sample data based on real data schema"""
    sample_data = {}

    for entity_name, records in real_data.items():
        if not records:
            sample_data[entity_name] = []
            continue

        field_info = {}
        all_fields = set()
        for record in records:
            all_fields.update(record.keys())

        for field in all_fields:
            values = [r.get(field) for r in records if field in r]
            field_info[field] = analyze_field_type(values)

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
        default_title='Healthcare Review'
    )
