"""
UI Components for Ghost of Space game
"""
import pygame
from typing import Callable, Optional, Tuple
from utils.logger import logger
import config
from resource_manager import resource_manager


class Button:
    """Improved button class with better functionality and visual feedback"""
    
    def __init__(self, width: int, height: int, text: str, callback: Optional[Callable] = None):
        """
        Initialize button
        
        Args:
            width: Button width
            height: Button height
            text: Button text
            callback: Function to call when clicked
        """
        self.width = width
        self.height = height
        self.text = text
        self.callback = callback
        self.font = resource_manager.get_font("Kenney Mini Square", 30)
        
        # Visual states
        self.is_hovered = False
        self.is_pressed = False
        self.last_click_time = 0
        
        # Colors
        self.normal_color = config.UI_GREEN
        self.hover_color = tuple(min(255, c + 30) for c in config.UI_GREEN)
        self.pressed_color = tuple(max(0, c - 30) for c in config.UI_GREEN)
        self.text_color = config.WHITE
        
        logger.debug(f"Button created: '{text}' ({width}x{height})")
    
    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int], 
                    button_rect: pygame.Rect) -> bool:
        """
        Handle input events for the button
        
        Args:
            event: Pygame event
            mouse_pos: Current mouse position
            button_rect: Button rectangle for collision detection
            
        Returns:
            True if button was clicked, False otherwise
        """
        # Check if mouse is over button
        self.is_hovered = button_rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True
                # Play click sound
                sound = resource_manager.get_sound("sfx_keypress")
                sound.play()
                return False
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.is_hovered:
                self.is_pressed = False
                current_time = pygame.time.get_ticks()
                
                # Prevent double-clicks
                if current_time - self.last_click_time > 300:
                    self.last_click_time = current_time
                    if self.callback:
                        self.callback()
                    return True
            self.is_pressed = False
        
        return False
    
    def draw(self, screen: pygame.Surface, x: int, y: int) -> pygame.Rect:
        """
        Draw the button
        
        Args:
            screen: Surface to draw on
            x: X position
            y: Y position
            
        Returns:
            Button rectangle
        """
        button_rect = pygame.Rect(x, y, self.width, self.height)
        
        # Choose color based on state
        if self.is_pressed:
            color = self.pressed_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.normal_color
        
        # Draw button background
        if self.is_hovered or self.is_pressed:
            pygame.draw.rect(screen, color, button_rect, 0, 10)
        else:
            pygame.draw.rect(screen, color, button_rect, 5, 10)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        
        return button_rect


class HealthBar:
    """Health bar UI component"""
    
    def __init__(self, width: int, height: int = 17):
        """
        Initialize health bar
        
        Args:
            width: Bar width
            height: Bar height
        """
        self.width = width
        self.height = height
        
    def draw(self, screen: pygame.Surface, x: int, y: int, current_hp: int, 
             max_hp: int, color: Tuple[int, int, int] = None):
        """
        Draw the health bar
        
        Args:
            screen: Surface to draw on
            x: X position
            y: Y position
            current_hp: Current health value
            max_hp: Maximum health value
            color: Bar color (defaults to green)
        """
        if color is None:
            color = config.HP_GREEN
        
        # Calculate fill percentage
        fill_ratio = max(0, current_hp / max_hp) if max_hp > 0 else 0
        fill_width = self.width * fill_ratio
        
        # Draw background
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(screen, config.GRAY, bg_rect)
        
        # Draw fill
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, self.height)
            pygame.draw.rect(screen, color, fill_rect)
        
        # Draw border
        pygame.draw.rect(screen, config.WHITE, bg_rect, 2)


class ProgressBar:
    """Progress bar UI component for score/level progress"""
    
    def __init__(self, width: int, height: int = 22):
        """
        Initialize progress bar
        
        Args:
            width: Bar width
            height: Bar height
        """
        self.width = width
        self.height = height
    
    def draw(self, screen: pygame.Surface, x: int, y: int, current: float, 
             maximum: float, color: Tuple[int, int, int] = None):
        """
        Draw the progress bar
        
        Args:
            screen: Surface to draw on
            x: X position
            y: Y position
            current: Current progress value
            maximum: Maximum progress value
            color: Bar color (defaults to blue)
        """
        if color is None:
            color = config.SCORE_BLUE
        
        # Calculate fill percentage
        fill_ratio = min(1.0, max(0, current / maximum)) if maximum > 0 else 0
        fill_width = self.width * fill_ratio
        
        # Draw background
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(screen, config.GRAY, bg_rect)
        
        # Draw fill
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, self.height)
            pygame.draw.rect(screen, color, fill_rect)
        
        # Draw decorative borders
        pygame.draw.rect(screen, (146, 143, 99), bg_rect, 3)
        pygame.draw.rect(screen, (199, 186, 150), bg_rect, 2)


class TextRenderer:
    """Utility class for rendering text"""
    
    @staticmethod
    def draw_text(screen: pygame.Surface, text: str, size: int, x: int, y: int, 
                 color: Tuple[int, int, int] = None, center: bool = True):
        """
        Draw text on screen
        
        Args:
            screen: Surface to draw on
            text: Text to draw
            size: Font size
            x: X position
            y: Y position
            color: Text color (defaults to white)
            center: Whether to center the text at the position
        """
        if color is None:
            color = config.WHITE
        
        font = resource_manager.get_font("Kenney Mini Square", size)
        text_surface = font.render(str(text), True, color)
        
        if center:
            text_rect = text_surface.get_rect()
            text_rect.midtop = (x, y)
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, (x, y))
    
    @staticmethod
    def get_text_size(text: str, size: int) -> Tuple[int, int]:
        """
        Get the size of rendered text
        
        Args:
            text: Text to measure
            size: Font size
            
        Returns:
            (width, height) of the text
        """
        font = resource_manager.get_font("Kenney Mini Square", size)
        return font.size(str(text))


class FPSCounter:
    """FPS counter display"""
    
    def __init__(self):
        """Initialize FPS counter"""
        self.font = resource_manager.get_font("Kenney Mini Square", 30)
        
    def draw(self, screen: pygame.Surface, clock: pygame.time.Clock, x: int = 5, y: int = 60):
        """
        Draw FPS counter
        
        Args:
            screen: Surface to draw on
            clock: Pygame clock object
            x: X position
            y: Y position
        """
        fps = int(clock.get_fps())
        text_surface = self.font.render(str(fps), True, config.GREEN)
        screen.blit(text_surface, (x, y))


class Panel:
    """Generic panel for UI layouts"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 background_color: Tuple[int, int, int] = None, alpha: int = 255):
        """
        Initialize panel
        
        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            background_color: Background color (None for transparent)
            alpha: Alpha transparency (0-255)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.background_color = background_color
        self.alpha = alpha
        
        if background_color:
            self.surface = pygame.Surface((width, height))
            self.surface.fill(background_color)
            if alpha < 255:
                self.surface.set_alpha(alpha)
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the panel
        
        Args:
            screen: Surface to draw on
        """
        if hasattr(self, 'surface'):
            screen.blit(self.surface, self.rect)


class Menu:
    """Base menu class"""
    
    def __init__(self, title: str):
        """
        Initialize menu
        
        Args:
            title: Menu title
        """
        self.title = title
        self.buttons = []
        self.active = False
        
    def add_button(self, button: Button) -> int:
        """
        Add a button to the menu
        
        Args:
            button: Button to add
            
        Returns:
            Index of the added button
        """
        self.buttons.append(button)
        return len(self.buttons) - 1
    
    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        """
        Handle events for all buttons in the menu
        
        Args:
            event: Pygame event
            mouse_pos: Current mouse position
            
        Returns:
            True if any button was clicked
        """
        # Calculate button positions
        start_y = config.SCREEN_HEIGHT // 2 - 50
        button_spacing = 70
        
        for i, button in enumerate(self.buttons):
            button_x = config.SCREEN_WIDTH // 2 - button.width // 2
            button_y = start_y + (i * button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button.width, button.height)
            
            if button.handle_event(event, mouse_pos, button_rect):
                return True
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the menu
        
        Args:
            screen: Surface to draw on
        """
        # Draw title
        TextRenderer.draw_text(screen, self.title, 75, config.SCREEN_WIDTH // 2, 150)
        TextRenderer.draw_text(screen, ". .", 80, config.SCREEN_WIDTH // 2, 200)
        TextRenderer.draw_text(screen, "_", 80, config.SCREEN_WIDTH // 2, 220)
        
        # Draw buttons
        start_y = config.SCREEN_HEIGHT // 2 - 50
        button_spacing = 70
        
        for i, button in enumerate(self.buttons):
            button_x = config.SCREEN_WIDTH // 2 - button.width // 2
            button_y = start_y + (i * button_spacing)
            button.draw(screen, button_x, button_y)