"""
YouTube Uploader
Handles authentication and video uploads to YouTube
"""

import os
import logging
from pathlib import Path
from typing import Dict, List
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubeUploader:
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, config: Dict):
        """Initialize YouTube uploader"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.youtube = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        credentials = None
        token_path = Path('./youtube_token.pickle')
        
        # Load existing credentials
        if token_path.exists():
            with open(token_path, 'rb') as token:
                credentials = pickle.load(token)
        
        # If credentials are invalid or don't exist, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                self.logger.info("Refreshing YouTube credentials...")
                credentials.refresh(Request())
            else:
                self.logger.info("Getting new YouTube credentials...")
                client_secrets = self.config['api_keys']['youtube_client_secrets']
                
                if not Path(client_secrets).exists():
                    self.logger.error(f"Client secrets file not found: {client_secrets}")
                    self.logger.error("Download it from Google Cloud Console")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets, 
                    self.SCOPES
                )
                credentials = flow.run_local_server(port=8080)
            
            # Save credentials for next time
            with open(token_path, 'wb') as token:
                pickle.dump(credentials, token)
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=credentials)
        self.logger.info("✅ YouTube API authenticated")
    
    def upload(self, video_path: str, title: str, description: str, tags: List[str]) -> bool:
        """Upload video to YouTube"""
        if not self.youtube:
            self.logger.error("YouTube API not authenticated")
            return False
        
        try:
            self.logger.info(f"📤 Uploading: {title}")
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': self.config['youtube']['category_id']
                },
                'status': {
                    'privacyStatus': self.config['youtube']['privacy_status'],
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=1024*1024,  # 1MB chunks
                resumable=True
            )
            
            # Execute upload
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.logger.info(f"Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            self.logger.info(f"✅ Video uploaded successfully!")
            self.logger.info(f"🔗 URL: {video_url}")
            
            # Optionally add to playlist
            self._add_to_playlist(video_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Upload failed: {str(e)}", exc_info=True)
            return False
    
    def _add_to_playlist(self, video_id: str):
        """Add video to a playlist (optional)"""
        try:
            playlist_id = self.config['youtube'].get('playlist_id')
            if not playlist_id:
                return
            
            self.youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()
            
            self.logger.info(f"✅ Added to playlist: {playlist_id}")
            
        except Exception as e:
            self.logger.warning(f"Failed to add to playlist: {str(e)}")
    
    def get_channel_info(self):
        """Get information about the authenticated channel"""
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics',
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'title': channel['snippet']['title'],
                    'subscribers': channel['statistics']['subscriberCount'],
                    'views': channel['statistics']['viewCount'],
                    'videos': channel['statistics']['videoCount']
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get channel info: {str(e)}")
            return None
    
    def delete_old_videos(self, keep_last_n: int = 100):
        """Delete old videos to manage channel content"""
        try:
            # Get all videos
            request = self.youtube.search().list(
                part='id',
                forMine=True,
                type='video',
                maxResults=50
            )
            response = request.execute()
            
            videos = response.get('items', [])
            
            if len(videos) > keep_last_n:
                videos_to_delete = videos[keep_last_n:]
                
                for video in videos_to_delete:
                    video_id = video['id']['videoId']
                    self.youtube.videos().delete(id=video_id).execute()
                    self.logger.info(f"🗑️ Deleted old video: {video_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to delete old videos: {str(e)}")
    
    def get_video_analytics(self, video_id: str):
        """Get analytics for a specific video"""
        try:
            request = self.youtube.videos().list(
                part='statistics',
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                stats = response['items'][0]['statistics']
                return {
                    'views': stats.get('viewCount', 0),
                    'likes': stats.get('likeCount', 0),
                    'comments': stats.get('commentCount', 0)
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics: {str(e)}")
            return None