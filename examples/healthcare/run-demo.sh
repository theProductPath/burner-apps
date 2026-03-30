#!/bin/bash
# Healthcare Mission App Demo Runner
# Opens files in sequence for live demo

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🏥 Healthcare Mission App Demo"
echo "=============================="
echo ""

# Step 1: Open the demo script
echo "📋 Step 1: Opening demo script..."
open "$SCRIPT_DIR/DEMO_SCRIPT.md" 2>/dev/null || xdg-open "$SCRIPT_DIR/DEMO_SCRIPT.md" 2>/dev/null
echo "   Opened DEMO_SCRIPT.md"
echo ""

# Step 2: Open the dataset
echo "📊 Step 2: Opening sample dataset..."
open "$SCRIPT_DIR/Healthcare_Sample_Data.xlsx" 2>/dev/null || xdg-open "$SCRIPT_DIR/Healthcare_Sample_Data.xlsx" 2>/dev/null
echo "   Opened Healthcare_Sample_Data.xlsx"
echo ""

# Step 3: Open the review app
echo "🌐 Step 3: Opening the burner app..."
open "$SCRIPT_DIR/healthcare_review.html" 2>/dev/null || xdg-open "$SCRIPT_DIR/healthcare_review.html" 2>/dev/null
echo "   Opened healthcare_review.html in browser"
echo ""

# Step 4: Wait for confirmation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "📄 Press Enter to open the sample flagged report... "
echo ""

# Open the flagged sample
echo "📄 Step 4: Opening sample flagged report (stakeholder view)..."
open "$SCRIPT_DIR/healthcare_flagged_sample.md" 2>/dev/null || xdg-open "$SCRIPT_DIR/healthcare_flagged_sample.md" 2>/dev/null
echo "   Opened healthcare_flagged_sample.md"
echo ""

# Step 5: Wait for confirmation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "📊 Press Enter to open the creator report (session analytics)... "
echo ""

# Open the creator report
echo "📊 Step 5: Opening creator report..."
open "$SCRIPT_DIR/healthcare_creator_report_sample.md" 2>/dev/null || xdg-open "$SCRIPT_DIR/healthcare_creator_report_sample.md" 2>/dev/null
echo "   Opened healthcare_creator_report_sample.md"
echo ""

echo "✅ Demo complete. See DEMO_SCRIPT.md for talking points."
