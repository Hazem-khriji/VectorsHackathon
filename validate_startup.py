import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from create_indexes import create_product_index
    from create_behavior_indexes import create_behavioral_index
    print("Imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)
