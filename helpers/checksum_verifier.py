import os
import hashlib
from typing import Tuple, Dict, List, Any

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
    Class responsible for verifying file checksums against a provided manifest.
    """
    
    def __init__(self, data_dir: str = TUB_FILES_DIR):
        self.data_dir = data_dir

    def _calculate_sha256(self, file_path: str) -> str:
        """Calculates the SHA-256 checksum of a file."""
        if not os.path.exists(file_path):
            return ""
        
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating checksum for {file_path}: {e}")
            return ""

    def verify_files(self, manifest_items: List[Any]) -> Dict[str, bool]:
        """
        Verifies the checksums of files listed in the manifest items.

        Args:
            manifest_items: List of RodamManifestItem objects (or objects with FileName, FilePath, Hash256 attributes).

        Returns:
            Dict[str, bool]: A dictionary mapping FileName to validity status (True/False).
        """
        results = {}
        
        if not manifest_items:
            print("No manifest items provided for verification.")
            return results

        for item in manifest_items:
            # Construct full local path using data_dir, item's FilePath, and FileName
            # item.FilePath might be empty strings or relative paths like "semantic\model"
            full_path = os.path.join(self.data_dir, item.FilePath, item.FileName)
            
            # Calculate local checksum
            if not os.path.exists(full_path):
                # If optional and missing, maybe valid? But for sync purposes, we usually assume missing = needs download.
                # If the goal is "is the file correct on disk", missing means False.
                results[item.FileName] = False
                continue

            calculated_checksum = self._calculate_sha256(full_path)
            
            if calculated_checksum == item.Hash256:
                results[item.FileName] = True
            else:
                print(f"Checksum mismatch for {item.FileName}. Expected: {item.Hash256}, Got: {calculated_checksum}")
                results[item.FileName] = False
                
        return results

if __name__ == "__main__":
    # Test routine
    verifier = ChecksumVerifier()
    print(f"ChecksumVerifier instantiating for dir: {verifier.data_dir}")
    # Cannot verify without items passed in.

