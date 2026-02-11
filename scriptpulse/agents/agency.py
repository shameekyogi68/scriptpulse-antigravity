
try:
    import networkx as nx
except ImportError:
    nx = None
    print("[Warning] 'networkx' not found. Running Agency in SIMULATION MODE (Degree Centrality).")

import collections

def run(input_data):
    """
    vNext.9 Agency Analysis Agent.
    
    Objective: Measure Character Agency (Power/Influence) rather than just Presence (Line Counts).
    """
    
    # 1. Construct Interaction Graph (Global)
    # Using simple dict for fallback if NX missing
    adjacency = collections.defaultdict(int) # (src, dst) -> weight
    nodes = set()
    
    scenes = input_data.get('scenes', [])
    
    if not scenes:
        return {'error': 'No input scenes'}
        
    for scene in scenes:
        speakers = []
        for line in scene['lines']:
            if line['tag'] == 'C':
                name = line['text'].split('(')[0].strip()
                if name:
                    speakers.append(name)
                    nodes.add(name)
        
        # Add edges for turn-taking
        for k in range(len(speakers) - 1):
            src = speakers[k]
            dst = speakers[k+1]
            if src != dst:
                adjacency[(src, dst)] += 1
                
    if not nodes:
         return {'agency_metrics': []}
        
    # 2. Calculate Centrality Metrics
    if nx:
        G = nx.DiGraph()
        for (src, dst), weight in adjacency.items():
            G.add_edge(src, dst, weight=weight)
            
        try:
            eigenvector = nx.eigenvector_centrality(G, max_iter=1000, weight='weight')
            # Normalize
            max_val = max(eigenvector.values()) if eigenvector else 1
            centrality_map = {k: v/max_val for k, v in eigenvector.items()}
        except:
            centrality_map = {n: 0.0 for n in nodes}
    else:
        # Fallback: Degree Centrality (Manual)
        # Degree = Sum of outgoing + incoming weights
        degrees = collections.defaultdict(int)
        for (src, dst), weight in adjacency.items():
            degrees[src] += weight
            degrees[dst] += weight
            
        max_degree = max(degrees.values()) if degrees else 1
        centrality_map = {n: degrees[n]/max_degree for n in nodes}
    
    # 3. Analyze "Decision Verbs" (Agency Proxy in Dialogue)
    # Simple heuristic: Count active verbs in dialogue lines
    agency_verbs = ["decide", "choose", "will", "must", "order", "stop", "save", "kill", "fight"]
    passive_verbs = ["wait", "watch", "listen", "see", "hear", "feel", "think", "wonder"]
    
    verb_counts = collections.defaultdict(lambda: {"active": 0, "passive": 0})
    
    for scene in scenes:
        current_char = None
        for line in scene['lines']:
            if line['tag'] == 'C':
                current_char = line['text'].split('(')[0].strip()
            elif line['tag'] == 'D' and current_char:
                text = line['text'].lower()
                for v in agency_verbs:
                    if v in text: verb_counts[current_char]["active"] += 1
                for v in passive_verbs:
                    if v in text: verb_counts[current_char]["passive"] += 1
    
    agency_report = []
    
    for char in nodes:
        stats = verb_counts[char]
        total_verbs = stats["active"] + stats["passive"]
        # Smoothing: Add 1 to denominator to avoid div/0
        verb_ratio = stats["active"] / (total_verbs if total_verbs > 0 else 1)
        
        # Normalize Centrality relative to max in graph
        norm_cent = centrality_map.get(char, 0.0)
        
        # Composite Agency Score
        # Agency = (Relative Centrality * 0.6) + (VerbRatio * 0.4)
        agency_score = (norm_cent * 0.6) + (verb_ratio * 0.4)
        
        agency_report.append({
            'character': char,
            'agency_score': round(agency_score, 3),
            'centrality': round(norm_cent, 3),
            'active_verb_ratio': round(verb_ratio, 2),
            'classification': "High Agency" if agency_score > 0.4 else "Passive"
        })
        
    # Sort by Agency
    agency_report.sort(key=lambda x: x['agency_score'], reverse=True)
    
    return {'agency_metrics': agency_report}

if __name__ == "__main__":
    print(run({'features': [{}]}))
