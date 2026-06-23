# MODULE: streamlit_utils.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import streamlit as st
import streamlit.components.v1 as components

def check_integrity():
    """Validates startup state."""
    return True, "OK"

def sync_safety_state():
    """Syncs session state."""
    if 'safe_mode_active' not in st.session_state:
        st.session_state['safe_mode_active'] = False

def check_upload_size(uploaded_file):
    """Guards against excessively large files and empty files."""
    if uploaded_file:
        if uploaded_file.size == 0:
            st.error("Uploaded file is empty. Please check the file and try again.")
            return False
        if uploaded_file.size > 20 * 1024 * 1024:
            st.error("File too large. Please upload a script under 20MB.")
            return False
    return True

def render_operator_panel(prev_run=None):
    """Renders advanced control panel if needed."""
    return False, False # shadow_mode, high_accuracy_mode

def check_input_length(text):
    """Guards against excessively large paste inputs."""
    if text and len(text) > 500000:
        st.error("Pasted text is too long. Please upload as a file instead.")
        return False
    return True

def inject_scroll_to(selector: str, block: str = "center"):
    """Injects a smooth scroll script targeting the parent document selector."""
    html_scroll = f"""
    <script>
        (function() {{
            const scrollIntoViewWithRetry = (sel, ret, del) => {{
                try {{
                    const parentDoc = window.parent.document;
                    const target = parentDoc.querySelector(sel);
                    if (target) {{
                        target.scrollIntoView({{ behavior: 'smooth', block: '{block}' }});
                    }} else if (ret > 0) {{
                        setTimeout(() => scrollIntoViewWithRetry(sel, ret - 1, del), del);
                    }}
                }} catch (e) {{
                    console.error("Scroll failed:", e);
                }}
            }};
            scrollIntoViewWithRetry('{selector}', 15, 100);
        }})();
    </script>
    """
    components.html(html_scroll, height=0, width=0)


def convert_html_to_pdf(html_content: str) -> bytes:
    """
    Compiles HTML content into a PDF using headless Google Chrome.
    """
    import tempfile
    import os
    import subprocess
    
    # 1. Create temp files
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as html_file:
        html_file.write(html_content.encode("utf-8"))
        html_path = html_file.name
        
    pdf_path = html_path.replace(".html", ".pdf")
    
    try:
        # 2. Run Google Chrome CLI in headless mode
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 3. Read compiled PDF bytes
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        return pdf_bytes
        
    finally:
        # 4. Clean up temp files
        if os.path.exists(html_path):
            try:
                os.remove(html_path)
            except Exception:
                pass
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception:
                pass


def convert_md_report_to_html(md_content: str, title: str) -> str:
    """
    Converts a ScriptPulse Writer Markdown report (containing embedded HTML blocks)
    into a fully styled HTML page suitable for PDF rendering.
    """
    import re
    
    # Helper to clean markdown bold, italic, code
    def clean_inline(text):
        # bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # italic
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # code
        text = re.sub(r'`(.*?)`', r'<code style="background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px; font-family: \'JetBrains Mono\', monospace; font-size: 0.9em; color: #00C853;">\1</code>', text)
        return text

    # Pre-parse: split into blocks by double newlines
    blocks = md_content.split("\n\n")
    html_blocks = []
    
    in_table = False
    table_lines = []
    
    in_list = False
    list_items = []
    
    in_quote = False
    quote_lines = []

    def flush_table():
        nonlocal in_table, table_lines
        if not table_lines:
            return ""
        # Render table
        thead = ""
        tbody = ""
        is_first = True
        for line in table_lines:
            # check if separator
            if re.match(r'^\s*\|?\s*:?-+:?\s*\|', line) or '---' in line:
                continue
            cells = [c.strip() for c in line.split("|")]
            # remove leading/trailing empty cells
            if cells and cells[0] == "":
                cells = cells[1:]
            if cells and cells[-1] == "":
                cells = cells[:-1]
            if not cells:
                continue
            
            row_html = "<tr>"
            for cell in cells:
                cell_val = clean_inline(cell)
                if is_first:
                    row_html += f'<th style="text-align: left; padding: 12px; background: rgba(0,0,0,0.25); font-size: 11px; text-transform: uppercase; color: #9E9E9E; font-weight: 700; letter-spacing: 0.05em;">{cell_val}</th>'
                else:
                    row_html += f'<td style="padding: 14px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #E0E0E0; font-size: 13.5px;">{cell_val}</td>'
            row_html += "</tr>"
            
            if is_first:
                thead = f"<thead>{row_html}</thead>"
                is_first = False
            else:
                tbody += row_html
                
        table_lines = []
        in_table = False
        return f'<table style="width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.08);">{thead}<tbody>{tbody}</tbody></table>'

    def flush_list():
        nonlocal in_list, list_items
        if not list_items:
            return ""
        items_html = "".join([f'<li style="margin-bottom: 8px; font-size: 14px;">{clean_inline(i)}</li>' for i in list_items])
        list_items = []
        in_list = False
        return f'<ul style="padding-left: 20px; margin: 15px 0; color: #E0E0E0;">{items_html}</ul>'

    def flush_quote():
        nonlocal in_quote, quote_lines
        if not quote_lines:
            return ""
        # Determine if it is a callout box
        content = " ".join(quote_lines)
        quote_lines = []
        in_quote = False
        
        # Check GitHub-style alerts
        alert_style = 'background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-left: 4px solid #9B51E0;'
        alert_label = "NOTE"
        
        if '[!IMPORTANT]' in content:
            alert_style = 'background: rgba(155, 81, 224, 0.04); border: 1px solid rgba(155, 81, 224, 0.15); border-left: 4px solid #9B51E0;'
            alert_label = "📌 IMPORTANT"
            content = content.replace('[!IMPORTANT]', '').strip()
        elif '[!CAUTION]' in content:
            alert_style = 'background: rgba(255, 51, 102, 0.04); border: 1px solid rgba(255, 51, 102, 0.15); border-left: 4px solid #FF3366;'
            alert_label = "⚠️ CAUTION"
            content = content.replace('[!CAUTION]', '').strip()
        elif '[!WARNING]' in content:
            alert_style = 'background: rgba(255, 112, 67, 0.04); border: 1px solid rgba(255, 112, 67, 0.15); border-left: 4px solid #FF7043;'
            alert_label = "⚠️ WARNING"
            content = content.replace('[!WARNING]', '').strip()
            
        content = clean_inline(content)
        return f'<div style="{alert_style} border-radius: 8px; padding: 16px 20px; margin-bottom: 20px; font-family:\'Inter\',sans-serif; color:#E0E0E0;"><div style="font-size: 11px; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 6px; text-transform: uppercase;">{alert_label}</div>{content}</div>'

    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Is it an HTML block?
        if block.startswith("<div") or block.startswith("<!--") or block.startswith("<span") or block.endswith("</div>"):
            # Flush any pending structures
            if in_table: html_blocks.append(flush_table())
            if in_list: html_blocks.append(flush_list())
            if in_quote: html_blocks.append(flush_quote())
            # Keep HTML as is
            html_blocks.append(block)
            continue
            
        # Is it a heading?
        if block.startswith("## "):
            if in_table: html_blocks.append(flush_table())
            if in_list: html_blocks.append(flush_list())
            if in_quote: html_blocks.append(flush_quote())
            heading_text = block[3:].strip()
            heading_text = clean_inline(heading_text)
            h2_html = f'<h2 style="font-family: \'Outfit\', sans-serif; font-size: 1.5rem; font-weight: 700; color: white; margin-top: 2.2rem; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px;">{heading_text}</h2>'
            html_blocks.append(h2_html)
            continue
            
        # Is it a horizontal rule?
        if block == "---" or block.startswith("---"):
            if in_table: html_blocks.append(flush_table())
            if in_list: html_blocks.append(flush_list())
            if in_quote: html_blocks.append(flush_quote())
            html_blocks.append('<hr style="border: 0; height: 1px; background: rgba(255,255,255,0.08); margin: 30px 0;"/>')
            continue

        # Split block lines to inspect line-by-line
        lines = block.split("\n")
        first_line = lines[0].strip()
        
        # Is it a table?
        if first_line.startswith("|"):
            if in_list: html_blocks.append(flush_list())
            if in_quote: html_blocks.append(flush_quote())
            in_table = True
            table_lines.extend(lines)
            continue
            
        # Is it a list?
        if first_line.startswith("- ") or first_line.startswith("* "):
            if in_table: html_blocks.append(flush_table())
            if in_quote: html_blocks.append(flush_quote())
            in_list = True
            for line in lines:
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    list_items.append(line[2:])
                else:
                    if list_items:
                        list_items[-1] += " " + line
            continue
            
        # Is it a blockquote?
        if first_line.startswith(">"):
            if in_table: html_blocks.append(flush_table())
            if in_list: html_blocks.append(flush_list())
            in_quote = True
            for line in lines:
                line = line.strip()
                if line.startswith(">"):
                    quote_lines.append(line[1:].strip())
                else:
                    quote_lines.append(line)
            continue

        # Regular paragraph
        if in_table: html_blocks.append(flush_table())
        if in_list: html_blocks.append(flush_list())
        if in_quote: html_blocks.append(flush_quote())
        
        cleaned_paragraph = clean_inline(block)
        p_html = f'<p style="font-size: 14.5px; line-height: 1.7; color: #E0E0E0; margin-bottom: 16px;">{cleaned_paragraph}</p>'
        html_blocks.append(p_html)

    # Final flush
    if in_table: html_blocks.append(flush_table())
    if in_list: html_blocks.append(flush_list())
    if in_quote: html_blocks.append(flush_quote())
    
    html_content = "\n".join(html_blocks)
    
    # Wrap in shell
    shell = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: letter;
            margin: 15mm;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #121212;
            color: #E0E0E0;
            line-height: 1.65;
            margin: 0;
            padding: 0;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        h1, h2, h3, h4 {{
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: white;
            margin-top: 0;
        }}
        tr, p, ul, li, div, h2, h3, blockquote {{
            page-break-inside: avoid;
            break-inside: avoid;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""
    return shell

