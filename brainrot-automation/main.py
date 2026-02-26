#!/usr/bin/env python3
"""
Brainrot Content Automation System
Main orchestrator that runs continuously and generates content on schedule
"""

import os
import yaml
import schedule
import time
from datetime import datetime
import logging
from pathlib import Path
import random

# Import our custom modules
from content_generator import ContentGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from character_loader import CharacterDatabase

class BrainrotAutomation:
    def __init__(self, config_path="config.yaml"):
        """Initialize the automation system"""
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.logger.info("🚀 Brainrot Automation System Starting...")
        
        # Initialize components
        self.character_db = CharacterDatabase(self.config['characters']['dataset_folder'])
        self.content_generator = ContentGenerator(self.config, self.character_db)
        self.video_creator = VideoCreator(self.config)
        self.youtube_uploader = YouTubeUploader(self.config)
        
        # Track today's posts
        self.posts_today = 0
        self.last_date = datetime.now().date()
        
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_folder = Path(self.config['logging']['log_folder'])
        log_folder.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=self.config['logging']['level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_folder / f"automation_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def reset_daily_counter(self):
        """Reset post counter at midnight"""
        current_date = datetime.now().date()
        if current_date != self.last_date:
            self.posts_today = 0
            self.last_date = current_date
            self.logger.info(f"📅 New day! Reset counter. Date: {current_date}")
    
    def select_content_type(self):
        """Select content type based on configured distribution"""
        content_types = self.config['content']['content_types']
        choices = []
        weights = []
        
        for content_type, weight in content_types.items():
            choices.append(content_type)
            weights.append(weight)
        
        return random.choices(choices, weights=weights)[0]
    
    def create_and_upload_video(self):
        """Main workflow: Generate content -> Create video -> Upload to YouTube"""
        try:
            self.reset_daily_counter()
            
            # Check if we've hit daily limit
            if self.posts_today >= self.config['content']['posts_per_day']:
                self.logger.info(f"✋ Daily limit reached ({self.posts_today} posts)")
                return
            
            self.logger.info(f"🎬 Starting video creation #{self.posts_today + 1}")
            
            # Step 1: Select content type
            content_type = self.select_content_type()
            self.logger.info(f"📝 Content type: {content_type}")
            
            # Step 2: Generate content (script, images, voice)
            content_data = self.content_generator.generate(content_type)
            
            if not content_data:
                self.logger.error("❌ Content generation failed")
                return
            
            # Step 3: Create video
            self.logger.info("🎥 Creating video...")
            video_path = self.video_creator.create_video(content_data)
            
            if not video_path:
                self.logger.error("❌ Video creation failed")
                return
            
            # Step 4: Upload to YouTube
            self.logger.info("📤 Uploading to YouTube...")
            upload_success = self.youtube_uploader.upload(
                video_path=video_path,
                title=content_data['title'],
                description=content_data['description'],
                tags=content_data['tags']
            )
            
            if upload_success:
                self.posts_today += 1
                self.logger.info(f"✅ Video uploaded successfully! ({self.posts_today}/{self.config['content']['posts_per_day']})")
                
                # Cleanup if configured
                if not self.config['deployment']['keep_videos_locally']:
                    os.remove(video_path)
                    self.logger.info("🗑️ Local video deleted to save space")
            else:
                self.logger.error("❌ YouTube upload failed")
                
        except Exception as e:
            self.logger.error(f"❌ Error in workflow: {str(e)}", exc_info=True)
    
    def schedule_jobs(self):
        """Schedule content creation at configured times"""
        upload_times = self.config['youtube']['upload_times']
        
        for upload_time in upload_times:
            schedule.every().day.at(upload_time).do(self.create_and_upload_video)
            self.logger.info(f"⏰ Scheduled upload at {upload_time}")
    
    def run(self):
        """Run the automation system continuously"""
        self.logger.info("🎯 Automation system ready!")
        self.logger.info(f"📊 Posts per day: {self.config['content']['posts_per_day']}")
        self.logger.info(f"⏰ Upload times: {self.config['youtube']['upload_times']}")
        
        # Schedule all jobs
        self.schedule_jobs()
        
        # Optional: Create one video immediately on startup for testing
        if os.getenv('CREATE_NOW', 'false').lower() == 'true':
            self.logger.info("🚀 Creating test video immediately...")
            self.create_and_upload_video()
        
        # Run forever
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Entry point"""
    automation = BrainrotAutomation()
    automation.run()

if __name__ == "__main__":
    main()