"""
Migrate existing JSON cache files to single Pickle file
Run this once to convert your existing cache
"""

import os
import json
import pickle
from datetime import datetime

CACHE_DIR = "cache"
OLD_CACHE_PATTERN = ".json"
NEW_CACHE_FILE = os.path.join(CACHE_DIR, "stocks_cache.pkl")


def migrate_json_to_pickle():
    """Convert all JSON cache files to single Pickle file"""
    
    if not os.path.exists(CACHE_DIR):
        print("No cache directory found. Nothing to migrate.")
        return
    
    # Initialize new cache structure
    new_cache = {
        'stocks': {},
        'last_updated': datetime.now()
    }
    
    # Count files
    json_files = [f for f in os.listdir(CACHE_DIR) if f.endswith(OLD_CACHE_PATTERN)]
    
    if not json_files:
        print("No JSON cache files found. Nothing to migrate.")
        return
    
    print(f"Found {len(json_files)} JSON cache files to migrate...")
    
    migrated = 0
    errors = 0
    
    for filename in json_files:
        try:
            filepath = os.path.join(CACHE_DIR, filename)
            
            # Load JSON file
            with open(filepath, 'r') as f:
                cache_data = json.load(f)
            
            # Extract ticker from filename
            ticker = cache_data.get('ticker', filename.replace('.json', '').replace('_', '.'))
            
            # Get timestamp from file modification time
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            # Add to new cache
            new_cache['stocks'][ticker] = {
                'data': cache_data.get('data', cache_data),
                'timestamp': mod_time
            }
            
            migrated += 1
            
            if migrated % 100 == 0:
                print(f"  Migrated {migrated}/{len(json_files)}...")
            
        except Exception as e:
            print(f"  Error migrating {filename}: {e}")
            errors += 1
    
    # Save new pickle file
    print(f"\nSaving to {NEW_CACHE_FILE}...")
    with open(NEW_CACHE_FILE, 'wb') as f:
        pickle.dump(new_cache, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"\n✅ Migration complete!")
    print(f"   Migrated: {migrated} stocks")
    print(f"   Errors: {errors}")
    print(f"   New cache file: {NEW_CACHE_FILE}")
    
    # Ask to delete old files
    response = input("\nDelete old JSON files? (y/n): ").strip().lower()
    if response == 'y':
        deleted = 0
        for filename in json_files:
            try:
                os.remove(os.path.join(CACHE_DIR, filename))
                deleted += 1
            except Exception as e:
                print(f"  Error deleting {filename}: {e}")
        print(f"✅ Deleted {deleted} old JSON files")
    else:
        print("Old JSON files kept. You can delete them manually later.")


if __name__ == "__main__":
    print("=" * 60)
    print("JSON to Pickle Cache Migration")
    print("=" * 60)
    migrate_json_to_pickle()
