import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if not getattr(sys, 'frozen', False):
    DATA_DIR = ROOT
elif sys.platform == 'win32':
    DATA_DIR = Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData' / 'Local') / 'GhostOfSpace'
else:
    DATA_DIR = Path.home() / 'Library' / 'Application Support' / 'GhostOfSpace'

SETTINGS_PATH = DATA_DIR / 'Settings.json'
SCORES_PATH = DATA_DIR / 'Scored.json'
