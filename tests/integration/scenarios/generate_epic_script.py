import random
import uuid

def generate_epic_screenplay(filename="tests/scenarios/epic_200pg.txt", target_pages=200):
    """
    Generates a massive ~200 page screenplay with VARIED content to test ML sensitivity.
    """
    
    locations = [
        "INT. SPACESHIP COCKPIT - NIGHT", "EXT. ALIEN DESERT - DAY", "INT. COMMAND CENTER - DAY", 
        "EXT. SPACE BATTLE - SPACE", "INT. MESS HALL - NIGHT", "EXT. JUNGLE - DAY", 
        "INT. LABORATORY - NIGHT", "EXT. CITY RUINS - DAY"
    ]
    characters = ["COMMANDER", "ROOKIE", "ALIEN EMPEROR", "AI SYSTEM", "REBEL LEADER", "SCIENTIST", "MEDIC"]
    
    # Expanded pools to prevent repetition
    dialogue_pool = {
        "setup": [
            "We need a plan.", "The sensors are picking up something.", "It's quiet. Too quiet.", 
            "Check the stabilizers.", "Reading normal parameters.", "Did you hear that?",
            "Supplies are running low.", "I don't like this integration.", "System check complete."
        ],
        "conflict": [
            "They are attacking!", "Shields are down!", "We can't hold them back!", 
            "Fire everything you have!", "It's a trap!", "Hull breach in sector 4!",
            "They've boarded the main deck!", "We're losing power!", "Get to the escape pods!"
        ],
        "climax": [
            "This is the end.", "I will never surrender.", "For the alliance!", 
            "Launch the final weapon!", "It's now or never!", "Overload the core!",
            "Tell them we died fighting.", "Die, you monster!"
        ],
        "resolution": [
            "We did it.", "The war is over.", "Let's go home.", "I need a drink.",
            "Look at the sunrise.", "We lost good people today.", "Peace at last."
        ]
    }
    
    adjectives = ["dark", "cold", "silent", "violent", "sudden", "bright", "ominous", "broken", "burning"]
    nouns = ["shadow", "light", "metal", "blood", "hope", "fear", "engine", "sky", "weapon"]
    
    print(f"Generating {target_pages} pages of screenplay (High Variance)...")
    
    with open(filename, "w") as f:
        f.write("THE LAST FRONTIER (VARIED)\n\nby\n\nScriptPulse Generator\n\n")
        
        current_page = 1
        lines_per_page = 55
        total_lines = target_pages * lines_per_page
        lines_written = 0
        
        while lines_written < total_lines:
            progress = lines_written / total_lines
            if progress < 0.25: act = "setup"
            elif progress < 0.75: act = "conflict"
            else: 
                if progress > 0.9: act = "resolution"
                else: act = "climax"
            
            f.write(f"\n{random.choice(locations)}\n\n")
            lines_written += 3
            
            # Generate unique action line to force unique embeddings
            unique_action = f"A {random.choice(adjectives)} {random.choice(nouns)} fills the room. {str(uuid.uuid4())[:8]}"
            f.write(f"{unique_action}\n\n")
            lines_written += 2
            
            for _ in range(random.randint(3, 6)):
                char = random.choice(characters)
                base_line = random.choice(dialogue_pool[act])
                # Mutate dialogue slightly to ensure unique semantics
                f.write(f"\t\t{char}\n\t{base_line} ({random.randint(1, 100)})\n\n")
                lines_written += 3
                
    print(f"Done. Generated {filename} (~{lines_written} lines).")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=200, help="Number of pages to generate")
    parser.add_argument("--output", type=str, default="tests/scenarios/epic_200pg.txt", help="Output filename")
    args = parser.parse_args()
    
    generate_epic_screenplay(filename=args.output, target_pages=args.pages)
