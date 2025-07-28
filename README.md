# Ghost of Space - Enhanced Edition

A modernized and improved version of the space shooter game built with Python and Pygame.

## 🚀 Features

### Game Improvements
- **Enhanced Graphics**: Improved visual effects and particle systems
- **Better Performance**: Optimized resource management and efficient asset loading
- **Improved UI**: Modern, responsive user interface components
- **State Management**: Clean separation between different game states
- **Sound System**: Enhanced audio with proper volume controls
- **Error Handling**: Comprehensive error handling and logging

### Technical Improvements
- **Modern Python**: Type hints, dataclasses, and modern Python features
- **Clean Architecture**: Modular design with clear separation of concerns
- **Logging System**: Comprehensive logging for debugging and monitoring
- **Configuration Management**: Centralized game settings and constants
- **Score System**: SQLite-based high score system with statistics
- **Resource Management**: Efficient asset loading and caching

## 🎮 Controls

- **WASD / Arrow Keys**: Move player
- **Space**: Shoot
- **ESC**: Pause game / Back to menu
- **Enter**: Confirm selections

## 📋 Requirements

- Python 3.8+
- Pygame 2.5.0+
- SQLite3 (included with Python)
- Additional dependencies listed in `requirements.txt`

## 🛠 Installation

1. Clone or download the game files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python ghost_of_space.py
   ```

## 📁 Project Structure

```
ghost_of_space/
├── ghost_of_space.py          # Main game entry point
├── config.py                  # Game configuration and constants
├── resource_manager.py        # Asset loading and management
├── game_state.py             # Game state management
├── score_manager.py          # High score system
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── game_objects/             # Game entity classes
│   ├── __init__.py
│   ├── player.py            # Player and bullet classes
│   ├── enemy.py             # Enemy and enemy bullet classes
│   └── effects.py           # Visual effects and particles
├── ui/                      # User interface components
│   ├── __init__.py
│   └── components.py        # UI elements (buttons, bars, etc.)
├── utils/                   # Utility functions
│   ├── __init__.py
│   └── logger.py           # Logging system
├── data/                    # Game data (scores, saves)
├── logs/                    # Log files
├── Png/                     # Game images (legacy)
├── Sound/                   # Game audio files (legacy)
├── Shrift/                  # Game fonts (legacy)
└── [legacy files...]       # Original game files
```

## 🎯 Game Features

### Player Progression
- Multiple upgrade types: Health, Damage, Speed, Life Steal
- Multi-bullet shooting patterns
- Progressive difficulty scaling

### Enemy System
- Multiple enemy types with different behaviors
- Enemy shooting patterns
- Dynamic spawning system

### Visual Effects
- Particle explosion effects
- Hit indicators and visual feedback
- Smooth animations

### Audio System
- Background music
- Sound effects for actions
- Volume controls

### Score System
- SQLite database for persistent high scores
- Player statistics tracking
- Score export/import functionality

## 🔧 Configuration

Game settings can be modified in `config.py`:

- Screen resolution
- Frame rate
- Audio volumes
- Game balance parameters
- File paths

## 📊 Logging

The game includes comprehensive logging:
- Console output for immediate feedback
- Daily log files in the `logs/` directory
- Different log levels (INFO, DEBUG, WARNING, ERROR)

## 🏆 High Scores

The game features a modern high score system:
- SQLite database storage
- Player statistics
- Play time tracking
- Export/import functionality

## 🎨 Asset Management

Improved asset loading system:
- Automatic caching
- Error handling for missing files
- Backward compatibility with original assets
- Efficient memory usage

## 🐛 Debugging

For debugging and development:
1. Enable debug logging in `config.py`
2. Check log files in the `logs/` directory
3. Use the FPS counter (shown in-game)

## 🔄 Migration from Original

This enhanced version maintains compatibility with original assets while providing:
- Improved code structure
- Better performance
- Enhanced features
- Modern Python practices

The original files are preserved for backward compatibility.

## 📝 Development

To contribute or modify the game:

1. Follow the existing code structure
2. Add type hints to new functions
3. Update documentation
4. Test thoroughly
5. Use the logging system for debugging

## 📄 License

This is an educational project demonstrating game development with Python and Pygame.

## 🙏 Acknowledgments

- Original game concept and assets
- Pygame community
- Python development community

---

Enjoy playing Ghost of Space Enhanced Edition! 🎮✨