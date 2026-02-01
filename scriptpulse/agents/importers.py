"""
ScriptPulse FDX Importer Agent (Market Layer)
Gap Solved: "The Caveman Importer"

Parses Final Draft (.fdx) XML files and converts them 
into the standardized Fountain-like format expected by the pipeline.
"""

import xml.etree.ElementTree as ET
import re

class FdxImporter:
    def __init__(self):
        pass
        
    def parse(self, xml_content):
        """
        Parse FDX XML string into standardized line dictionaries.
        Returns: list of dicts [{'text': '...', 'tag': 'S/A/C/D', 'line_index': i}]
        """
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return []
            
        parsed_lines = []
        line_idx = 0
        
        # FDX Structure: <FinalDraft> -> <Content> -> <Paragraph>
        content = root.find('Content')
        if content is None:
            return []
            
        for paragraph in content.findall('Paragraph'):
            p_type = paragraph.get('Type', 'Action')
            
            # Extract Text
            # Text can be in <Text> child or mixed content
            text_elem = paragraph.find('Text')
            raw_text = ""
            if text_elem is not None:
                # FDX text styles are often nested, but basic text is usually simple
                # We need to handle styles if possible, but raw text is priority
                raw_text = "".join(text_elem.itertext())
            else:
                # Try direct text if no Text tag (unlikely in valid FDX but safe)
                raw_text = "".join(paragraph.itertext())
                
            clean_text = raw_text.strip()
            
            if not clean_text:
                continue
                
            # Map FDX Types to ScriptPulse Tags
            # S=Scene, A=Action, C=Character, D=Dialogue, P=Parenthetical
            tag = 'A' # Default
            
            if p_type == 'Scene Heading':
                tag = 'S'
                # Ensure uppercase for standard
                clean_text = clean_text.upper()
            elif p_type == 'Character':
                tag = 'C'
                clean_text = clean_text.upper()
            elif p_type == 'Dialogue':
                tag = 'D'
            elif p_type == 'Parenthetical':
                tag = 'P'
            elif p_type == 'Transition':
                tag = 'T'
            elif p_type == 'Shot':
                tag = 'S' # Treat shots as scene boundaries or sub-headings? Usually A or S.
                          # Let's map to S to ensure segmentation happens if visual focus shifts.
            
            parsed_lines.append({
                'text': clean_text,
                'tag': tag,
                'line_index': line_idx,
                'original_line': clean_text # For reference
            })
            line_idx += 1
            
        return parsed_lines

def run(file_content):
    """
    Entry point for the agent.
    file_content: bytes or string of the .fdx file
    """
    importer = FdxImporter()
    return importer.parse(file_content)
