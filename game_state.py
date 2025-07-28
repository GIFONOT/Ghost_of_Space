"""
Game State Management for Ghost of Space
"""
import pygame
import sys
from enum import Enum
from typing import Dict, Any, Optional
from utils.logger import logger
import config
from ui.components import Menu, Button, TextRenderer, HealthBar, ProgressBar, FPSCounter
from resource_manager import resource_manager


class GameState(Enum):
    """Enumeration of possible game states"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_UP = "level_up"
    SETTINGS = "settings"
    SCORES = "scores"
    NAME_INPUT = "name_input"


class StateManager:
    """Manages different game states and transitions"""
    
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        """
        Initialize state manager
        
        Args:
            screen: Main game screen
            clock: Game clock
        """
        self.screen = screen
        self.clock = clock
        self.current_state = GameState.MENU
        self.states: Dict[GameState, 'BaseState'] = {}
        self.running = True
        
        # Initialize states
        self._initialize_states()
        
        logger.info("State manager initialized")
    
    def _initialize_states(self):
        """Initialize all game states"""
        self.states[GameState.MENU] = MenuState(self)
        self.states[GameState.PLAYING] = PlayingState(self)
        self.states[GameState.PAUSED] = PausedState(self)
        self.states[GameState.GAME_OVER] = GameOverState(self)
        self.states[GameState.LEVEL_UP] = LevelUpState(self)
        self.states[GameState.SETTINGS] = SettingsState(self)
        self.states[GameState.SCORES] = ScoresState(self)
        self.states[GameState.NAME_INPUT] = NameInputState(self)
    
    def change_state(self, new_state: GameState, **kwargs):
        """
        Change to a new game state
        
        Args:
            new_state: New state to transition to
            **kwargs: Additional data to pass to the new state
        """
        if new_state in self.states:
            # Exit current state
            if self.current_state in self.states:
                self.states[self.current_state].exit()
            
            # Enter new state
            self.current_state = new_state
            self.states[new_state].enter(**kwargs)
            
            logger.info(f"Changed state to {new_state.value}")
        else:
            logger.error(f"Unknown state: {new_state}")
    
    def handle_event(self, event: pygame.event.Event):
        """
        Handle events for the current state
        
        Args:
            event: Pygame event
        """
        if self.current_state in self.states:
            self.states[self.current_state].handle_event(event)
    
    def update(self, dt: float):
        """
        Update the current state
        
        Args:
            dt: Delta time in seconds
        """
        if self.current_state in self.states:
            self.states[self.current_state].update(dt)
    
    def draw(self):
        """Draw the current state"""
        if self.current_state in self.states:
            self.states[self.current_state].draw()
    
    def quit(self):
        """Quit the game"""
        self.running = False
        logger.info("Game quit requested")


class BaseState:
    """Base class for all game states"""
    
    def __init__(self, state_manager: StateManager):
        """
        Initialize base state
        
        Args:
            state_manager: Reference to the state manager
        """
        self.state_manager = state_manager
        self.screen = state_manager.screen
        self.clock = state_manager.clock
    
    def enter(self, **kwargs):
        """Called when entering this state"""
        pass
    
    def exit(self):
        """Called when exiting this state"""
        pass
    
    def handle_event(self, event: pygame.event.Event):
        """Handle events for this state"""
        if event.type == pygame.QUIT:
            self.state_manager.quit()
    
    def update(self, dt: float):
        """Update this state"""
        pass
    
    def draw(self):
        """Draw this state"""
        pass


class MenuState(BaseState):
    """Main menu state"""
    
    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.menu = Menu("Ghost of Space")
        
        # Create menu buttons
        self.menu.add_button(Button(200, 50, "PLAY", self._start_game))
        self.menu.add_button(Button(200, 50, "Scores", self._show_scores))
        self.menu.add_button(Button(200, 50, "Settings", self._show_settings))
        self.menu.add_button(Button(200, 50, "Exit", self._quit_game))
    
    def enter(self, **kwargs):
        """Enter menu state"""
        # Start menu music if available
        if resource_manager.music_loaded:
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(config.MUSIC_VOLUME)
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        mouse_pos = pygame.mouse.get_pos()
        self.menu.handle_event(event, mouse_pos)
    
    def draw(self):
        """Draw menu"""
        self.screen.fill(config.BLACK)
        self.menu.draw(self.screen)
    
    def _start_game(self):
        """Start a new game"""
        self.state_manager.change_state(GameState.NAME_INPUT)
    
    def _show_scores(self):
        """Show high scores"""
        self.state_manager.change_state(GameState.SCORES)
    
    def _show_settings(self):
        """Show settings menu"""
        self.state_manager.change_state(GameState.SETTINGS)
    
    def _quit_game(self):
        """Quit the game"""
        self.state_manager.quit()


class NameInputState(BaseState):
    """Player name input state"""
    
    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.player_name = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_name_length = 12
        
        # Back button
        self.back_button = Button(200, 50, "Back", self._go_back)
    
    def enter(self, **kwargs):
        """Enter name input state"""
        self.player_name = ""
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.player_name.strip()) >= 2:
                    self.state_manager.change_state(GameState.PLAYING, player_name=self.player_name.strip())
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_ESCAPE:
                self._go_back()
            else:
                # Add character to name
                if len(self.player_name) < self.max_name_length and event.unicode.isprintable():
                    self.player_name += event.unicode
        
        # Handle back button
        mouse_pos = pygame.mouse.get_pos()
        button_x = config.SCREEN_WIDTH // 2 - self.back_button.width // 2
        button_y = config.SCREEN_HEIGHT // 2 + 300
        button_rect = pygame.Rect(button_x, button_y, self.back_button.width, self.back_button.height)
        self.back_button.handle_event(event, mouse_pos, button_rect)
    
    def update(self, dt: float):
        """Update name input state"""
        # Animate cursor
        self.cursor_timer += dt * 1000
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self):
        """Draw name input screen"""
        self.screen.fill(config.BLACK)
        
        # Draw title
        TextRenderer.draw_text(self.screen, "Enter Your Name", 75, config.SCREEN_WIDTH // 2, 150)
        TextRenderer.draw_text(self.screen, ". .", 80, config.SCREEN_WIDTH // 2, 200)
        TextRenderer.draw_text(self.screen, "_", 80, config.SCREEN_WIDTH // 2, 220)
        
        # Draw input box
        input_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 150, config.SCREEN_HEIGHT // 2, 300, 50)
        pygame.draw.rect(self.screen, config.WHITE, input_rect, 2)
        
        # Draw name with cursor
        display_text = self.player_name
        if self.cursor_visible:
            display_text += "|"
        
        TextRenderer.draw_text(self.screen, display_text, 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 10)
        
        # Draw instructions
        if len(self.player_name.strip()) >= 2:
            TextRenderer.draw_text(self.screen, "Press ENTER to start", 25, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 80, config.GREEN)
        else:
            TextRenderer.draw_text(self.screen, "Enter at least 2 characters", 25, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 80, config.GRAY)
        
        # Draw back button
        button_x = config.SCREEN_WIDTH // 2 - self.back_button.width // 2
        button_y = config.SCREEN_HEIGHT // 2 + 300
        self.back_button.draw(self.screen, button_x, button_y)
    
    def _go_back(self):
        """Go back to main menu"""
        self.state_manager.change_state(GameState.MENU)


class PlayingState(BaseState):
    """Main gameplay state"""
    
    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.player_name = ""
        self.game_data = {}
        
        # UI components
        self.health_bar = HealthBar(200)
        self.progress_bar = ProgressBar(config.SCREEN_WIDTH - 10)
        self.fps_counter = FPSCounter()
    
    def enter(self, **kwargs):
        """Enter playing state"""
        self.player_name = kwargs.get('player_name', 'Player')
        # Initialize game data here
        # This would contain player, enemies, score, etc.
        logger.info(f"Starting game for player: {self.player_name}")
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameState.PAUSED)
    
    def update(self, dt: float):
        """Update playing state"""
        # Update game logic here
        pass
    
    def draw(self):
        """Draw playing state"""
        self.screen.fill(config.UI_DARK)
        
        # Draw background
        background = resource_manager.get_image("BackGround")
        self.screen.blit(background, (0, 0))
        
        # Draw UI elements
        self.fps_counter.draw(self.screen, self.clock)
        
        # Draw game objects here
        # Draw HUD
        TextRenderer.draw_text(self.screen, f"Player: {self.player_name}", 20, 10, 10, center=False)


class PausedState(BaseState):
    """Paused game state"""
    
    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.overlay.fill(config.BLACK)
        self.overlay.set_alpha(128)
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state_manager.change_state(GameState.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameState.MENU)
    
    def draw(self):
        """Draw paused state"""
        # Draw the game state underneath
        if GameState.PLAYING in self.state_manager.states:
            self.state_manager.states[GameState.PLAYING].draw()
        
        # Draw overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Draw pause text
        TextRenderer.draw_text(self.screen, "PAUSED", 75, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 100)
        TextRenderer.draw_text(self.screen, "Press ENTER to continue", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        TextRenderer.draw_text(self.screen, "Press ESC for main menu", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 50)


class GameOverState(BaseState):
    """Game over state"""
    
    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.final_score = 0
        self.player_name = ""
        
        # Buttons
        self.restart_button = Button(200, 50, "Restart", self._restart_game)
        self.menu_button = Button(200, 50, "Main Menu", self._go_to_menu)
    
    def enter(self, **kwargs):
        """Enter game over state"""
        self.final_score = kwargs.get('score', 0)
        self.player_name = kwargs.get('player_name', 'Player')
        
        # Play death sound
        death_sound = resource_manager.get_sound("Dark souls - You Died_(EEMUSIC.ru)")
        death_sound.play()
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle restart button
        button_x = config.SCREEN_WIDTH // 2 - 100
        button_y = config.SCREEN_HEIGHT // 2 + 50
        restart_rect = pygame.Rect(button_x, button_y, 200, 50)
        self.restart_button.handle_event(event, mouse_pos, restart_rect)
        
        # Handle menu button
        button_y += 70
        menu_rect = pygame.Rect(button_x, button_y, 200, 50)
        self.menu_button.handle_event(event, mouse_pos, menu_rect)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._restart_game()
            elif event.key == pygame.K_ESCAPE:
                self._go_to_menu()
    
    def draw(self):
        """Draw game over screen"""
        self.screen.fill(config.BLACK)
        
        # Draw game over text
        TextRenderer.draw_text(self.screen, "GAME OVER", 75, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 150)
        TextRenderer.draw_text(self.screen, f"Final Score: {self.final_score}", 40, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 50)
        
        # Draw buttons
        button_x = config.SCREEN_WIDTH // 2 - 100
        button_y = config.SCREEN_HEIGHT // 2 + 50
        self.restart_button.draw(self.screen, button_x, button_y)
        
        button_y += 70
        self.menu_button.draw(self.screen, button_x, button_y)
    
    def _restart_game(self):
        """Restart the game"""
        self.state_manager.change_state(GameState.PLAYING, player_name=self.player_name)
    
    def _go_to_menu(self):
        """Go to main menu"""
        self.state_manager.change_state(GameState.MENU)


class LevelUpState(BaseState):
    """Level up selection state"""
    
    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.level = 1
    
    def enter(self, **kwargs):
        """Enter level up state"""
        self.level = kwargs.get('level', 1)
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        # Handle level up selections
        pass
    
    def draw(self):
        """Draw level up screen"""
        self.screen.fill(config.BLACK)
        TextRenderer.draw_text(self.screen, f"LEVEL {self.level}!", 75, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)


class SettingsState(BaseState):
    """Settings menu state"""
    
    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.menu = Menu("Settings")
        
        # Add settings buttons
        self.menu.add_button(Button(200, 50, "Audio", self._audio_settings))
        self.menu.add_button(Button(200, 50, "Graphics", self._graphics_settings))
        self.menu.add_button(Button(200, 50, "Back", self._go_back))
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        mouse_pos = pygame.mouse.get_pos()
        self.menu.handle_event(event, mouse_pos)
    
    def draw(self):
        """Draw settings menu"""
        self.screen.fill(config.BLACK)
        self.menu.draw(self.screen)
    
    def _audio_settings(self):
        """Show audio settings"""
        # Implement audio settings
        pass
    
    def _graphics_settings(self):
        """Show graphics settings"""
        # Implement graphics settings
        pass
    
    def _go_back(self):
        """Go back to main menu"""
        self.state_manager.change_state(GameState.MENU)


class ScoresState(BaseState):
    """High scores state"""
    
    def __init__(self, state_manager: StateManager):
        super().__init__(state_manager)
        self.back_button = Button(200, 50, "Back", self._go_back)
    
    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        
        mouse_pos = pygame.mouse.get_pos()
        button_x = config.SCREEN_WIDTH // 2 - 100
        button_y = config.SCREEN_HEIGHT // 2 + 300
        button_rect = pygame.Rect(button_x, button_y, 200, 50)
        self.back_button.handle_event(event, mouse_pos, button_rect)
    
    def draw(self):
        """Draw high scores"""
        self.screen.fill(config.BLACK)
        
        # Draw title
        TextRenderer.draw_text(self.screen, "High Scores", 75, config.SCREEN_WIDTH // 2, 150)
        TextRenderer.draw_text(self.screen, ". .", 80, config.SCREEN_WIDTH // 2, 200)
        TextRenderer.draw_text(self.screen, "_", 80, config.SCREEN_WIDTH // 2, 220)
        
        # Draw scores (placeholder)
        y_offset = 300
        for i in range(5):
            TextRenderer.draw_text(self.screen, f"{i+1}. Player {i+1}: {1000 - i*100}", 30, 
                                 config.SCREEN_WIDTH // 2, y_offset + i * 40)
        
        # Draw back button
        button_x = config.SCREEN_WIDTH // 2 - 100
        button_y = config.SCREEN_HEIGHT // 2 + 300
        self.back_button.draw(self.screen, button_x, button_y)
    
    def _go_back(self):
        """Go back to main menu"""
        self.state_manager.change_state(GameState.MENU)