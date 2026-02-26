"""
Character Database Loader
Loads brainrot characters and their images from the dataset folder
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import logging

class CharacterDatabase:
    def __init__(self, dataset_folder: str):
        """
        Initialize character database
        
        Expected folder structure:
        character_dataset/
        ├── skibidi_toilet/
        │   ├── info.json (optional: contains character details)
        │   ├── image1.jpg
        │   ├── image2.png
        ├── gman/
        │   ├── info.json
        │   ├── image1.jpg
        """
        self.dataset_folder = Path(dataset_folder)
        self.logger = logging.getLogger(__name__)
        self.characters = {}
        self.load_characters()
    
    def load_characters(self):
        """Load all characters from dataset folder"""
        if not self.dataset_folder.exists():
            self.dataset_folder.mkdir(parents=True)
            self.logger.warning(f"Created dataset folder: {self.dataset_folder}")
            return
        
        for character_folder in self.dataset_folder.iterdir():
            if not character_folder.is_dir():
                continue
            
            character_name = character_folder.name
            character_data = self.load_character(character_folder)
            
            if character_data:
                self.characters[character_name] = character_data
                self.logger.info(f"✅ Loaded character: {character_name} ({len(character_data['images'])} images)")
    
    def load_character(self, character_folder: Path) -> Dict:
        """Load a single character's data"""
        character_data = {
            'name': character_folder.name.replace('_', ' ').title(),
            'folder': character_folder,
            'images': [],
            'info': {}
        }
        
        # Load info.json if exists
        info_file = character_folder / 'info.json'
        if info_file.exists():
            with open(info_file, 'r') as f:
                character_data['info'] = json.load(f)
        
        # Load all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        for file in character_folder.iterdir():
            if file.suffix.lower() in image_extensions:
                character_data['images'].append(str(file))
        
        return character_data if character_data['images'] else None
    
    def get_all_characters(self) -> List[str]:
        """Get list of all character names"""
        return list(self.characters.keys())
    
    def get_character(self, name: str) -> Dict:
        """Get character data by name"""
        return self.characters.get(name)
    
    def get_random_characters(self, count: int = 5) -> List[Dict]:
        """Get random characters for content generation"""
        import random
        character_names = list(self.characters.keys())
        
        if len(character_names) < count:
            self.logger.warning(f"Only {len(character_names)} characters available, requested {count}")
            count = len(character_names)
        
        selected_names = random.sample(character_names, count)
        return [self.characters[name] for name in selected_names]
    
    def get_character_by_type(self, character_type: str) -> List[Dict]:
        """Get characters filtered by type (if specified in info.json)"""
        filtered = []
        for char_data in self.characters.values():
            if char_data['info'].get('type') == character_type:
                filtered.append(char_data)
        return filtered
    
    def add_character_info(self, character_name: str, info: Dict):
        """Add or update character info"""
        if character_name in self.characters:
            character_folder = self.characters[character_name]['folder']
            info_file = character_folder / 'info.json'
            
            with open(info_file, 'w') as f:
                json.dump(info, f, indent=2)
            
            self.characters[character_name]['info'] = info
            self.logger.info(f"Updated info for {character_name}")
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        total_images = sum(len(char['images']) for char in self.characters.values())
        
        return {
            'total_characters': len(self.characters),
            'total_images': total_images,
            'characters': list(self.characters.keys())
        }

# Example info.json structure:
"""
{
  "name": "Skibidi Toilet",
  "type": "villain",
  "description": "A toilet with a head that sings",
  "catchphrase": "Skibidi dop dop yes yes",
  "traits": ["chaotic", "viral", "meme"],
  "story": "The main antagonist of the Skibidi series..."
}
"""