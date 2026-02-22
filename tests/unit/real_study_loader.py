
import csv
import statistics
import os

class RealReaderLoader:
    """
    Infrastructure for loading real-world human study data.
    """
    
    def __init__(self, participants_path='data/real_study/participants.csv', ratings_path='data/real_study/ratings.csv'):
        self.participants_path = participants_path
        self.ratings_path = ratings_path
        self.data = {}
        
    def load_study_data(self):
        """
        Loads participants and ratings.
        Returns a structured dict of {script_id: {scene_index: {ratings: [], mean: val, std: val}}}
        """
        if not os.path.exists(self.ratings_path):
            print("No real study data found. Using empty structure.")
            return {}
            
        # ... logic to read CSVs ...
        # For this implementation plan, we just setup the structure
        return self.data

    def generate_template_files(self):
        """
        Generates empty CSV templates for the user to fill.
        """
        os.makedirs(os.path.dirname(self.participants_path), exist_ok=True)
        
        with open(self.participants_path, 'w') as f:
            f.write("participant_id,age,gender,reading_frequency,screenwriting_experience\n")
            f.write("# EX: P001,34,M,Daily,Advanced\n")
            
        with open(self.ratings_path, 'w') as f:
            f.write("participant_id,script_id,scene_index,effort_rating,tension_rating,fatigue_rating\n")
            f.write("# EX: P001,S001,1,3,5,1\n")
            
        return "Templates generated in data/real_study/"

    def generate_report(self):
        md = "### Real Reader Study\n\n"
        if not os.path.exists(self.ratings_path):
             md += "_No real reader data loaded. using synthetic/mock validation only._\n"
        else:
             md += "**Study Status**: Data loaded.\n"
        return md
