"""Run with the target platform's Python: python build.py."""
import sys
from pathlib import Path


if __name__ == '__main__':
    if sys.platform not in ('win32', 'darwin'):
        raise SystemExit('Build on Windows for .exe or macOS for .app.')
    try:
        import PyInstaller.__main__
    except ImportError:
        raise SystemExit('Install build dependencies: python -m pip install -r requirements-build.txt')

    root = Path(__file__).resolve().parent
    options = [
        str(root / 'Game.py'), '--name=GhostOfSpace', '--windowed', '--noconfirm', '--clean',
        '--distpath=' + str(root / 'dist'), '--workpath=' + str(root / 'build' / 'work'),
        '--specpath=' + str(root / 'build'),
        '--add-data=' + str(root / 'Png') + ':Png',
        '--add-data=' + str(root / 'Sound') + ':Sound',
    ]
    if sys.platform == 'win32':
        options.append('--onefile')
    else:
        options += ['--onedir', '--osx-bundle-identifier=com.ghostofspace.game']
    PyInstaller.__main__.run(options)
