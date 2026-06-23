#!/usr/bin/env python3
import os
import sys

# Ensure project root is in path
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from scriptpulse.pipeline import runner
from scriptpulse.reporters import writer_report, studio_report, print_summary
import app.streamlit_utils as stu

def main():
    print("Generating re-themed PDF reports for 'The Godfather'...")
    
    # Read sample script
    filepath = os.path.join(ROOT_DIR, "data", "samples", "Godfather, The.txt")
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        
    # Run pipeline
    print("Running pipeline (Drama)...")
    report = runner.run_pipeline(text, genre='Drama')
    
    # Title and genre
    title = "The Godfather"
    genre = "drama"
    
    # 1. Writer Report PDF
    print("Generating Writer Report PDF...")
    md_content = writer_report.generate_writer_report(report, title=title, genre=genre)
    html_writer = stu.convert_md_report_to_html(md_content, title=title)
    pdf_writer_bytes = stu.convert_html_to_pdf(html_writer)
    writer_pdf_path = os.path.join(ROOT_DIR, "ScriptPulse_Writer_drama.pdf")
    with open(writer_pdf_path, "wb") as f:
        f.write(pdf_writer_bytes)
    print(f"Saved Writer Report to {writer_pdf_path}")
    
    # 2. Studio Coverage PDF
    print("Generating Studio Coverage PDF...")
    html_studio = studio_report.generate_report(report, script_title=title, lens="Story Editor")
    pdf_studio_bytes = stu.convert_html_to_pdf(html_studio)
    studio_pdf_path = os.path.join(ROOT_DIR, "ScriptPulse_Studio_drama.pdf")
    with open(studio_pdf_path, "wb") as f:
        f.write(pdf_studio_bytes)
    print(f"Saved Studio Coverage to {studio_pdf_path}")
    
    # 3. One-Page Summary PDF
    print("Generating One-Page Summary PDF...")
    html_summary = print_summary.generate_print_summary(report, script_title=title)
    pdf_summary_bytes = stu.convert_html_to_pdf(html_summary)
    summary_pdf_path = os.path.join(ROOT_DIR, "ScriptPulse_Summary_drama.pdf")
    with open(summary_pdf_path, "wb") as f:
        f.write(pdf_summary_bytes)
    print(f"Saved Summary to {summary_pdf_path}")
    
    # 4. Clean legacy files
    print("Cleaning legacy files...")
    for legacy_ext, prefix in [("md", "Writer"), ("html", "Studio"), ("html", "Summary")]:
        legacy_path = os.path.join(ROOT_DIR, f"ScriptPulse_{prefix}_drama.{legacy_ext}")
        if os.path.exists(legacy_path):
            try:
                os.remove(legacy_path)
                print(f"Removed legacy file {legacy_path}")
            except Exception as e:
                print(f"Could not remove {legacy_path}: {e}")
                
    print("All reports compiled successfully as PDFs and saved to the workspace root!")

if __name__ == "__main__":
    main()
