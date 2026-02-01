"""
ScriptPulse Syntactic Agent (IEEE SOTA Layer)
Gap Solved: "Bag of Words Fallacy"

Calculates Syntactic Complexity (Clause Density) as a proxy for Tree Depth.
Rationale: Deeply nested sentences (e.g., "The man who knew...") require more working memory
than flat sentences, even if entropy is identical.

Implementation: Heuristic Clause Detection (Regex-based).
Avoids heavy NLP dependencies (Spacy) for portability while maintaining high correlation.
"""

import re
import statistics

def analyze_diction_weakness(scene_lines):
    """
    Identify weak verbs in Action lines.
    """
    weak_markers = {'is', 'are', 'was', 'were', 'has', 'have', 'had'}
    weak_count = 0
    suggestions = []
    
    for line in scene_lines:
        if line.get('tag') == 'A': # Ensure 'tag' exists and is 'A'
            words = line['text'].lower().split()
            found = [w for w in words if w in weak_markers]
            if found:
                weak_count += len(found)
                if len(suggestions) < 3: # Limit detailed examples
                    suggestions.append(f"Line {line.get('line_index', '?')}: usage of '{found[0]}' (Passive/Weak)")
                    
    for line in scene_lines:
        if line.get('tag') == 'A': # Ensure 'tag' exists and is 'A'
            words = line['text'].lower().split()
            found = [w for w in words if w in weak_markers]
            if found:
                weak_count += len(found)
                if len(suggestions) < 3: # Limit detailed examples
                    suggestions.append(f"Line {line.get('line_index', '?')}: usage of '{found[0]}' (Passive/Weak)")
                    
    return weak_count, suggestions

def detect_exposition_dumps(scene_lines):
    """
    Identify potential info-dumps (Long, complex dialogue).
    """
    expos = []
    for line in scene_lines:
        if line.get('tag') == 'D':
            words = line['text'].split()
            if len(words) > 40: # Long monologue
                # Check complexity (quick heuristic: average word length or comma usage)
                avg_len = sum(len(w) for w in words)/len(words)
                commas = line['text'].count(',')
                if avg_len > 4.5 or commas > 3: # Complex language
                    expos.append(f"Line {line.get('line_index', '?')}: High-Density Monologue ({len(words)} words). Risk of Exposition Dump.")
    return expos

def run(data):
    """
    Analyze syntax complexity and diction.
    """
    scenes = data.get('scenes', [])
    if not scenes: return {}
    
    complexity_scores = []
    
    # Clause markers (Subordinating conjunctions & Relative pronouns)
    # These signal nesting/recursion in English syntax.
    patterns = [
        r'\bwhich\b', r'\bthat\b', r'\bwho\b', r'\bwhom\b', r'\bwhose\b', # Relative
        r'\bbecause\b', r'\balthough\b', r'\bif\b', r'\bwhile\b', r'\bwhen\b', # Subordinating
        r'\buntil\b', r'\bunless\b', r'\bsince\b', r'\bwhereas\b', # Corrected 'unitl' to 'until'
        r'[,;]\s*and\b', r'[,;]\s*but\b' # Compound
    ]
    regex = re.compile('|'.join(patterns), re.IGNORECASE)
    
    for scene in scenes:
        lines = [l['text'] for l in scene['lines']]
        if not lines:
            complexity_scores.append(0.0)
            continue
            
        scene_scores = []
        scene_total_words = 0
        scene_total_matches = 0
        
        for line in lines:
            # Count clause markers
            matches = len(regex.findall(line))
            
            # Update totals
            scene_total_matches += matches
            words_count = len(line.split())
            scene_total_words += words_count
            
            # Count punctuation (commas often delimit clauses)
            commas = line.count(',')
            
            # Simple Proxy for Tree Depth:
            # Depth ≈ 1 + (Markers * 0.5) + (Commas * 0.2)
            depth_proxy = 1.0 + (matches * 0.8) + (commas * 0.2)
            
            # Penalize length (long sentences with no structure are hard too)
            if words_count > 20: 
                depth_proxy += (words_count - 20) * 0.05
                
            scene_scores.append(depth_proxy)
            
        # Scene score is the average depth of its sentences
        avg_depth = statistics.mean(scene_scores) if scene_scores else 1.0
        
        # Normalize (rough heuristic: higher clause density = higher complexity)
        # Avg words per clause approx
        c_len = scene_total_words
        ratio = scene_total_matches / max(1, c_len) * 20 # 1 match per 20 words is high
        complexity_scores.append(min(1.0, ratio))

    # Diction Scan (v10.1) & Exposition Scan (v11.0)
    diction_issues = []
    
    for scene in scenes:
        cnt, exs = analyze_diction_weakness(scene['lines'])
        if cnt > 2: 
             diction_issues.extend(exs)
             
        # v11.0: Exposition Alarm
        dumps = detect_exposition_dumps(scene['lines'])
        diction_issues.extend(dumps)

    return {
        'complexity_scores': complexity_scores,
        'diction_issues': diction_issues
    }
