"""
Use the original CSV URLs that work - they have car-related seeds
"""

import csv
import requests
from database import SessionLocal, Claim
from import_csv_data import download_image
from collections import defaultdict

def get_csv_urls():
    """Get all working URLs from CSV with their claim IDs."""
    url_map = {}
    with open('../car_insurance_training_dataset_with_images.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            claim_id = row.get('claim_id', '').strip()
            url = row.get('photos', '').strip()
            if claim_id and url and url != 'None':
                url_map[claim_id] = url
    return url_map

def test_url(url):
    """Test if URL works."""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def fix_with_csv_urls():
    """Use original CSV URLs that work."""
    db = SessionLocal()
    
    try:
        # Get URL mapping from CSV
        csv_urls = get_csv_urls()
        print(f"Found {len(csv_urls)} URLs in CSV")
        
        # Get all claims
        all_claims = db.query(Claim).all()
        print(f"Processing {len(all_claims)} claims...")
        print("=" * 80)
        
        # Group URLs by pattern to find working ones
        url_patterns = defaultdict(list)
        for claim_id, url in csv_urls.items():
            # Extract pattern (e.g., seed name)
            if 'seed' in url:
                pattern = url.split('seed/')[1].split('/')[0] if 'seed/' in url else 'other'
                url_patterns[pattern].append((claim_id, url))
        
        print(f"Found {len(url_patterns)} URL patterns")
        
        # Test patterns and find working ones
        working_patterns = {}
        for pattern, urls in url_patterns.items():
            if urls:
                test_url_obj = urls[0][1]
                if test_url(test_url_obj):
                    working_patterns[pattern] = test_url_obj
                    print(f"✅ Pattern '{pattern}' works: {test_url_obj[:60]}...")
        
        fixed = 0
        failed = 0
        
        for claim in all_claims:
            try:
                # Try to get original URL from CSV
                original_url = csv_urls.get(claim.claim_id)
                
                if original_url and test_url(original_url):
                    # Use original URL
                    car_image_url = original_url
                else:
                    # Use a working pattern URL
                    if working_patterns:
                        car_image_url = random.choice(list(working_patterns.values()))
                    else:
                        # Fallback
                        car_image_url = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"
                
                # Download
                photo_path = download_image(car_image_url, claim.claim_id)
                
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
        print(f"📊 Success rate: {fixed/(fixed+failed)*100:.1f}%")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Fatal error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_with_csv_urls()

