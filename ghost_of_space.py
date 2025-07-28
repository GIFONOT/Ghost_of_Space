"""
Ghost of Space - Improved Version
A space shooter game built with Pygame
"""
import pygame
import sys
from pathlib import Path
from utils.logger import logger
import config
from resource_manager import resource_manager
from game_state import StateManager


class GhostOfSpace:
    """Main game class for Ghost of Space"""
    
    def __init__(self):
        """Initialize the game"""
        logger.info("Initializing Ghost of Space...")
        
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Create display
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Ghost of Space - Enhanced Edition")
        
        # Set up icon if available
        try:
            icon = resource_manager.get_image("somm")
            pygame.display.set_icon(icon)
        except:
            logger.warning("Could not set game icon")
        
        # Initialize clock
        self.clock = pygame.time.Clock()
        
        # Preload assets
        resource_manager.preload_assets()
        
        # Initialize state manager
        self.state_manager = StateManager(self.screen, self.clock)
        
        logger.info("Game initialization complete")
    
    def run(self):
        """Main game loop"""
        logger.info("Starting game loop")
        
        try:
            while self.state_manager.running:
                dt = self.clock.tick(config.FPS) / 1000.0  # Delta time in seconds
                
                # Handle events
                for event in pygame.event.get():
                    self.state_manager.handle_event(event)
                
                # Update game state
                self.state_manager.update(dt)
                
                # Draw everything
                self.state_manager.draw()
                
                # Update display
                pygame.display.flip()
                
        except KeyboardInterrupt:
            logger.info("Game interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in game loop: {e}")
            raise
        finally:
            self.quit()
    
    def quit(self):
        """Clean up and quit the game"""
        logger.info("Shutting down game")
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()


def main():
    """Main entry point"""
    try:
        # Change to game directory
        game_dir = Path(__file__).parent
        if game_dir != Path.cwd():
            import os
            os.chdir(game_dir)
            logger.info(f"Changed working directory to: {game_dir}")
        
        # Create and run the game
        game = GhostOfSpace()
        game.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()