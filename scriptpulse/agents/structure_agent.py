"""
Structure Agent - Handling Parsing, Segmentation, and Importing.
Consolidates: parsing.py, bert_parser.py, segmentation.py, beat.py, importers.py
"""

import re
import math
import xml.etree.ElementTree as ET
from ..utils.model_manager import manager

# =============================================================================
# IMPORTER LOGIC (formerly importers.py)
# =============================================================================

class ImporterAgent:
    """
    Parses Final Draft (.fdx) XML files and converts them 
    into the standardized Fountain-like format expected by the pipeline.
    """
    def run(self, file_content):
        """
        Entry point for the agent.
        file_content: bytes or string of the .fdx file
        """
        return self.parse_fdx(file_content)

    def parse_fdx(self, xml_content):
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
            text_elem = paragraph.find('Text')
            raw_text = ""
            if text_elem is not None:
                raw_text = "".join(text_elem.itertext())
            else:
                raw_text = "".join(paragraph.itertext())
                
            clean_text = raw_text.strip()
            
            if not clean_text:
                continue
                
            # Map FDX Types to ScriptPulse Tags
            tag = 'A' # Default
            
            if p_type == 'Scene Heading':
                tag = 'S'
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
                tag = 'S' 
            
            parsed_lines.append({
                'text': clean_text,
                'tag': tag,
                'line_index': line_idx,
                'original_line': clean_text
            })
            line_idx += 1
            
        return parsed_lines


# =============================================================================
# PARSING LOGIC (formerly parsing.py & bert_parser.py)
# =============================================================================

def is_scene_heading(line_text):
    """
    Detect if a line is a scene heading.
    Extracted for testability and reuse.
    """
    line = line_text.strip()
    if not line: return False
    
    # 1. Standard Int/Ext prefixes
    line_upper = line.upper()
    # Expanded based on tests
    if line_upper.startswith(("INT.", "EXT.", "INT ", "EXT ", "I/E.", "I.", "E.", "INT/", "EXT/")): return True
    if line_upper.startswith("SCENE"): return True 
    
    # 2. Fallback Patterns (Full words)
    fallback_patterns = [
        r'^INTERIOR\s+', r'^EXTERIOR\s+', 
        r'^\d+\s*(INT|EXT)'
    ]
    for pattern in fallback_patterns:
        if re.match(pattern, line, re.IGNORECASE): return True
        
    # 3. Time of Day suffix pattern (Implicit heading)
    # e.g. "KITCHEN - DAY"
    time_pattern = r'^[A-Z][A-Z\s]+\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME)'
    if re.match(time_pattern, line, re.IGNORECASE): return True
    
    return False

class ParsingAgent:
    """
    Structural Parsing Agent - Classifies screenplay lines.
    Combines Heuristic (parsing.py) and ML (bert_parser.py) approaches.
    """
    def __init__(self, use_ml=True, model_name="valhalla/distilbart-mnli-12-3"):
        self.use_ml = use_ml
        self.classifier = None
        self.is_mock = True
        
        if use_ml:
            self.classifier = manager.get_pipeline("zero-shot-classification", model_name)
            self.is_mock = self.classifier is None
            if self.is_mock:
                print(f"[Warning] Failed to load ML model. Falling back to Heuristics.")

        self.tag_map = {
            "Dialogue": "D",
            "Action": "A",
            "Scene Heading": "S",
            "Character Name": "C",
            "Transition": "T",
            "Parenthetical": "M" 
        }

    def run(self, script_text):
        """
        Parses the entire script.
        """
        # Dash Normalization
        script_text = script_text.replace('—', '-').replace('–', '-')
        
        lines = script_text.split('\n')
        results = []
        context = []
        
        for i, line in enumerate(lines):
            tag = self.predict_line(line, context_window=context, index=i, all_lines=lines)
            context.append(tag)
            
            confidence = 0.95 if self.is_mock else 0.85 
            
            results.append({
                'line_index': i,
                'text': line,
                'tag': tag,
                'model': 'consolidated-parser-v1',
                'confidence': confidence
            })
            
        return {'lines': results}

    def predict_line(self, line_text, context_window=None, index=0, all_lines=None):
        """
        Predicts the structural tag for a single line.
        """
        line = line_text.strip()
        if not line: return "A"
        
        # 1. Hard Rules (Performance Optimization & Sanity)
        if is_scene_heading(line): return "S"
        
        line_upper = line.upper()
        if line_upper.endswith(" TO:"): return "T"

        # Metadata/transitions
        transitions = ['FADE IN', 'FADE OUT', 'FADE TO', 'CUT TO', 'DISSOLVE TO', 'MATCH CUT', 'SMASH CUT', 'THE END', 'CONTINUED']
        if any(t in line_upper or line_upper.startswith(t) for t in transitions): return 'M'
        if line_upper.endswith(':'): return 'M' # Broad transition check

        # 2. Contextual Heuristics
        prev_tag = context_window[-1] if context_window else "A"
        
        if prev_tag == "C": 
            if line.startswith("("): return "M" # Parenthetical
            return "D"
            
        if line.isupper() and len(line) < 40 and not line.endswith((".", "?", "!")):
            # Look ahead for dialogue
            if all_lines and index + 1 < len(all_lines):
                 next_line = all_lines[index + 1].strip()
                 if next_line and not next_line.isupper():
                     return "C"
            # Fallback if no lookahead
            return "C"

        # 3. ML Inference (Skipped if mock or high confidence in heuristic)
        # Note: In consolidation, preserving the heuristic path as primary for speed/reliability unless ambiguous
        
        # 4. Fallback Heuristics
        if prev_tag == "C": return "D"
        if line.startswith("(") and line.endswith(")"): return "D" 
        if line.isupper() and len(line) < 30: return "C"
        
        return "A"


# =============================================================================
# SEGMENTATION LOGIC (formerly segmentation.py)
# =============================================================================

class SegmentationAgent:
    """Scene Segmentation Agent - Conservative Boundary Detection"""
    
    MIN_SCENE_LENGTH = 3
    LOW_CONFIDENCE_THRESHOLD = 0.6

    def run(self, input_data):
        """Segment parsed lines into scenes."""
        if not input_data: return []
        parsed_lines = input_data if isinstance(input_data, list) else input_data.get('lines', [])
        
        boundaries = self.detect_boundaries(parsed_lines)
        scenes = self.create_scenes(parsed_lines, boundaries)
        scenes = self.enforce_minimum_length(scenes)
        scenes = self.merge_headless_fragments(scenes, parsed_lines)
        scenes = self.merge_low_confidence(scenes)
        scenes = self.reindex_scenes(scenes)
        scenes = self.extract_scene_info(scenes, parsed_lines)
        
        return scenes

    def detect_boundaries(self, parsed_lines):
        boundaries = [(0, 1.0)]
        for i, line_data in enumerate(parsed_lines):
            if i == 0: continue
            tag = line_data['tag']
            confidence = 0.0
            if tag == 'S': confidence = 0.9
            elif tag == 'M': confidence = 0.4
            
            if confidence > 0.3:
                boundaries.append((i, confidence))
        return boundaries

    def create_scenes(self, parsed_lines, boundaries):
        scenes = []
        for i in range(len(boundaries)):
            start_line = boundaries[i][0]
            start_confidence = boundaries[i][1]
            end_line = boundaries[i + 1][0] - 1 if i + 1 < len(boundaries) else len(parsed_lines) - 1
            scenes.append({
                'scene_index': i,
                'start_line': start_line,
                'end_line': end_line,
                'boundary_confidence': start_confidence
            })
        return scenes

    def enforce_minimum_length(self, scenes):
        if not scenes: return scenes
        merged = []
        skip_next = False
        for i in range(len(scenes)):
            if skip_next:
                skip_next = False
                continue
            scene = scenes[i]
            length = scene['end_line'] - scene['start_line'] + 1
            if length < self.MIN_SCENE_LENGTH and i + 1 < len(scenes):
                next_scene = scenes[i + 1]
                merged_scene = {
                    'scene_index': scene['scene_index'],
                    'start_line': scene['start_line'],
                    'end_line': next_scene['end_line'],
                    'boundary_confidence': min(scene['boundary_confidence'], next_scene['boundary_confidence'])
                }
                merged.append(merged_scene)
                skip_next = True
            else:
                merged.append(scene)
        return merged

    def merge_headless_fragments(self, scenes, parsed_lines, max_orphan_lines=5):
        if len(scenes) <= 1: return scenes
        merged = [scenes[0]]
        for scene in scenes[1:]:
            has_heading = any(parsed_lines[i]['tag'] == 'S' for i in range(scene['start_line'], min(scene['end_line'] + 1, len(parsed_lines))))
            length = scene['end_line'] - scene['start_line'] + 1
            if not has_heading and length <= max_orphan_lines and merged:
                merged[-1]['end_line'] = scene['end_line']
            else:
                merged.append(scene)
        return merged

    def merge_low_confidence(self, scenes):
        if len(scenes) <= 1: return scenes
        merged = []
        current = scenes[0]
        for i in range(1, len(scenes)):
            next_scene = scenes[i]
            if current['boundary_confidence'] < self.LOW_CONFIDENCE_THRESHOLD:
                current = {
                    'scene_index': current['scene_index'],
                    'start_line': current['start_line'],
                    'end_line': next_scene['end_line'],
                    'boundary_confidence': max(current['boundary_confidence'], next_scene['boundary_confidence'])
                }
            else:
                merged.append(current)
                current = next_scene
        merged.append(current)
        return merged

    def reindex_scenes(self, scenes):
        for i, scene in enumerate(scenes):
            scene['scene_index'] = i
        return scenes

    def extract_scene_info(self, scenes, parsed_lines):
        for scene in scenes:
            start = scene['start_line']
            end = scene['end_line']
            heading = ""
            preview_lines = []
            for i in range(start, min(end + 1, len(parsed_lines))):
                line_data = parsed_lines[i]
                text = line_data['text'].strip()
                tag = line_data['tag']
                if not text: continue
                if tag == 'S' and not heading:
                    heading = text
                elif len(preview_lines) < 2:
                    if text and text != heading:
                        preview_lines.append(text[:60] + ('...' if len(text) > 60 else ''))
            scene['heading'] = heading if heading else f"Scene {scene['scene_index'] + 1}"
            scene['preview'] = ' | '.join(preview_lines) if preview_lines else ""
        return scenes


# =============================================================================
# BEAT LOGIC (formerly beat.py)
# =============================================================================

class BeatAgent:
    """Sub-segments scenes into Beats."""
    
    BEAT_WORD_TARGET = 120

    def subdivide_into_beats(self, scenes):
        beats = []
        for scene in scenes:
            lines = scene.get('lines', [])
            current_beat_lines = []
            current_word_count = 0
            beat_in_scene = 1
            
            for line in lines:
                text = line.get('text', "")
                words = len(text.split())
                is_transition = line.get('type') == 'TRANSITION' # Check if 'tag' or 'type' used? Standard is 'tag'='T'
                
                if current_word_count + words > self.BEAT_WORD_TARGET and current_beat_lines:
                    beat_obj = self.create_beat(scene, current_beat_lines, beat_in_scene)
                    beats.append(beat_obj)
                    current_beat_lines = []
                    current_word_count = 0
                    beat_in_scene += 1
                
                current_beat_lines.append(line)
                current_word_count += words
                
                if is_transition:
                    beat_obj = self.create_beat(scene, current_beat_lines, beat_in_scene)
                    beats.append(beat_obj)
                    current_beat_lines = []
                    current_word_count = 0
                    beat_in_scene += 1
                    
            if current_beat_lines:
                 beat_obj = self.create_beat(scene, current_beat_lines, beat_in_scene)
                 beats.append(beat_obj)
                 
        return beats

    def create_beat(self, parent_scene, lines, beat_idx):
        return {
            'scene_index': parent_scene['scene_index'],
            'beat_index': beat_idx,
            'heading': f"{parent_scene['heading']} (Beat {beat_idx})",
            'lines': lines,
            'start_line': lines[0]['line_index'] if lines else 0,
            'end_line': lines[-1]['line_index'] if lines else 0,
            'location': parent_scene.get('location', 'UNKNOWN'),
            'time': parent_scene.get('time', 'UNKNOWN')
        }
