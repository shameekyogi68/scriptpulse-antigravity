"""
ScriptPulse Research Baselines (Control Group)
Gap Solved: "Comparative Benchmark"

Implements a standard Rule-Based Sentiment Analysis (VADER-style) 
to act as a baseline for comparing ScriptPulse's Cognitive Trace.
"""

import math

def run_baseline_sentiment(scenes):
    """
    Run a standard sentiment analysis on the scenes.
    Returns a trace of Sentiment scores (-1.0 to 1.0).
    
    This mimics VADER/TextBlob logic:
    - BoW (Bag of Words) approach.
    - Intensifiers (very, really).
    - Negations (not, never).
    """
    trace = []
    
    # 1. Lexicons (Standard Academic Baselines)
    pos_words = {
        'good', 'great', 'excellent', 'amazing', 'happy', 'joy', 'love', 'beautiful', 
        'best', 'win', 'success', 'vibrant', 'light', 'hero', 'safe', 'relief',
        'calm', 'peace', 'hope', 'laugh', 'smile', 'fun', 'yes', 'alive'
    }
    
    neg_words = {
        'bad', 'terrible', 'horrible', 'worst', 'sad', 'pain', 'death', 'kill', 
        'die', 'dead', 'fear', 'afraid', 'dark', 'evil', 'danger', 'risk', 
        'loss', 'fail', 'no', 'stop', 'hate', 'enemy', 'fight', 'hurt', 'cry'
    }
    
    intensifiers = {
        'very', 'really', 'extremely', 'absolutely', 'completely', 'so'
    }
    
    negators = {
        'not', 'never', 'no', 'neither', 'nor', 'cannot', 'cant', 'wont', 'dont'
    }
    
    for scene in scenes:
        lines = scene.get('lines', [])
        text = " ".join([l['text'] for l in lines]).lower()
        words = text.replace('.', '').replace(',', '').split()
        
        score = 0.0
        
        if not words:
            trace.append(0.0)
            continue
            
        for i, w in enumerate(words):
            val = 0
            if w in pos_words: val = 1
            elif w in neg_words: val = -1
            
            if val != 0:
                # Check previous word for modifiers
                if i > 0:
                    prev = words[i-1]
                    if prev in negators:
                        val *= -0.5 # Flip and dampen ("not happy" != "sad")
                    elif prev in intensifiers:
                        val *= 1.5
                        
                score += val
                
        # Normalize to -1.0 to 1.0
        # VADER uses x / sqrt(x^2 + alpha)
        alpha = 15
        norm_score = score / math.sqrt(score*score + alpha)
        
        trace.append(round(norm_score, 3))
        
    return trace
