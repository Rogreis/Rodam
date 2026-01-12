import os
import json
import hashlib
from typing import Tuple, Dict

import sys
# Fix path to run directly if executed as main script
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)

# Assuming helpers.globals is available in sys.path
from helpers.globals import TUB_FILES_DIR

class ChecksumVerifier:
    """
    Class responsible for verifying file checksums against a JSON manifest.
    """
    
    def __init__(self, data_dir: str = TUB_FILES_DIR):
        self.data_dir = data_dir
        self.manifest_file = os.path.join(self.data_dir, "rodam_available.json")

    def _calculate_sha256(self, file_path: str) -> str:
        """Calculates the SHA-256 checksum of a file."""
        if not os.path.exists(file_path):
            return None
        
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating checksum for {file_path}: {e}")
            return None

    def verify_files(self) -> Tuple[bool, bool, bool]:
        """
        Reads the manifest file and verifies the checksums of the 3 specific files:
        1. FormatTable.gz
        2. TR000.zip
        3. TR002.zip

        Returns:
            Tuple[bool, bool, bool]: A tuple indicating (valid_format_table, valid_tr000, valid_tr002)
        """
        # Default results (False implies missing or invalid)
        results = {
            "FormatTable.gz": False,
            "TR000.zip": False,
            "TR002.zip": False
        }
        
        if not os.path.exists(self.manifest_file):
            print(f"Manifest file not found: {self.manifest_file}")
            return (False, False, False)
            
        try:
            with open(self.manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception as e:
            print(f"Error reading manifest file: {e}")
            return (False, False, False)

        # Check each file
        target_files = ["FormatTable.gz", "TR000.zip", "TR002.zip"]
        
        for filename in target_files:
            expected_checksum = manifest_data.get(filename)
            
            if not expected_checksum:
                print(f"Checksum for {filename} not found in manifest.")
                results[filename] = False
                continue
                
            file_path = os.path.join(self.data_dir, filename)
            calculated_checksum = self._calculate_sha256(file_path)
            
            if calculated_checksum == expected_checksum:
                results[filename] = True
            else:
                print(f"Checksum mismatch for {filename}. Expected: {expected_checksum}, Got: {calculated_checksum}")
                results[filename] = False
                
        return (results["FormatTable.gz"], results["TR000.zip"], results["TR002.zip"])

if __name__ == "__main__":
    # Test routine
    verifier = ChecksumVerifier()
    print(f"Verifying files in: {verifier.data_dir}")
    
    # Create dummy files for testing if they don't exist (Optional, but good for self-contained test)
    # Note: In a real scenario, these files should exist.
    
    r1, r2, r3 = verifier.verify_files()
    print(f"FormatTable.gz valid: {r1}")
    print(f"TR000.zip valid: {r2}")
    print(f"TR002.zip valid: {r3}")
