"""
Fix images with actual car crash/accident images from reliable sources
"""

import requests
from database import SessionLocal, Claim
from import_csv_data import download_image
import random
import time

# Working car crash/accident image URLs from reliable sources
# Using direct Unsplash image IDs that are known to work
CAR_CRASH_IMAGE_URLS = [
    # Unsplash car accident images - using known working photo IDs
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
    "https://images.unsplash.com/photo-1558618022-e6ac99f8ec67?w=800", 
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop",
    "https://images.unsplash.com/photo-1558618022-e6ac99f8ec67?w=800&h=600&fit=crop",
    # Pexels car crash images
    "https://images.pexels.com/photos/3802508/pexels-photo-3802508.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
    "https://images.pexels.com/photos/159376/pexels-photo-159376.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop",
    # More variations
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600",
    "https://images.unsplash.com/photo-1558618022-e6ac99f8ec67?w=800&h=600",
]

# Alternative: Use placeholder services that provide car images
# But we'll try to use actual working URLs first

def get_car_crash_image_url(claim_id=None):
    """Get a working car crash image URL."""
    # Try known working URLs first
    for url in CAR_CRASH_IMAGE_URLS:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return url
        except:
            continue
    
    # If all fail, use a placeholder service with car keywords
    # Using placeholder.com which allows keywords
    seed = hash(claim_id) % 1000 if claim_id else random.randint(1, 1000)
    return f"https://via.placeholder.com/800x600/333333/FFFFFF?text=Car+Accident+{seed}"

def test_url(url):
    """Test if URL is accessible."""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def fix_all_car_images():
    """Replace all images with actual car crash images."""
    db = SessionLocal()
    
    try:
        # Get all claims
        all_claims = db.query(Claim).all()
        print(f"Processing {len(all_claims)} claims...")
        print("=" * 80)
        
        # Test URLs first
        print("Testing image URLs...")
        working_urls = [url for url in CAR_CRASH_IMAGE_URLS if test_url(url)]
        if working_urls:
            print(f"✅ Found {len(working_urls)} working URLs")
        else:
            print("⚠️  No working URLs found, will use placeholders")
        
        fixed = 0
        failed = 0
        
        for i, claim in enumerate(all_claims, 1):
            try:
                # Get a car crash image URL
                if working_urls:
                    car_image_url = random.choice(working_urls)
                else:
                    car_image_url = get_car_crash_image_url(claim.claim_id)
                
                # Download the image with retry
                photo_path = None
                for attempt in range(3):
                    photo_path = download_image(car_image_url, claim.claim_id)
                    if photo_path:
                        break
                    time.sleep(0.5)  # Wait before retry
                
                if photo_path:
                    # Update database
                    claim.photos_url = car_image_url
                    claim.photos_local_path = photo_path
                    fixed += 1
                    
                    if fixed % 50 == 0:
                        print(f"✅ Downloaded {fixed} car crash images...")
                        db.commit()  # Commit periodically
                else:
                    failed += 1
                    if failed <= 5:  # Only show first few failures
                        print(f"❌ Failed to download for {claim.claim_id}")
                    
            except Exception as e:
                failed += 1
                if failed <= 5:
                    print(f"❌ Error for {claim.claim_id}: {str(e)[:50]}")
                continue
        
        db.commit()
        
        print("=" * 80)
        print(f"✅ Successfully downloaded: {fixed}")
        print(f"❌ Failed: {failed}")
        if fixed + failed > 0:
            print(f"📊 Success rate: {fixed/(fixed+failed)*100:.1f}%")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Fatal error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_car_images()
