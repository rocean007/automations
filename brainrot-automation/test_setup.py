#!/usr/bin/env python3
"""
Test script to verify the automation system works
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        'yaml',
        'schedule',
        'PIL',
        'moviepy',
        'google.generativeai',
        'gtts',
        'googleapiclient',
    ]
    
    failed = []
    for module in required_modules:
        try:
            __import__(module.split('.')[0])
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Missing modules: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All modules imported successfully\n")
    return True

def test_config():
    """Test if config file is valid"""
    print("🧪 Testing config.yaml...")
    
    if not Path('config.yaml').exists():
        print("❌ config.yaml not found")
        return False
    
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required keys
        required_keys = ['api_keys', 'content', 'video', 'youtube']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing key in config: {key}")
                return False
            print(f"  ✅ {key}")
        
        # Check API keys
        if 'YOUR_' in config['api_keys'].get('gemini_api_key', ''):
            print("⚠️  Gemini API key not set in config.yaml")
        
        print("✅ Config file is valid\n")
        return True
        
    except Exception as e:
        print(f"❌ Error reading config: {str(e)}")
        return False

def test_directories():
    """Test if required directories exist"""
    print("🧪 Testing directories...")
    
    required_dirs = [
        'character_dataset',
        'music',
        'logs',
        'generated_content',
        'output_videos'
    ]
    
    for dir_name in required_dirs:
        path = Path(dir_name)
        if not path.exists():
            path.mkdir(exist_ok=True)
            print(f"  ✅ Created {dir_name}/")
        else:
            print(f"  ✅ {dir_name}/ exists")
    
    print("✅ All directories ready\n")
    return True

def test_character_database():
    """Test character database"""
    print("🧪 Testing character database...")
    
    dataset_path = Path('character_dataset')
    character_folders = [f for f in dataset_path.iterdir() if f.is_dir()]
    
    if not character_folders:
        print("⚠️  No characters found in character_dataset/")
        print("  Add character folders with images to get started")
        return False
    
    print(f"  Found {len(character_folders)} characters:")
    for char_folder in character_folders:
        images = list(char_folder.glob('*.jpg')) + list(char_folder.glob('*.png'))
        print(f"  ✅ {char_folder.name}: {len(images)} images")
    
    print("✅ Character database ready\n")
    return True

def test_youtube_auth():
    """Test YouTube authentication"""
    print("🧪 Testing YouTube authentication...")
    
    if not Path('client_secrets.json').exists():
        print("⚠️  client_secrets.json not found")
        print("  Download from Google Cloud Console")
        return False
    
    print("  ✅ client_secrets.json found")
    
    if Path('youtube_token.pickle').exists():
        print("  ✅ youtube_token.pickle found (already authenticated)")
    else:
        print("  ⚠️  youtube_token.pickle not found")
        print("  Run main.py to authenticate")
    
    print("✅ YouTube setup ready\n")
    return True

def test_music():
    """Test background music"""
    print("🧪 Testing background music...")
    
    music_path = Path('music')
    music_files = list(music_path.glob('*.mp3')) + list(music_path.glob('*.wav'))
    
    if not music_files:
        print("⚠️  No music files found in music/")
        print("  Add .mp3 or .wav files for background music")
        return False
    
    print(f"  ✅ Found {len(music_files)} music files")
    print("✅ Background music ready\n")
    return True

def test_gemini_api():
    """Test Gemini API connection"""
    print("🧪 Testing Gemini API...")
    
    try:
        import yaml
        import google.generativeai as genai
        
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        api_key = config['api_keys']['gemini_api_key']
        
        if 'YOUR_' in api_key:
            print("⚠️  Gemini API key not configured")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content("Say 'test successful' and nothing else")
        
        if 'test successful' in response.text.lower():
            print("  ✅ Gemini API connected successfully")
            print("✅ API test passed\n")
            return True
        else:
            print("  ⚠️  Unexpected response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🔥 BRAINROT AUTOMATION TEST SUITE 🔥")
    print("=" * 50)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Config", test_config),
        ("Directories", test_directories),
        ("Character Database", test_character_database),
        ("YouTube Auth", test_youtube_auth),
        ("Background Music", test_music),
        ("Gemini API", test_gemini_api),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {str(e)}\n")
            results.append((name, False))
    
    # Summary
    print("=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nScore: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready to run!")
        print("\nNext steps:")
        print("1. python main.py  # Start the automation")
        print("2. docker-compose up -d  # Or run in Docker")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix issues above before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())