"""
Fix images with actual car crash images - use only working URLs
"""

import requests
from database import SessionLocal, Claim
from import_csv_data import download_image
import random
import time

# Use ONLY the one URL that we know works
WORKING_CAR_IMAGE_URL = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"

# Also try Pexels which might work
PEXELS_CAR_URLS = [
    "https://images.pexels.com/photos/3802508/pexels-photo-3802508.jpeg?auto=compress&cs=tinysrgb&w=800",
]

def get_working_car_url():
    """Get a working car image URL - use the one we know works."""
    # Test if Pexels works
    for url in PEXELS_CAR_URLS:
        try:
            response = requests.head(url, timeout=3, allow_redirects=True)
            if response.status_code == 200:
                return url
        except:
            pass
    
    # Fallback to the one we know works
    return WORKING_CAR_IMAGE_URL

def fix_all_car_images():
    """Replace all images with working car crash images."""
    db = SessionLocal()
    
    try:
        # Get all claims
        all_claims = db.query(Claim).all()
        print(f"Processing {len(all_claims)} claims...")
        print("Using verified working car image URLs...")
        print("=" * 80)
        
        # Test URL first
        test_url = get_working_car_url()
        print(f"Using URL: {test_url[:60]}...")
        
        fixed = 0
        failed = 0
        
        for i, claim in enumerate(all_claims, 1):
            try:
                # Use working URL
                car_image_url = get_working_car_url()
                
                # Download with retry
                photo_path = None
                for attempt in range(3):
                    photo_path = download_image(car_image_url, claim.claim_id)
                    if photo_path:
                        break
                    time.sleep(0.2)
                
                if photo_path:
                    claim.photos_url = car_image_url
                    claim.photos_local_path = photo_path
                    fixed += 1
                    
                    if fixed % 50 == 0:
                        print(f"✅ Downloaded {fixed} images...")
                        db.commit()
                else:
                    failed += 1
                    
            except Exception as e:
                failed += 1
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

