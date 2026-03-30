#!/usr/bin/env python3
"""
Mission App Generator - Shared Base Module

This module contains all shared functionality for Mission App generators.
Individual missions import from this and provide their own configuration.

Usage in a mission generator:
    from generator_base import generate_mission_app, read_excel_data

    ENTITY_CONFIG = {...}
    FIELD_CONFIG = {...}
    RENDER_FUNCTIONS = '''...'''

    if __name__ == '__main__':
        generate_mission_app(ENTITY_CONFIG, FIELD_CONFIG, RENDER_FUNCTIONS)
"""

import sys
import re
import json
import zlib
import base64
import zipfile
import hashlib
import secrets
import argparse
import random
import string
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta


def safe_json_embed(obj, **kwargs):
    """Serialize to JSON and escape sequences that are dangerous inside <script> tags.

    This prevents data values containing '</script>' from prematurely closing
    the HTML script block, which would enable XSS injection.
    """
    return json.dumps(obj, **kwargs).replace('</script>', r'<\/script>').replace('</Script>', r'<\/Script>').replace('</SCRIPT>', r'<\/SCRIPT>')


# ============== HTML Template ==============

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; form-action 'none'; base-uri 'none';">
    <title>{title}</title>
    <style>
        :root {{
            --bg: #1a1a2e;
            --surface: #0f3460;
            --accent: #e94560;
            --accent-light: #ff6b81;
            --text: #eee;
            --text-muted: #8892b0;
            --card-bg: #1e2a4a;
            --card-border: #2a3a5a;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: var(--card-bg);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }}
        h1 {{ color: var(--text); margin-bottom: 10px; font-size: 28px; }}
        .header-top {{ display: flex; justify-content: space-between; align-items: start; }}
        .help-link {{
            color: var(--accent);
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            padding: 6px 12px;
            border-radius: 6px;
            transition: background 0.2s;
        }}
        .help-link:hover {{ background: rgba(233, 69, 96, 0.1); }}
        .subtitle {{ color: var(--text-muted); font-size: 14px; }}
        .mission-context {{
            margin-top: 15px;
            padding: 15px;
            background: rgba(42, 58, 90, 0.6);
            border-left: 4px solid var(--accent);
            border-radius: 4px;
            font-size: 14px;
            color: var(--text);
            line-height: 1.5;
        }}
        .mission-context strong {{ color: var(--accent); }}

        .search-section {{
            background: var(--card-bg);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }}
        .search-controls {{ display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }}
        .search-input {{
            flex: 1;
            min-width: 250px;
            padding: 12px 20px;
            border: 2px solid var(--card-border);
            border-radius: 8px;
            font-size: 15px;
            background: var(--surface);
            color: var(--text);
        }}
        .search-input:focus {{ outline: none; border-color: var(--accent); }}
        .filter-buttons {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid var(--accent);
            background: transparent;
            color: var(--accent);
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }}
        .filter-btn:hover {{ background: rgba(233, 69, 96, 0.1); }}
        .filter-btn.active {{ background: var(--accent); color: white; }}

        .export-flags-btn {{
            padding: 10px 20px;
            border: 2px solid #ffc107;
            background: #ffc107;
            color: #856404;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .export-flags-btn:hover {{ background: #e0a800; }}
        .export-flags-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}

        .stats {{ display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }}
        .stat-card {{
            flex: 1;
            min-width: 150px;
            padding: 20px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            color: white;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
            box-shadow: 0 4px 16px rgba(233, 69, 96, 0.2);
        }}
        .stat-number {{ font-size: 32px; font-weight: bold; margin-bottom: 5px; color: var(--accent); }}
        .stat-label {{ font-size: 13px; color: var(--text-muted); }}

        .results-section {{
            background: var(--card-bg);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}

        .result-item {{
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
        }}
        .result-item:hover {{
            box-shadow: 0 4px 12px rgba(233, 69, 96, 0.2);
            border-color: var(--accent);
        }}
        .result-item.flagged {{
            border: 2px solid #ffc107;
            background: rgba(42, 58, 90, 0.8);
        }}

        .result-header {{ display: flex; justify-content: space-between; margin-bottom: 15px; align-items: start; }}
        .result-title {{ font-size: 18px; font-weight: 600; color: var(--text); margin-bottom: 5px; }}
        .result-type {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .flag-btn {{
            padding: 6px 12px;
            border: 1px solid #ffc107;
            background: var(--card-bg);
            color: #ffc107;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .flag-btn:hover {{ background: #fff3cd; }}
        .flag-btn.flagged {{ background: #ffc107; color: white; }}

        .flag-note-input {{
            width: 100%;
            padding: 8px;
            border: 1px solid var(--card-border);
            background: var(--surface);
            color: var(--text);
            border-radius: 4px;
            font-size: 13px;
            margin-top: 8px;
            display: none;
        }}
        .flag-note-input.active {{ display: block; }}

        .result-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        .detail-item {{ display: flex; flex-direction: column; }}
        .detail-label {{
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 4px;
            text-transform: uppercase;
        }}
        .detail-value {{ font-size: 14px; color: var(--text); }}
        .record-link {{
            color: var(--accent-light, #ff6b81);
            text-decoration: none;
            border-bottom: 1px solid rgba(255,107,129,0.3);
            transition: border-color 0.15s;
        }}
        .record-link:hover {{ border-bottom-color: var(--accent-light, #ff6b81); }}

        .relationships {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--card-border);
        }}
        .relationship-section {{ margin-bottom: 15px; }}
        .relationship-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 10px;
        }}
        .relationship-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .relationship-tag {{
            padding: 6px 12px;
            background: rgba(42, 58, 90, 0.6);
            border: 1px solid var(--card-border);
            border-radius: 6px;
            font-size: 13px;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s;
        }}
        .relationship-tag:hover {{
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }}
        .clear-btn {{
            padding: 12px 20px;
            border: 2px solid var(--card-border);
            background: transparent;
            color: var(--text-muted);
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .clear-btn:hover {{
            border-color: var(--accent);
            color: var(--accent);
        }}
        .clear-btn.hidden {{ display: none; }}

        .no-results {{ text-align: center; padding: 60px 20px; color: var(--text-muted); }}
        .no-results-icon {{ font-size: 64px; margin-bottom: 20px; opacity: 0.3; }}

        .welcome-modal {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        .welcome-modal.hidden {{ display: none; }}
        .welcome-content {{
            background: var(--card-bg);
            border-radius: 16px;
            padding: 40px;
            max-width: 600px;
            margin: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }}
        .welcome-content h2 {{ color: var(--accent); font-size: 28px; margin-bottom: 10px; }}
        .welcome-content .tagline {{ color: var(--text-muted); font-size: 14px; margin-bottom: 25px; font-style: italic; }}
        .welcome-features {{
            background: rgba(42, 58, 90, 0.6);
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
        }}
        .welcome-feature {{ display: flex; align-items: start; margin-bottom: 15px; }}
        .welcome-feature:last-child {{ margin-bottom: 0; }}
        .welcome-feature-icon {{ font-size: 24px; margin-right: 12px; }}
        .welcome-feature-text {{ flex: 1; }}
        .welcome-feature-title {{ font-weight: 600; color: var(--text); margin-bottom: 3px; }}
        .welcome-feature-desc {{ font-size: 14px; color: var(--text-muted); line-height: 1.4; }}
        .welcome-note {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .welcome-note-title {{ font-weight: 600; color: #856404; margin-bottom: 5px; font-size: 14px; }}
        .welcome-note-text {{ font-size: 13px; color: #856404; line-height: 1.5; }}
        .welcome-btn {{
            width: 100%;
            padding: 14px 24px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            background: linear-gradient(135deg, var(--accent) 0%, #c73652 100%);
            color: white;
            margin-top: 25px;
        }}
        .welcome-btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(233, 69, 96, 0.4); }}

        {custom_styles}
    </style>
</head>
<body>
<div class="welcome-modal" id="welcomeModal">
    <div class="welcome-content">
        <h2>Welcome!</h2>
        <p class="tagline">This is a purpose-built data review tool, created just for you</p>
        <div class="welcome-features">
            {welcome_features_html}
        </div>
        {expiration_notice}
        <div class="welcome-note">
            <div class="welcome-note-title">💡 Think of this as a "disposable data viewer"</div>
            <div class="welcome-note-text">This tool was custom-generated for this specific data review. It's intentionally lightweight and temporary - perfect for one-time exploration without the overhead of a full application.</div>
        </div>
        <div class="welcome-note" style="background: rgba(42, 58, 90, 0.8); border-left-color: #e94560;">
            <div class="welcome-note-title">📊 Session Activity</div>
            <div class="welcome-note-text">Your search and flag activity during this session is included in the exported report to help the review process.</div>
        </div>
        <div style="text-align: center; margin-top: 15px; font-size: 12px; color: #999;">🔑 App ID: <code style="background: rgba(42, 58, 90, 0.8); padding: 2px 6px; border-radius: 3px; color: #eee;" id="welcomeAppId"></code></div>
        <button class="welcome-btn" onclick="document.getElementById('welcomeModal').classList.add('hidden')">Let's Get Started →</button>
    </div>
</div>

<div class="container">
    <div class="header">
        <div class="header-top">
            <div>
                <h1>{heading}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
            <a class="help-link" onclick="document.getElementById('welcomeModal').classList.remove('hidden')">ℹ️ Instructions</a>
        </div>
        <div class="mission-context">
            <strong>Your mission:</strong> {mission_context}
        </div>
    </div>

    <div class="search-section">
        <div class="search-controls">
            <input type="text" class="search-input" id="searchInput" placeholder="Search across all fields...">
            <button class="clear-btn hidden" id="clearBtn">✕ Clear</button>
            <div class="filter-buttons">
                {filter_buttons}
                <button class="export-flags-btn" id="exportFlagsBtn" disabled>📋 Export Flagged Records</button>
            </div>
        </div>
        <div class="stats">
            {stats_cards}
            <div class="stat-card"><div class="stat-number" id="resultCount">0</div><div class="stat-label">Results Found</div></div>
            <div class="stat-card" style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);"><div class="stat-number" id="flaggedCount">0</div><div class="stat-label">Flagged Issues</div></div>
        </div>
    </div>

    <div class="results-section">
        <div id="resultsContainer"></div>
    </div>
</div>

<script>
{javascript_code}
</script>
</body>
</html>
"""


# ============== Expiration JavaScript ==============

EXPIRATION_JAVASCRIPT = """
const EXPIRATION_CONFIG = {expiration_config_json};

function checkExpiration() {
    if (!EXPIRATION_CONFIG.enabled) return true;
    const now = Date.now();
    if (EXPIRATION_CONFIG.activeFrom && now < EXPIRATION_CONFIG.activeFrom) {
        showNotYetActive();
        return false;
    }
    if (EXPIRATION_CONFIG.activeUntil && now > EXPIRATION_CONFIG.activeUntil) {
        showExpiredState();
        return false;
    }
    showCountdownBanner();
    return true;
}

function showNotYetActive() {
    const activeDate = new Date(EXPIRATION_CONFIG.activeFrom);
    document.body.innerHTML = `
        <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #1a1a2e; padding: 20px;">
            <div style="background: #1e2a4a; border-radius: 16px; padding: 60px; max-width: 500px; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
                <div style="font-size: 80px; margin-bottom: 20px;">⏳</div>
                <h1 style="color: #e94560; margin-bottom: 15px; font-size: 28px;">Not Yet Active</h1>
                <p style="color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 25px;">
                    This Mission App isn't ready yet. It will activate on:
                </p>
                <div style="background: rgba(42, 58, 90, 0.6); padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <div style="font-size: 24px; font-weight: bold; color: #eee;">
                        ${activeDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
                    </div>
                    <div style="font-size: 18px; color: #e94560; margin-top: 5px;">
                        ${activeDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}
                    </div>
                </div>
                <p style="color: #999; font-size: 14px;">
                    Please come back then, or contact the sender if you need early access.
                </p>
            </div>
        </div>
    `;
    document.title = "Not Yet Active - Mission App";
}

function showExpiredState() {
    const expiredDate = new Date(EXPIRATION_CONFIG.activeUntil);
    const flagCount = typeof flaggedRecords !== 'undefined' ? flaggedRecords.length : 0;
    document.body.innerHTML = `
        <div id="selfDestructContainer" style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 20px;">
            <div style="text-align: center; color: white;">
                <div style="font-size: 120px; font-family: 'Courier New', monospace; text-shadow: 0 0 30px #ff6b6b;">💥</div>
                <h1 style="font-size: 36px; margin: 20px 0; color: #ffffff; text-shadow: 0 0 30px rgba(255,255,255,0.8), 0 0 60px rgba(255,107,107,0.5);">MISSION COMPLETE</h1>
                <p style="font-size: 18px; color: rgba(255,255,255,0.85); margin-bottom: 30px;">This app has self-destructed as planned</p>
                <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 30px; max-width: 400px; margin: 0 auto;">
                    <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 10px;">Mission ended</div>
                    <div style="font-size: 20px; font-weight: bold; color: #ffffff;">${expiredDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</div>
                    <div style="font-size: 16px; color: rgba(255,255,255,0.85); margin-top: 5px;">${expiredDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
                ${flagCount > 0 ? `
                <div style="margin-top: 30px;">
                    <p style="font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 15px;">You have ${flagCount} flagged record${flagCount !== 1 ? 's' : ''} to export</p>
                    <button id="expiredExportBtn" style="background: linear-gradient(135deg, #ffc107 0%, #ffca2c 100%); color: #000; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(255,193,7,0.4);">
                        📋 Export Flagged Records
                    </button>
                </div>
                ` : ''}
                <p style="margin-top: 30px; font-size: 14px; color: rgba(255,255,255,0.6);">
                    This message will self-destruct in... just kidding, it already did.<br>
                    Contact the sender if you need a new mission app.
                </p>
                <div style="margin-top: 40px; font-size: 12px; color: rgba(255,255,255,0.4);">🎯 Mission Apps are temporary by design</div>
            </div>
        </div>
    `;
    document.title = "Mission Complete - Self-Destructed";
    const exportBtn = document.getElementById('expiredExportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportFromExpiredState);
    }
}

function exportFromExpiredState() {
    if (typeof flaggedRecords === 'undefined' || flaggedRecords.length === 0) return;
    const generated = new Date().toISOString();
    const missionTitle = missionInfo.title || 'Data Review';
    const sessionEnd = new Date();
    const sessionMinutes = typeof analytics !== 'undefined' ? Math.round((sessionEnd - new Date(analytics.sessionStart)) / 60000) : 0;

    let md = '# Flagged Records Report\\n\\n';
    md += '**Generated:** ' + new Date().toLocaleString() + '  \\n';
    md += '**Mission:** ' + missionTitle + '  \\n';
    md += '**Mission ID:** `' + missionInfo.mission_id + '`  \\n';
    md += '**App Fingerprint:** `' + missionInfo.app_fingerprint + '`  \\n';
    md += '**Flagged:** ' + flaggedRecords.length + ' records\\n';
    md += '**Note:** Exported after mission expiration\\n\\n';
    md += '---\\n\\n';

    const jsonData = {
        generated: generated,
        mission: missionTitle,
        mission_id: missionInfo.mission_id,
        data_fingerprint: missionInfo.data_fingerprint,
        app_fingerprint: missionInfo.app_fingerprint,
        exported_after_expiration: true,
        analytics: typeof analytics !== 'undefined' ? {
            session_start: analytics.sessionStart,
            session_end: sessionEnd.toISOString(),
            session_duration_minutes: sessionMinutes,
            searches: analytics.searches,
            filters: analytics.filters,
            navigation: analytics.navigation,
            flags: analytics.flags
        } : null,
        flagged: []
    };

    md += '## Records\\n\\n';
    flaggedRecords.forEach((flag, index) => {
        const recordData = typeof recordLookup !== 'undefined' ? (recordLookup[flag.id] || {}) : {};
        const recordType = flag.id.split('-')[0] || flag.type;
        md += '### ' + (index + 1) + '. ' + flag.type + ': ' + flag.name + '\\n\\n';
        const fields = Object.entries(recordData);
        if (fields.length > 0) {
            md += '| Field | Value |\\n|-------|-------|\\n';
            fields.forEach(([key, value]) => {
                const displayValue = value !== null && value !== undefined ? String(value) : '';
                md += '| ' + key + ' | ' + displayValue.replace(/\\|/g, '\\\\|') + ' |\\n';
            });
            md += '\\n';
        }
        if (flag.note) md += '**Issue:** ' + flag.note + '\\n\\n';
        md += '---\\n\\n';
        jsonData.flagged.push({ type: recordType, id: flag.id, title: flag.name, note: flag.note || '', timestamp: flag.timestamp, data: recordData });
    });

    md += '## Machine-Readable Data\\n\\n```json\\n' + JSON.stringify(jsonData, null, 2) + '\\n```\\n';

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'flagged_' + new Date().toISOString().split('T')[0] + '.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    alert('Flagged records report downloaded!');
}

function showCountdownBanner() {
    if (!EXPIRATION_CONFIG.activeUntil) return;
    const banner = document.createElement('div');
    banner.id = 'expirationBanner';
    banner.style.cssText = 'background: linear-gradient(90deg, #fff3cd 0%, #ffe8a1 100%); border-bottom: 2px solid #ffc107; padding: 10px 20px; text-align: center; font-size: 14px; color: #856404; position: fixed; top: 0; left: 0; right: 0; z-index: 999; box-shadow: 0 2px 4px rgba(0,0,0,0.1);';
    banner.innerHTML = '⏰ This app will expire in <strong id="countdown"></strong>. Complete your work and export results before then.';
    document.body.insertBefore(banner, document.body.firstChild);
    document.body.style.paddingTop = '50px';
    updateCountdown();
}

function updateCountdown() {
    const countdownEl = document.getElementById('countdown');
    if (!countdownEl) return;
    const now = Date.now();
    const timeRemaining = EXPIRATION_CONFIG.activeUntil - now;
    if (timeRemaining <= 0) {
        // Clear data from memory before showing expired state
        if (typeof data !== 'undefined') data = null;
        if (typeof recordLookup !== 'undefined') { for (const k in recordLookup) delete recordLookup[k]; }
        showExpiredState();
        return;
    }
    const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
    let countdownText;
    if (days > 1) countdownText = `${days} days`;
    else if (days === 1) countdownText = `1 day, ${hours} hours`;
    else if (hours > 0) countdownText = `${hours} hour${hours !== 1 ? 's' : ''}, ${minutes} min`;
    else {
        countdownText = `${minutes} minute${minutes !== 1 ? 's' : ''}`;
        const banner = document.getElementById('expirationBanner');
        if (banner) {
            banner.style.background = 'linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%)';
            banner.style.borderColor = '#dc3545';
            banner.style.color = '#721c24';
        }
    }
    countdownEl.textContent = countdownText;
    const updateInterval = days > 0 ? 60000 : (hours > 0 ? 30000 : 10000);
    setTimeout(updateCountdown, updateInterval);
}

if (!checkExpiration()) {
    throw new Error('App not active');
}
"""


# ============== Session-Based Expiration JavaScript ==============

SESSION_EXPIRATION_JAVASCRIPT = """
const SESSION_CONFIG = {session_config_json};
const SESSION_STORAGE_KEY = 'mission_session_' + SESSION_CONFIG.missionId;

function getSessionStart() {
    const stored = localStorage.getItem(SESSION_STORAGE_KEY);
    if (stored) {
        const parsed = JSON.parse(stored);
        return parsed.startTime;
    }
    // First time opening - record session start
    const startTime = Date.now();
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({
        startTime: startTime,
        missionId: SESSION_CONFIG.missionId
    }));
    return startTime;
}

function checkSessionExpiration() {
    const sessionStart = getSessionStart();
    const now = Date.now();
    const expiresAt = sessionStart + SESSION_CONFIG.durationMs;

    if (now > expiresAt) {
        showSessionExpiredState(sessionStart, expiresAt);
        return false;
    }
    showSessionCountdownBanner(sessionStart, expiresAt);
    return true;
}

function showSessionExpiredState(sessionStart, expiresAt) {
    const startedDate = new Date(sessionStart);
    const expiredDate = new Date(expiresAt);
    const flagCount = typeof flaggedRecords !== 'undefined' ? flaggedRecords.length : 0;
    document.body.innerHTML = `
        <div id="selfDestructContainer" style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 20px;">
            <div style="text-align: center; color: white;">
                <div style="font-size: 120px; font-family: 'Courier New', monospace; text-shadow: 0 0 30px #ff6b6b;">💥</div>
                <h1 style="font-size: 36px; margin: 20px 0; color: #ffffff; text-shadow: 0 0 30px rgba(255,255,255,0.8), 0 0 60px rgba(255,107,107,0.5);">SESSION EXPIRED</h1>
                <p style="font-size: 18px; color: rgba(255,255,255,0.85); margin-bottom: 30px;">Your ${SESSION_CONFIG.durationDisplay} session has ended</p>
                <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 30px; max-width: 400px; margin: 0 auto;">
                    <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 10px;">Session started</div>
                    <div style="font-size: 18px; font-weight: bold; color: #ffffff;">${startedDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })} at ${startedDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                    <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-top: 15px; margin-bottom: 10px;">Expired</div>
                    <div style="font-size: 18px; font-weight: bold; color: #ffffff;">${expiredDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })} at ${expiredDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
                ${flagCount > 0 ? `
                <div style="margin-top: 30px;">
                    <p style="font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 15px;">You have ${flagCount} flagged record${flagCount !== 1 ? 's' : ''} to export</p>
                    <button id="expiredExportBtn" style="background: linear-gradient(135deg, #ffc107 0%, #ffca2c 100%); color: #000; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(255,193,7,0.4);">
                        📋 Export Flagged Records
                    </button>
                </div>
                ` : ''}
                <p style="margin-top: 30px; font-size: 14px; color: rgba(255,255,255,0.6);">
                    Your session time limit has been reached.<br>
                    Contact the sender if you need a new mission app.
                </p>
                <div style="margin-top: 40px; font-size: 12px; color: rgba(255,255,255,0.4);">🎯 Mission Apps are temporary by design</div>
            </div>
        </div>
    `;
    document.title = "Session Expired - Mission App";
    const exportBtn = document.getElementById('expiredExportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportFromExpiredState);
    }
}

function exportFromExpiredState() {
    if (typeof flaggedRecords === 'undefined' || flaggedRecords.length === 0) return;
    const generated = new Date().toISOString();
    const missionTitle = missionInfo.title || 'Data Review';
    const sessionEnd = new Date();
    const sessionMinutes = typeof analytics !== 'undefined' ? Math.round((sessionEnd - new Date(analytics.sessionStart)) / 60000) : 0;

    let md = '# Flagged Records Report\\n\\n';
    md += '**Generated:** ' + new Date().toLocaleString() + '  \\n';
    md += '**Mission:** ' + missionTitle + '  \\n';
    md += '**Mission ID:** `' + missionInfo.mission_id + '`  \\n';
    md += '**App Fingerprint:** `' + missionInfo.app_fingerprint + '`  \\n';
    md += '**Flagged:** ' + flaggedRecords.length + ' records\\n';
    md += '**Note:** Exported after session expiration\\n\\n';
    md += '---\\n\\n';

    const jsonData = {
        generated: generated,
        mission: missionTitle,
        mission_id: missionInfo.mission_id,
        data_fingerprint: missionInfo.data_fingerprint,
        app_fingerprint: missionInfo.app_fingerprint,
        exported_after_expiration: true,
        session_based_expiration: true,
        analytics: typeof analytics !== 'undefined' ? {
            session_start: analytics.sessionStart,
            session_end: sessionEnd.toISOString(),
            session_duration_minutes: sessionMinutes,
            searches: analytics.searches,
            filters: analytics.filters,
            navigation: analytics.navigation,
            flags: analytics.flags
        } : null,
        flagged: []
    };

    md += '## Records\\n\\n';
    flaggedRecords.forEach((flag, index) => {
        const recordData = typeof recordLookup !== 'undefined' ? (recordLookup[flag.id] || {}) : {};
        const recordType = flag.id.split('-')[0] || flag.type;
        md += '### ' + (index + 1) + '. ' + flag.type + ': ' + flag.name + '\\n\\n';
        const fields = Object.entries(recordData);
        if (fields.length > 0) {
            md += '| Field | Value |\\n|-------|-------|\\n';
            fields.forEach(([key, value]) => {
                const displayValue = value !== null && value !== undefined ? String(value) : '';
                md += '| ' + key + ' | ' + displayValue.replace(/\\|/g, '\\\\|') + ' |\\n';
            });
            md += '\\n';
        }
        if (flag.note) md += '**Issue:** ' + flag.note + '\\n\\n';
        md += '---\\n\\n';
        jsonData.flagged.push({ type: recordType, id: flag.id, title: flag.name, note: flag.note || '', timestamp: flag.timestamp, data: recordData });
    });

    md += '## Machine-Readable Data\\n\\n```json\\n' + JSON.stringify(jsonData, null, 2) + '\\n```\\n';

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'flagged_' + new Date().toISOString().split('T')[0] + '.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    alert('Flagged records report downloaded!');
}

function showSessionCountdownBanner(sessionStart, expiresAt) {
    const banner = document.createElement('div');
    banner.id = 'expirationBanner';
    banner.style.cssText = 'background: linear-gradient(90deg, #fff3cd 0%, #ffe8a1 100%); border-bottom: 2px solid #ffc107; padding: 10px 20px; text-align: center; font-size: 14px; color: #856404; position: fixed; top: 0; left: 0; right: 0; z-index: 999; box-shadow: 0 2px 4px rgba(0,0,0,0.1);';
    banner.innerHTML = '⏰ Session expires in <strong id="countdown"></strong>. Complete your work and export results before then.';
    document.body.insertBefore(banner, document.body.firstChild);
    document.body.style.paddingTop = '50px';
    updateSessionCountdown(sessionStart, expiresAt);
}

function updateSessionCountdown(sessionStart, expiresAt) {
    const countdownEl = document.getElementById('countdown');
    if (!countdownEl) return;
    const now = Date.now();
    const timeRemaining = expiresAt - now;
    if (timeRemaining <= 0) {
        // Clear data from memory before showing expired state
        if (typeof data !== 'undefined') data = null;
        if (typeof recordLookup !== 'undefined') { for (const k in recordLookup) delete recordLookup[k]; }
        showSessionExpiredState(sessionStart, expiresAt);
        return;
    }
    const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
    let countdownText;
    if (days > 1) countdownText = `${days} days`;
    else if (days === 1) countdownText = `1 day, ${hours} hours`;
    else if (hours > 0) countdownText = `${hours} hour${hours !== 1 ? 's' : ''}, ${minutes} min`;
    else {
        countdownText = `${minutes} minute${minutes !== 1 ? 's' : ''}`;
        const banner = document.getElementById('expirationBanner');
        if (banner) {
            banner.style.background = 'linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%)';
            banner.style.borderColor = '#dc3545';
            banner.style.color = '#721c24';
        }
    }
    countdownEl.textContent = countdownText;
    const updateInterval = days > 0 ? 60000 : (hours > 0 ? 30000 : 10000);
    setTimeout(() => updateSessionCountdown(sessionStart, expiresAt), updateInterval);
}

if (!checkSessionExpiration()) {
    throw new Error('Session expired');
}
"""


# ============== Core JavaScript ==============

CORE_JAVASCRIPT = """
let currentFilter = 'all';
let flaggedRecords = [];
let recordLookup = {};
const missionInfo = {mission_info_json};
const _appIdEl = document.getElementById('welcomeAppId');
if (_appIdEl) _appIdEl.textContent = missionInfo.mission_id || '';
const searchInput = document.getElementById('searchInput');

const analytics = {
    sessionStart: new Date().toISOString(),
    searches: [],
    filters: [],
    flags: [],
    navigation: [],
    recordsViewed: new Set()
};

function trackEvent(type, data) {
    const event = { ...data, timestamp: new Date().toISOString() };
    if (type === 'search') analytics.searches.push(event);
    else if (type === 'filter') analytics.filters.push(event);
    else if (type === 'flag') analytics.flags.push(event);
    else if (type === 'navigation') analytics.navigation.push(event);
}

function updateFlaggedCount() {
    document.getElementById('flaggedCount').textContent = flaggedRecords.length;
    document.getElementById('exportFlagsBtn').disabled = flaggedRecords.length === 0;
}

function toggleFlag(recordId, recordType, recordName) {
    const index = flaggedRecords.findIndex(f => f.id === recordId);
    if (index >= 0) {
        flaggedRecords.splice(index, 1);
        trackEvent('flag', { action: 'unflag', recordId, recordType });
    } else {
        flaggedRecords.push({
            id: recordId,
            type: recordType,
            name: recordName,
            note: '',
            timestamp: new Date().toISOString()
        });
        trackEvent('flag', { action: 'flag', recordId, recordType });
    }
    updateFlaggedCount();
    performSearch();
}

function updateFlagNote(recordId, note) {
    const record = flaggedRecords.find(f => f.id === recordId);
    if (record) record.note = note;
}

const clearBtn = document.getElementById('clearBtn');
let searchTimeout;

searchInput.addEventListener('input', function() {
    clearBtn.classList.toggle('hidden', !this.value);
    performSearch();
    clearTimeout(searchTimeout);
    if (this.value.trim()) {
        searchTimeout = setTimeout(() => {
            const resultCount = parseInt(document.getElementById('resultCount').textContent) || 0;
            trackEvent('search', { query: this.value.trim(), resultCount });
        }, 500);
    }
});

clearBtn.addEventListener('click', function() {
    searchInput.value = '';
    clearBtn.classList.add('hidden');
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');
    currentFilter = 'all';
    performSearch();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter = e.target.dataset.filter;
        trackEvent('filter', { filter: currentFilter });
        performSearch();
    });
});

function navigateTo(searchTerm, filterType) {
    trackEvent('navigation', { to: searchTerm, filterType: filterType || 'all' });
    searchInput.value = searchTerm;
    clearBtn.classList.remove('hidden');
    if (filterType) {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        const targetBtn = document.querySelector(`.filter-btn[data-filter="${filterType}"]`);
        if (targetBtn) targetBtn.classList.add('active');
        currentFilter = filterType;
    }
    performSearch();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function filterTo(filterType) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    const targetBtn = document.querySelector(`.filter-btn[data-filter="${filterType}"]`);
    if (targetBtn) targetBtn.classList.add('active');
    currentFilter = filterType;
    trackEvent('filter', { filter: currentFilter });
    performSearch();
}

function esc(text) {
    if (!text) return '';
    const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;', '`': '&#96;'};
    return String(text).replace(/[&<>"'`]/g, m => map[m]);
}

function highlight(text) {
    if (!text) return '';
    const escaped = esc(text);
    if (!currentQuery) return escaped;
    const regex = new RegExp('(' + currentQuery.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + ')', 'gi');
    return escaped.replace(regex, '<mark style="background:#fef08a;padding:1px 2px;border-radius:2px;">$1</mark>');
}

function formatCurrency(value) {
    if (!value && value !== 0) return '';
    const num = typeof value === 'number' ? value : parseFloat(value);
    if (isNaN(num)) return esc(String(value));
    return '$' + num.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0});
}

document.getElementById('exportFlagsBtn').addEventListener('click', function() {
    if (flaggedRecords.length === 0) return;
    const generated = new Date().toISOString();
    const missionTitle = document.querySelector('h1').textContent.replace(/^[^\\w]*/, '');
    const sessionStart = new Date(analytics.sessionStart);
    const sessionEnd = new Date();
    const sessionMinutes = Math.round((sessionEnd - sessionStart) / 60000);

    let md = '# Flagged Records Report\\n\\n';
    md += '**Generated:** ' + new Date().toLocaleString() + '  \\n';
    md += '**Mission:** ' + missionTitle + '  \\n';
    md += '**Mission ID:** `' + missionInfo.mission_id + '`  \\n';
    md += '**App Fingerprint:** `' + missionInfo.app_fingerprint + '`  \\n';
    md += '**Flagged:** ' + flaggedRecords.length + ' records\\n\\n';
    md += '---\\n\\n';
    md += '## Session Analytics\\n\\n';
    md += '| Metric | Value |\\n|--------|-------|\\n';
    md += '| Session Duration | ' + sessionMinutes + ' minutes |\\n';
    md += '| Searches Performed | ' + analytics.searches.length + ' |\\n';
    md += '| Filter Changes | ' + analytics.filters.length + ' |\\n';
    md += '| Navigation Clicks | ' + analytics.navigation.length + ' |\\n';
    md += '| Flag/Unflag Actions | ' + analytics.flags.length + ' |\\n';
    md += '\\n---\\n\\n## Records\\n\\n';

    const jsonData = {
        generated: generated,
        mission: missionTitle,
        mission_id: missionInfo.mission_id,
        data_fingerprint: missionInfo.data_fingerprint,
        app_fingerprint: missionInfo.app_fingerprint,
        analytics: {
            session_start: analytics.sessionStart,
            session_end: sessionEnd.toISOString(),
            session_duration_minutes: sessionMinutes,
            searches: analytics.searches,
            filters: analytics.filters,
            navigation: analytics.navigation,
            flags: analytics.flags
        },
        flagged: []
    };

    flaggedRecords.forEach((flag, index) => {
        const recordData = recordLookup[flag.id] || {};
        const recordType = flag.id.split('-')[0] || flag.type;
        md += '### ' + (index + 1) + '. ' + flag.type + ': ' + flag.name + '\\n\\n';
        const fields = Object.entries(recordData);
        if (fields.length > 0) {
            md += '| Field | Value |\\n|-------|-------|\\n';
            fields.forEach(([key, value]) => {
                const displayValue = value !== null && value !== undefined ? String(value) : '';
                md += '| ' + key + ' | ' + displayValue.replace(/\\|/g, '\\\\|') + ' |\\n';
            });
            md += '\\n';
        }
        if (flag.note) md += '**Issue:** ' + flag.note + '\\n\\n';
        md += '---\\n\\n';
        jsonData.flagged.push({ type: recordType, id: flag.id, title: flag.name, note: flag.note || '', timestamp: flag.timestamp, data: recordData });
    });

    md += '## Machine-Readable Data\\n\\n```json\\n' + JSON.stringify(jsonData, null, 2) + '\\n```\\n';

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'flagged_records_' + new Date().toISOString().split('T')[0] + '.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    alert('Flagged records report downloaded!');
});
"""


# ============== Synthetic Data Pools ==============

SAMPLE_POOLS = {
    'first_names': ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
                    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica'],
    'last_names': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                   'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas'],
    'companies': ['Acme Corp', 'Globex Industries', 'Initech', 'Umbrella LLC', 'Stark Enterprises',
                  'Wayne Industries', 'Oscorp', 'Cyberdyne Systems', 'Soylent Corp', 'Massive Dynamic'],
    'streets': ['Main St', 'Oak Ave', 'Maple Dr', 'Cedar Ln', 'Pine Rd', 'Elm St', 'Washington Blvd'],
    'cities': ['Springfield', 'Riverside', 'Georgetown', 'Franklin', 'Clinton', 'Madison', 'Salem'],
    'states': ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI'],
    'industries': ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Real Estate'],
    'statuses': ['Active', 'Pending', 'Inactive', 'Review', 'Approved', 'On Hold'],
}


# ============== Excel Reading ==============

def read_excel_data(excel_path, sheet_names):
    """Read Excel file and return data as dict of lists"""

    def get_shared_strings(zf):
        try:
            with zf.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                strings = []
                for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    text_parts = []
                    for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                        if t.text:
                            text_parts.append(t.text)
                    strings.append(''.join(text_parts))
                return strings
        except KeyError:
            return []

    def col_letter_to_index(col):
        result = 0
        for char in col:
            result = result * 26 + (ord(char.upper()) - ord('A') + 1)
        return result - 1

    def parse_cell_ref(ref):
        col = ''
        row = ''
        for char in ref:
            if char.isalpha():
                col += char
            else:
                row += char
        return col_letter_to_index(col), int(row) - 1

    def read_sheet(zf, sheet_path, shared_strings):
        with zf.open(sheet_path) as f:
            tree = ET.parse(f)
            root = tree.getroot()

        rows_data = {}
        for row in root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            row_num = int(row.get('r')) - 1
            rows_data[row_num] = {}
            for cell in row.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                ref = cell.get('r')
                col_idx, _ = parse_cell_ref(ref)
                cell_type = cell.get('t')
                value_elem = cell.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')

                if value_elem is not None and value_elem.text is not None:
                    if cell_type == 's':
                        value = shared_strings[int(value_elem.text)]
                    elif cell_type == 'b':
                        value = value_elem.text == '1'
                    else:
                        try:
                            value = float(value_elem.text)
                            if value == int(value):
                                value = int(value)
                        except ValueError:
                            value = value_elem.text
                else:
                    is_elem = cell.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is')
                    if is_elem is not None:
                        t_elem = is_elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                        value = t_elem.text if t_elem is not None else None
                    else:
                        value = None

                rows_data[row_num][col_idx] = value

        if not rows_data:
            return []

        headers = rows_data.get(0, {})
        max_col = max(headers.keys()) if headers else 0
        header_list = [headers.get(i, f'Column{i}') for i in range(max_col + 1)]

        records = []
        for row_num in sorted(rows_data.keys()):
            if row_num == 0:
                continue
            row_dict = {}
            for col_idx, header in enumerate(header_list):
                value = rows_data[row_num].get(col_idx)
                if value is not None:
                    row_dict[header] = value
            if row_dict:
                records.append(row_dict)

        return records

    def get_sheet_path(zf, sheet_name):
        with zf.open('xl/workbook.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()

        sheets = root.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets')
        sheet_rid = None
        for sheet in sheets:
            if sheet.get('name') == sheet_name:
                sheet_rid = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                break

        if not sheet_rid:
            raise ValueError(f"Sheet '{sheet_name}' not found")

        with zf.open('xl/_rels/workbook.xml.rels') as f:
            tree = ET.parse(f)
            root = tree.getroot()

        for rel in root:
            if rel.get('Id') == sheet_rid:
                target = rel.get('Target')
                if not target.startswith('/'):
                    target = 'xl/' + target
                else:
                    target = target[1:]
                return target

        raise ValueError(f"Could not find path for sheet '{sheet_name}'")

    try:
        data = {}
        with zipfile.ZipFile(excel_path, 'r') as zf:
            shared_strings = get_shared_strings(zf)
            for sheet_name, entity_name in sheet_names.items():
                sheet_path = get_sheet_path(zf, sheet_name)
                data[entity_name] = read_sheet(zf, sheet_path, shared_strings)
        return data
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)


# ============== Helper Functions ==============

def parse_datetime(dt_string):
    """Parse datetime string in various formats"""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse datetime: {dt_string}. Use format: YYYY-MM-DD HH:MM")


def parse_duration(duration_string):
    """Parse duration string like '2h', '30m', '1d' into milliseconds"""
    match = re.match(r'^(\d+(?:\.\d+)?)\s*(m|min|mins|minutes?|h|hr|hrs|hours?|d|days?)$', duration_string.lower().strip())
    if not match:
        raise ValueError(f"Invalid duration format: {duration_string}. Use formats like '2h', '30m', '1d'")

    value = float(match.group(1))
    unit = match.group(2)

    if unit.startswith('m'):
        ms = value * 60 * 1000
    elif unit.startswith('h'):
        ms = value * 60 * 60 * 1000
    elif unit.startswith('d'):
        ms = value * 24 * 60 * 60 * 1000
    else:
        raise ValueError(f"Unknown duration unit: {unit}")

    return int(ms), duration_string


def generate_fingerprints(data, title):
    """Generate mission fingerprints for traceability"""
    data_json = json.dumps(data, sort_keys=True)
    data_fingerprint = hashlib.sha256(data_json.encode()).hexdigest()[:16]

    title_slug = ''.join(c if c.isalnum() else '-' for c in title.lower()).strip('-')[:30]
    date_str = datetime.now().strftime('%Y%m%d')
    random_suffix = secrets.token_hex(3)
    mission_id = f"{title_slug}-{date_str}-{random_suffix}"

    config_str = json.dumps({'title': title, 'data_fingerprint': data_fingerprint}, sort_keys=True)
    app_fingerprint = hashlib.sha256(config_str.encode()).hexdigest()[:16]

    return {
        'mission_id': mission_id,
        'data_fingerprint': data_fingerprint,
        'app_fingerprint': app_fingerprint,
        'generated': datetime.now().isoformat()
    }


# ============== HTML Generation ==============

def generate_html(data, entity_config, field_config, render_functions, search_function,
                  title_override=None, expiration_config=None, session_config=None, preview_mode=False):
    """Generate complete HTML with embedded data"""
    title = title_override or entity_config['title']

    # Preview mode modifications
    if preview_mode:
        heading = f"👁️ PREVIEW: {title}"
        page_title = f"[PREVIEW] {title}"
    else:
        heading = f"🔍 {title}"
        page_title = title

    if expiration_config is None:
        expiration_config = {'enabled': False}

    # Generate filter buttons
    filter_buttons = ['<button class="filter-btn active" data-filter="all">All</button>']
    for entity in entity_config['entities']:
        filter_buttons.append(f'<button class="filter-btn" data-filter="{entity["name"]}">{entity["label"]}</button>')

    # Generate stats cards
    stats_cards = []
    for entity in entity_config['entities']:
        stats_cards.append(
            f'<div class="stat-card" onclick="filterTo(\'{entity["name"]}\')">'
            f'<div class="stat-number" id="{entity["name"]}Count">0</div>'
            f'<div class="stat-label">{entity["label"]}</div></div>'
        )

    # Custom styles
    custom_styles = [f".type-{e['name']} {{ background: {e['bg_color']}; color: {e['color']}; }}" for e in entity_config['entities']]

    # Preview banner styles
    if preview_mode:
        custom_styles.append("""
        .preview-banner {
            background: linear-gradient(90deg, #e94560 0%, #c73652 100%);
            color: white;
            padding: 12px 20px;
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(233, 69, 96, 0.4);
        }
        .preview-banner span { opacity: 0.9; font-weight: 400; margin-left: 10px; }
        body { padding-top: 48px; }
        """)

    # Welcome features
    if preview_mode:
        welcome_features = [
            {'icon': '👁️', 'title': 'This is a Preview', 'desc': 'This app contains sample data only - not real records. Use it to familiarize yourself with the tool.'},
            {'icon': '🎯', 'title': 'Practice Flagging', 'desc': 'Try flagging records and adding notes. Your feedback helps confirm you understand the mission.'},
            {'icon': '📤', 'title': 'Test the Export', 'desc': 'When ready, export your flagged records to confirm you can complete the workflow.'},
            {'icon': '✅', 'title': 'Confirmation', 'desc': 'Send your exported preview report back to confirm you\'re ready for the real mission.'},
        ]
    else:
        welcome_features = entity_config.get('welcome_features', [])

    welcome_features_html = '\n'.join([
        f'''<div class="welcome-feature">
                <div class="welcome-feature-icon">{f['icon']}</div>
                <div class="welcome-feature-text">
                    <div class="welcome-feature-title">{f['title']}</div>
                    <div class="welcome-feature-desc">{f['desc']}</div>
                </div>
            </div>'''
        for f in welcome_features
    ])

    # Mission context
    if preview_mode:
        mission_context = '<strong style="color: #6366f1;">PREVIEW MODE:</strong> This app contains synthetic sample data for training purposes. Explore the interface, try flagging some records, and export a test report to confirm you understand the workflow.'
    else:
        mission_context = entity_config.get('mission_context', 'Review this data and flag any issues you find.')

    # Expiration notice
    if session_config:
        expiration_notice = f'''<div class="welcome-note" style="background: #fff3cd; border-left-color: #ffc107;">
            <div class="welcome-note-title">⏰ This {'preview' if preview_mode else 'app'} has a time limit</div>
            <div class="welcome-note-text">This {'Preview' if preview_mode else 'Mission App'} will expire <strong>{session_config['durationDisplay']}</strong> after you first open it.</div>
        </div>'''
    elif expiration_config.get('enabled') and expiration_config.get('activeUntilDisplay'):
        expiration_notice = f'''<div class="welcome-note" style="background: #fff3cd; border-left-color: #ffc107;">
            <div class="welcome-note-title">⏰ This {'preview' if preview_mode else 'app'} has a deadline</div>
            <div class="welcome-note-text">This {'Preview' if preview_mode else 'Mission App'} will expire on <strong>{expiration_config['activeUntilDisplay']}</strong>.</div>
        </div>'''
    else:
        expiration_notice = ''

    # Generate fingerprints
    mission_info = generate_fingerprints(data, title)
    mission_info['preview'] = preview_mode
    mission_info['title'] = title
    mission_info_json = safe_json_embed(mission_info)

    # Build JavaScript
    js_parts = []

    if session_config:
        # Session-based expiration (dynamic, uses localStorage)
        full_session_config = {
            **session_config,
            'missionId': mission_info['mission_id'],
        }
        session_config_json = safe_json_embed(full_session_config)
        js_parts.append(SESSION_EXPIRATION_JAVASCRIPT.replace('{session_config_json}', session_config_json))
    elif expiration_config.get('enabled'):
        # Fixed expiration (static timestamps)
        expiration_config_json = safe_json_embed(expiration_config)
        js_parts.append(EXPIRATION_JAVASCRIPT.replace('{expiration_config_json}', expiration_config_json))

    # Obfuscate data: compress + base64 encode so it's not plaintext in the file
    data_json = json.dumps(data)
    compressed = zlib.compress(data_json.encode('utf-8'))
    encoded_data = base64.b64encode(compressed).decode('ascii')

    # JavaScript decoder: base64 → zlib decompress → JSON.parse
    # Uses DecompressionStream('deflate') which handles zlib format (RFC 1950)
    # Browser support: Chrome 80+, Firefox 113+, Safari 16.4+, Edge 80+
    data_decoder = f"""const _encoded = "{encoded_data}";
async function _decodeData() {{
    const bin = Uint8Array.from(atob(_encoded), c => c.charCodeAt(0));
    const ds = new DecompressionStream('deflate');
    const writer = ds.writable.getWriter();
    writer.write(bin);
    writer.close();
    const reader = ds.readable.getReader();
    const chunks = [];
    while (true) {{
        const {{done, value}} = await reader.read();
        if (done) break;
        chunks.push(value);
    }}
    const totalLength = chunks.reduce((sum, c) => sum + c.length, 0);
    const result = new Uint8Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {{
        result.set(chunk, offset);
        offset += chunk.length;
    }}
    return JSON.parse(new TextDecoder().decode(result));
}}"""

    # Transform search function: change eagerly-evaluated `const totals = {...}`
    # into a lazy `let totals = {}` + `function _initTotals(){...}` so that data
    # can be decoded asynchronously before totals are computed.
    import re as _re
    totals_match = _re.search(r'const totals = \{([^}]+)\};', search_function)
    if totals_match:
        totals_body = totals_match.group(1)
        search_function = search_function.replace(
            f'const totals = {{{totals_body}}};',
            f'let totals = {{}};\nfunction _initTotals() {{ totals = {{{totals_body}}}; }}'
        )

    # Data variable declared at top level, populated async, then app initializes
    js_parts.extend([
        data_decoder,
        "let data;",
        CORE_JAVASCRIPT.replace('{mission_info_json}', mission_info_json),
        render_functions,
        search_function,
        """_decodeData().then(d => {
    data = d;
    if (typeof _initTotals === 'function') _initTotals();
    updateStats();
    updateFlaggedCount();
    performSearch();
}).catch(err => {
    console.error('Failed to decode data:', err);
    document.body.innerHTML = '<div style="padding:40px;text-align:center;color:#666;"><h2>Error Loading App</h2><p>This browser may not support the required features. Please use a recent version of Chrome, Firefox, Edge, or Safari.</p></div>';
});""",
    ])
    javascript_code = '\n'.join(js_parts)

    # Fill template
    html = HTML_TEMPLATE.format(
        title=page_title,
        heading=heading,
        subtitle=entity_config['subtitle'],
        filter_buttons='\n                '.join(filter_buttons),
        stats_cards='\n            '.join(stats_cards),
        custom_styles='\n        '.join(custom_styles),
        javascript_code=javascript_code,
        welcome_features_html=welcome_features_html,
        mission_context=mission_context,
        expiration_notice=expiration_notice,
    )

    # Add preview banner
    if preview_mode:
        preview_banner = '''<div class="preview-banner">
    👁️ PREVIEW MODE <span>This app contains sample data for training purposes only</span>
</div>'''
        html = html.replace('<body>', f'<body>\n{preview_banner}')

    return html, mission_info


# ============== Main Generator Function ==============

def generate_mission_app(entity_config, field_config, render_functions, search_function,
                         generate_sample_data_fn=None, default_title='Data Review'):
    """Main entry point for mission generators"""
    parser = argparse.ArgumentParser(description=f'Generate {default_title} Mission App')
    parser.add_argument('input_file', help='Input Excel file (.xlsx)')
    parser.add_argument('output_file', help='Output HTML file')
    parser.add_argument('title', nargs='?', default=default_title, help='Mission app title')
    parser.add_argument('--preview', action='store_true', help='Generate Preview with synthetic sample data (72h expiration)')
    parser.add_argument('--preview-records', type=int, default=7, metavar='N', help='Sample records per entity (default: 7)')
    parser.add_argument('--active-from', metavar='DATETIME', help='When the app becomes active')
    parser.add_argument('--active-until', metavar='DATETIME', help='When the app expires')
    parser.add_argument('--session-duration', metavar='DURATION', help='Session expires N time after first open (e.g., 2h, 30m, 1d)')
    parser.add_argument('--no-expiration', action='store_true', help='Disable expiration (default for non-preview)')

    args = parser.parse_args()

    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)

    # Build expiration config
    expiration_config = {'enabled': False}
    session_config = None

    if args.session_duration:
        # Session-based expiration (dynamic, starts on first open)
        duration_ms, duration_display = parse_duration(args.session_duration)
        session_config = {
            'durationMs': duration_ms,
            'durationDisplay': duration_display,
        }
    elif args.preview and not args.active_from and not args.active_until and not args.no_expiration:
        active_from_dt = datetime.now()
        active_until_dt = active_from_dt + timedelta(hours=72)
        expiration_config['enabled'] = True
        expiration_config['activeFrom'] = int(active_from_dt.timestamp() * 1000)
        expiration_config['activeFromDisplay'] = active_from_dt.strftime('%B %d, %Y at %I:%M %p')
        expiration_config['activeUntil'] = int(active_until_dt.timestamp() * 1000)
        expiration_config['activeUntilDisplay'] = active_until_dt.strftime('%B %d, %Y at %I:%M %p')
    elif args.active_from or args.active_until:
        expiration_config['enabled'] = True
        if args.active_from:
            active_from_dt = parse_datetime(args.active_from)
            expiration_config['activeFrom'] = int(active_from_dt.timestamp() * 1000)
            expiration_config['activeFromDisplay'] = active_from_dt.strftime('%B %d, %Y at %I:%M %p')
        if args.active_until:
            active_until_dt = parse_datetime(args.active_until)
            expiration_config['activeUntil'] = int(active_until_dt.timestamp() * 1000)
            expiration_config['activeUntilDisplay'] = active_until_dt.strftime('%B %d, %Y at %I:%M %p')

    # Read data
    sheet_names = {e['sheet']: e['name'] for e in entity_config['entities']}
    print(f"Reading data from {args.input_file}...")
    real_data = read_excel_data(args.input_file, sheet_names)

    for entity in entity_config['entities']:
        count = len(real_data.get(entity['name'], []))
        print(f"  Found {count} {entity['label'].lower()}")

    # Generate synthetic data for preview
    if args.preview:
        print(f"\n👁️  PREVIEW MODE: Generating synthetic sample data...")
        if generate_sample_data_fn:
            data = generate_sample_data_fn(real_data, num_records=args.preview_records)
        else:
            print("  Warning: No sample data generator provided, using real data subset")
            data = {k: v[:args.preview_records] for k, v in real_data.items()}
        for entity in entity_config['entities']:
            count = len(data.get(entity['name'], []))
            print(f"  Generated {count} sample {entity['label'].lower()}")
    else:
        data = real_data

    # Generate HTML
    print("\nGenerating HTML...")
    html, mission_info = generate_html(
        data, entity_config, field_config, render_functions, search_function,
        args.title, expiration_config, session_config=session_config, preview_mode=args.preview
    )

    # Write output
    print(f"Writing to {args.output_file}...")
    Path(args.output_file).write_text(html, encoding='utf-8')

    # Write manifest
    manifest_file = Path(args.output_file).with_suffix('.manifest.json')
    manifest = {'output_file': args.output_file, 'input_file': args.input_file, **mission_info}
    if session_config:
        manifest['expiration'] = {
            'enabled': True,
            'type': 'session',
            'session_duration': session_config['durationDisplay'],
        }
    elif expiration_config['enabled']:
        manifest['expiration'] = {
            'enabled': True,
            'type': 'fixed',
            'active_from': expiration_config.get('activeFromDisplay'),
            'active_until': expiration_config.get('activeUntilDisplay'),
        }
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    file_size = Path(args.output_file).stat().st_size / 1024
    print(f"\nDone! Created {args.output_file} ({file_size:.1f} KB)")
    print(f"  Mission ID: {mission_info['mission_id']}")
    print(f"  Manifest: {manifest_file}")

    if args.preview:
        print(f"\n  👁️  PREVIEW MODE:")
        print(f"     Contains synthetic sample data")
        print(f"     Safe to distribute to all Consumers for training")

    if session_config:
        print(f"\n  ⏰ SESSION-BASED EXPIRATION:")
        print(f"     Duration:     {session_config['durationDisplay']} from first open")
        print(f"     Note:         Each browser gets its own independent session timer")
    elif expiration_config['enabled']:
        print(f"\n  ⏰ FIXED EXPIRATION:")
        if expiration_config.get('activeFromDisplay'):
            print(f"     Active from:  {expiration_config['activeFromDisplay']}")
        if expiration_config.get('activeUntilDisplay'):
            print(f"     Expires:      {expiration_config['activeUntilDisplay']}")
    elif not args.preview:
        print(f"\n  ℹ️  No expiration set (testing mode)")
