#!/usr/bin/env python3
"""
Process Report - General Purpose Mission App Report Processor

This script processes flagged records reports from any Mission App.
It verifies integrity, displays session analytics, and summarizes flagged records.

Usage:
    python process_report.py <report.md> [options]

Options:
    --coordinator    Generate simplified report for Coordinator (action-focused)
    --creator        Generate full detailed report for Creator (default)
    -o, --output     Specify output filename (default: auto-generated)

Examples:
    python process_report.py flagged_records_2026-01-17.md
    python process_report.py flagged_records_2026-01-17.md --coordinator
    python process_report.py flagged_records_2026-01-17.md --creator -o my_report.md

The script will:
1. Extract JSON data from the markdown report
2. Find the matching manifest file by mission_id
3. Verify integrity (fingerprints match)
4. Generate a processed report in markdown format
"""

import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime


# ============== Report Parsing ==============

def extract_json_from_report(report_path):
    """Extract the JSON block from a markdown report"""
    report_text = Path(report_path).read_text(encoding='utf-8')

    # Find JSON code block
    json_match = re.search(r'```json\n(.*?)\n```', report_text, re.DOTALL)
    if not json_match:
        return None, "No JSON block found in report"

    try:
        return json.loads(json_match.group(1)), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in report: {e}"


def find_manifest(mission_id, search_dirs=None):
    """Find manifest file matching the mission ID"""
    if search_dirs is None:
        search_dirs = ['.']

    for search_dir in search_dirs:
        search_path = Path(search_dir)
        if not search_path.exists():
            continue

        # Look for manifest files
        for manifest_path in search_path.glob('*.manifest.json'):
            try:
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                if manifest.get('mission_id') == mission_id:
                    return manifest, manifest_path
            except:
                continue

    return None, None


# ============== Integrity Verification ==============

def verify_integrity(report_data, manifest):
    """Verify report fingerprints against manifest"""
    checks = []

    # Mission ID
    report_mid = report_data.get('mission_id', '')
    manifest_mid = manifest.get('mission_id', '')
    checks.append({
        'field': 'Mission ID',
        'report': report_mid,
        'manifest': manifest_mid,
        'match': report_mid == manifest_mid
    })

    # App Fingerprint
    report_app = report_data.get('app_fingerprint', '')
    manifest_app = manifest.get('app_fingerprint', '')
    checks.append({
        'field': 'App Fingerprint',
        'report': report_app,
        'manifest': manifest_app,
        'match': report_app == manifest_app
    })

    # Data Fingerprint
    report_data_fp = report_data.get('data_fingerprint', '')
    manifest_data_fp = manifest.get('data_fingerprint', '')
    checks.append({
        'field': 'Data Fingerprint',
        'report': report_data_fp,
        'manifest': manifest_data_fp,
        'match': report_data_fp == manifest_data_fp
    })

    all_passed = all(c['match'] for c in checks)
    return checks, all_passed


# ============== Markdown Generation - Creator Mode ==============

def generate_creator_report(report_data, manifest, manifest_path, checks, all_passed):
    """Generate full detailed report for Creator"""
    md = []

    # Header
    mission_name = report_data.get('mission', 'Unknown Mission')
    md.append(f"# Mission Report: {mission_name}")
    md.append("")
    md.append(f"**Report Type:** Creator (Full Detail)  ")
    md.append(f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    md.append(f"**Source Report Generated:** {report_data.get('generated', 'Unknown')}  ")
    md.append(f"**Records Flagged:** {len(report_data.get('flagged', []))}")
    md.append("")

    # Integrity Verification Section
    md.append("---")
    md.append("")
    md.append("## Integrity Verification")
    md.append("")

    if manifest:
        md.append(f"**Matched Manifest:** `{manifest_path}`  ")
        md.append(f"**App Generated:** {manifest.get('generated', 'Unknown')}  ")
        if manifest.get('input_file'):
            md.append(f"**Source Data:** `{manifest.get('input_file')}`")
        md.append("")

        # Integrity check table
        md.append("| Check | Report Value | Manifest Value | Status |")
        md.append("|-------|--------------|----------------|--------|")
        for check in checks:
            status = "✅ PASS" if check['match'] else "❌ FAIL"
            md.append(f"| {check['field']} | `{check['report']}` | `{check['manifest']}` | {status} |")
        md.append("")

        if all_passed:
            md.append("> ✅ **INTEGRITY VERIFIED** - Report matches source Mission App")
        else:
            md.append("> ⚠️ **INTEGRITY FAILURE** - Report may have been tampered with")
        md.append("")
    else:
        md.append("> ⚠️ No manifest found - integrity verification skipped")
        md.append("")

    # Session Analytics Section
    analytics = report_data.get('analytics')
    if analytics:
        md.append("---")
        md.append("")
        md.append("## Session Analytics")
        md.append("")

        start = analytics.get('session_start', 'Unknown')
        end = analytics.get('session_end', 'Unknown')
        duration = analytics.get('session_duration_minutes', 'Unknown')

        md.append(f"**Session Start:** {start}  ")
        md.append(f"**Session End:** {end}  ")
        md.append(f"**Duration:** {duration} minutes")
        md.append("")

        # Activity summary table
        searches = analytics.get('searches', [])
        filters = analytics.get('filters', [])
        navigation = analytics.get('navigation', [])
        flags = analytics.get('flags', [])

        md.append("### Activity Summary")
        md.append("")
        md.append("| Activity | Count |")
        md.append("|----------|-------|")
        md.append(f"| Searches | {len(searches)} |")
        md.append(f"| Filter Changes | {len(filters)} |")
        md.append(f"| Navigation Clicks | {len(navigation)} |")
        md.append(f"| Flag/Unflag Actions | {len(flags)} |")
        md.append("")

        # Search details
        if searches:
            md.append("### Search Queries")
            md.append("")
            for s in searches:
                md.append(f"- \"{s.get('query', '')}\" → {s.get('resultCount', 0)} results")
            md.append("")

        # Filter details
        if filters:
            md.append("### Filters Applied")
            md.append("")
            for f in filters:
                md.append(f"- {f.get('filter', 'Unknown')}")
            md.append("")

        # Navigation details
        if navigation:
            md.append("### Navigation")
            md.append("")
            for n in navigation:
                md.append(f"- Jumped to: {n.get('to', 'Unknown')} ({n.get('filterType', '')})")
            md.append("")

        # Flag timeline
        if flags:
            md.append("### Flag Timeline")
            md.append("")
            md.append("| Time | Action | Record Type |")
            md.append("|------|--------|-------------|")
            for f in flags:
                action = f.get('action', 'flag')
                record_type = f.get('recordType', 'Record')
                timestamp = f.get('timestamp', '')
                if 'T' in timestamp:
                    time_part = timestamp.split('T')[1][:8]
                else:
                    time_part = timestamp
                md.append(f"| {time_part} | {action} | {record_type} |")
            md.append("")

    # Flagged Records Section
    flagged_records = report_data.get('flagged', [])
    if flagged_records:
        md.append("---")
        md.append("")
        md.append("## Flagged Records")
        md.append("")

        # Group by type
        by_type = {}
        for record in flagged_records:
            record_type = record.get('type', 'Unknown')
            if record_type not in by_type:
                by_type[record_type] = []
            by_type[record_type].append(record)

        md.append(f"**Total:** {len(flagged_records)} records flagged")
        md.append("")
        for record_type, records in by_type.items():
            md.append(f"- {record_type}: {len(records)}")
        md.append("")

        # List each record with full data
        for i, record in enumerate(flagged_records, 1):
            md.append(f"### {i}. [{record.get('type', 'Unknown')}] {record.get('title', 'Unknown')}")
            md.append("")
            md.append(f"**Issue:** {record.get('note', 'No note provided')}")
            md.append("")

            # Full data table
            data = record.get('data', {})
            if data:
                md.append("| Field | Value |")
                md.append("|-------|-------|")
                for key, value in data.items():
                    str_value = str(value) if value is not None else ''
                    # Escape pipe characters for markdown table
                    str_value = str_value.replace('|', '\\|')
                    md.append(f"| {key} | {str_value} |")
                md.append("")

        # Recommended Actions
        md.append("---")
        md.append("")
        md.append("## Recommended Actions")
        md.append("")

        for i, record in enumerate(flagged_records, 1):
            note = record.get('note', '')
            record_type = record.get('type', 'Record')
            title = record.get('title', 'Unknown')

            md.append(f"### {i}. {record_type}: {title}")
            md.append("")
            md.append(f"**Issue:** \"{note}\"")
            md.append("")

            # Action suggestion
            note_lower = note.lower()
            if any(word in note_lower for word in ['wrong', 'incorrect', 'error', 'mistake']):
                md.append("→ Verify data accuracy in source system")
            elif any(word in note_lower for word in ['duplicate', 'dup', 'already']):
                md.append("→ Check for duplicate records, consider merging")
            elif any(word in note_lower for word in ['missing', 'empty', 'blank', 'null']):
                md.append("→ Investigate missing data, update source if available")
            elif any(word in note_lower for word in ['old', 'outdated', 'stale', 'expired']):
                md.append("→ Review for potential removal or update")
            elif any(word in note_lower for word in ['?', 'why', 'unclear', 'confused']):
                md.append("→ Clarify with data owner or stakeholder")
            else:
                md.append("→ Review and resolve as appropriate")
            md.append("")
    else:
        md.append("---")
        md.append("")
        md.append("## Flagged Records")
        md.append("")
        md.append("*No flagged records in this report.*")
        md.append("")

    # Footer
    md.append("---")
    md.append("")
    md.append("*Report generated by Mission Apps Report Processor*")

    return '\n'.join(md)


# ============== Markdown Generation - Coordinator Mode ==============

def generate_coordinator_report(report_data, manifest, manifest_path, checks, all_passed):
    """Generate simplified action-focused report for Coordinator"""
    md = []

    # Header
    mission_name = report_data.get('mission', 'Unknown Mission')
    md.append(f"# Action Items: {mission_name}")
    md.append("")
    md.append(f"**Report Type:** Coordinator (Action-Focused)  ")
    md.append(f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    md.append(f"**Records to Review:** {len(report_data.get('flagged', []))}")
    md.append("")

    # Quick integrity status (one line)
    if all_passed is True:
        md.append("> ✅ Report integrity verified")
    elif all_passed is False:
        md.append("> ⚠️ **Warning:** Report integrity check failed - verify with Creator")
    else:
        md.append("> ℹ️ Integrity verification not available")
    md.append("")

    # Flagged Records - Action-focused format
    flagged_records = report_data.get('flagged', [])
    if flagged_records:
        md.append("---")
        md.append("")
        md.append("## Items Requiring Action")
        md.append("")

        # Summary by type
        by_type = {}
        for record in flagged_records:
            record_type = record.get('type', 'Unknown')
            if record_type not in by_type:
                by_type[record_type] = []
            by_type[record_type].append(record)

        md.append("### Summary")
        md.append("")
        md.append("| Type | Count |")
        md.append("|------|-------|")
        for record_type, records in by_type.items():
            md.append(f"| {record_type} | {len(records)} |")
        md.append(f"| **Total** | **{len(flagged_records)}** |")
        md.append("")

        # Action checklist
        md.append("### Action Checklist")
        md.append("")

        for i, record in enumerate(flagged_records, 1):
            note = record.get('note', 'No note provided')
            record_type = record.get('type', 'Record')
            title = record.get('title', 'Unknown')

            # Determine action based on note
            note_lower = note.lower()
            if any(word in note_lower for word in ['wrong', 'incorrect', 'error', 'mistake']):
                action = "Verify and correct"
            elif any(word in note_lower for word in ['duplicate', 'dup', 'already']):
                action = "Check for duplicates"
            elif any(word in note_lower for word in ['missing', 'empty', 'blank', 'null']):
                action = "Add missing data"
            elif any(word in note_lower for word in ['old', 'outdated', 'stale', 'expired']):
                action = "Review for removal/update"
            elif any(word in note_lower for word in ['?', 'why', 'unclear', 'confused']):
                action = "Clarify with stakeholder"
            else:
                action = "Review"

            md.append(f"- [ ] **{record_type}:** {title}")
            md.append(f"  - Issue: {note}")
            md.append(f"  - Action: {action}")
            md.append("")
    else:
        md.append("---")
        md.append("")
        md.append("## Items Requiring Action")
        md.append("")
        md.append("*No items flagged for review.*")
        md.append("")

    # Footer
    md.append("---")
    md.append("")
    md.append("*Coordinator report - for full details request Creator report*")

    return '\n'.join(md)


# ============== Main ==============

def main():
    parser = argparse.ArgumentParser(
        description='Process Mission App flagged records reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('report', help='Path to the flagged records report (.md)')
    parser.add_argument('--coordinator', action='store_true',
                        help='Generate simplified report for Coordinator')
    parser.add_argument('--creator', action='store_true',
                        help='Generate full detailed report for Creator (default)')
    parser.add_argument('-o', '--output', help='Output filename (default: auto-generated)')

    args = parser.parse_args()

    report_path = args.report

    # Check report exists
    if not Path(report_path).exists():
        print(f"Error: Report file not found: {report_path}")
        sys.exit(1)

    # Determine mode (creator is default)
    mode = 'coordinator' if args.coordinator else 'creator'

    print(f"\nProcessing report: {report_path}")
    print(f"Mode: {mode.capitalize()}")

    # Extract JSON from report
    report_data, error = extract_json_from_report(report_path)
    if error:
        print(f"Error: {error}")
        sys.exit(1)

    # Find matching manifest
    mission_id = report_data.get('mission_id')
    manifest = None
    manifest_path = None
    all_passed = None
    checks = []

    if mission_id:
        # Search in current dir and report's directory
        report_dir = Path(report_path).parent
        search_dirs = ['.', str(report_dir)]

        manifest, manifest_path = find_manifest(mission_id, search_dirs)
        if manifest:
            checks, all_passed = verify_integrity(report_data, manifest)
            status = "✅ Verified" if all_passed else "⚠️ Failed"
            print(f"Integrity: {status}")
        else:
            print(f"Warning: No manifest found for mission_id: {mission_id}")
    else:
        print("Warning: Report does not contain a mission_id")

    # Generate report
    if mode == 'coordinator':
        md_content = generate_coordinator_report(report_data, manifest, manifest_path, checks, all_passed)
    else:
        md_content = generate_creator_report(report_data, manifest, manifest_path, checks, all_passed)

    # Determine output filename
    if args.output:
        output_path = args.output
    else:
        report_stem = Path(report_path).stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"processed_{mode}_{report_stem}_{timestamp}.md"

    # Write output
    Path(output_path).write_text(md_content, encoding='utf-8')

    flagged_count = len(report_data.get('flagged', []))
    print(f"Flagged records: {flagged_count}")
    print(f"\n✅ Report saved: {output_path}")


if __name__ == '__main__':
    main()
