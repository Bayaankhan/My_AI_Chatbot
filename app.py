import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engbot.ui.app import demo

if __name__ == "__main__":
    demo.launch()