#!/usr/bin/env python3
# Memory Puzzle Game
# A matching game with 16 cards (8 pairs)
# Features: 4x4 grid, card flipping animation, move counter, victory screen, save/load functionality

import pygame
import sys
import random
import time
import json
import os

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 30
CARD_SIZE = 100
CARD_SPACING = 10
GRID_SIZE = 4
ANIMATION_SPEED = 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
BACKGROUND_COLOR = (50, 50, 50)
CARD_BACK_COLOR = (72, 61, 139)  # Dark slate blue

# Card values (symbols to match)
CARD_VALUES = [
    '1', '2', '3', '4', '5', '6', '7', '8'
]

# Value to color mapping
VALUE_COLORS = {
    '1': RED,
    '2': GREEN,
    '3': BLUE,
    '4': YELLOW,
    '5': PURPLE,
    '6': CYAN,
    '7': ORANGE,
    '8': PINK
}

# Setup the display
DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Memory Puzzle Game')
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 36)

# Save file path
SAVE_FILE = 'memory_puzzle_save.json'

class Card:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)
        self.is_flipped = False
        self.is_matched = False
        self.flip_progress = 0  # 0 to CARD_SIZE for animation

    def draw(self):
        if self.is_flipped or self.is_matched:
            # Calculate width for animation
            width = max(1, abs(self.flip_progress - CARD_SIZE/2) * 2)
            card_rect = pygame.Rect(
                self.x + (CARD_SIZE - width) // 2,
                self.y,
                width,
                CARD_SIZE
            )
            
            # Draw the front face of the card (when flipped)
            pygame.draw.rect(DISPLAY_SURFACE, VALUE_COLORS[self.value], card_rect)
            pygame.draw.rect(DISPLAY_SURFACE, BLACK, card_rect, 2)
            
            # Only draw the text if the card is fully flipped
            if self.flip_progress >= CARD_SIZE / 2:
                # Draw the card value
                text = FONT.render(self.value, True, WHITE)
                text_rect = text.get_rect(center=(self.x + CARD_SIZE // 2, self.y + CARD_SIZE // 2))
                DISPLAY_SURFACE.blit(text, text_rect)
        else:
            # Calculate width for animation
            width = max(1, abs(self.flip_progress - CARD_SIZE/2) * 2)
            card_rect = pygame.Rect(
                self.x + (CARD_SIZE - width) // 2,
                self.y,
                width,
                CARD_SIZE
            )
            
            # Draw the back face of the card
            pygame.draw.rect(DISPLAY_SURFACE, CARD_BACK_COLOR, card_rect)
            pygame.draw.rect(DISPLAY_SURFACE, BLACK, card_rect, 2)

    def flip(self):
        self.is_flipped = not self.is_flipped

    def update_animation(self):
        if self.is_flipped or self.is_matched:
            # Animate towards fully flipped
            if self.flip_progress < CARD_SIZE:
                self.flip_progress += ANIMATION_SPEED
                if self.flip_progress > CARD_SIZE:
                    self.flip_progress = CARD_SIZE
        else:
            # Animate towards face down
            if self.flip_progress > 0:
                self.flip_progress -= ANIMATION_SPEED
                if self.flip_progress < 0:
                    self.flip_progress = 0

class Game:
    def __init__(self):
        self.cards = []
        self.first_selection = None
        self.second_selection = None
        self.moves = 0
        self.victory = False
        self.wait_time = 0
        self.initialize_cards()
    
    def initialize_cards(self):
        # Create a list of paired values
        values = CARD_VALUES * 2
        random.shuffle(values)
        
        # Calculate grid position
        start_x = (WINDOW_WIDTH - (GRID_SIZE * CARD_SIZE + (GRID_SIZE - 1) * CARD_SPACING)) // 2
        start_y = (WINDOW_HEIGHT - (GRID_SIZE * CARD_SIZE + (GRID_SIZE - 1) * CARD_SPACING)) // 2
        
        # Create cards
        self.cards = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = start_x + col * (CARD_SIZE + CARD_SPACING)
                y = start_y + row * (CARD_SIZE + CARD_SPACING)
                card_value = values.pop()
                self.cards.append(Card(x, y, card_value))
    
    def handle_click(self, pos):
        # If we're waiting for cards to flip back, ignore clicks
        if self.wait_time > 0 or self.victory:
            return
        
        # Find which card was clicked
        for card in self.cards:
            if card.rect.collidepoint(pos) and not card.is_flipped and not card.is_matched:
                if self.first_selection is None:
                    self.first_selection = card
                    card.flip()
                elif self.second_selection is None and card != self.first_selection:
                    self.second_selection = card
                    card.flip()
                    self.moves += 1
                    
                    # Check for match
                    if self.first_selection.value == self.second_selection.value:
                        self.first_selection.is_matched = True
                        self.second_selection.is_matched = True
                        self.check_victory()
                        self.reset_selection()
                    else:
                        # Set wait time before flipping back
                        self.wait_time = FPS  # Wait for 1 second
                break
    
    def update(self):
        # Update all card animations
        for card in self.cards:
            card.update_animation()
            
        # Handle waiting time for unmatched cards
        if self.wait_time > 0:
            self.wait_time -= 1
            if self.wait_time == 0:
                self.flip_back_cards()
    
    def flip_back_cards(self):
        if self.first_selection and self.second_selection:
            if not self.first_selection.is_matched:
                self.first_selection.flip()
            if not self.second_selection.is_matched:
                self.second_selection.flip()
            self.reset_selection()
    
    def reset_selection(self):
        self.first_selection = None
        self.second_selection = None
    
    def check_victory(self):
        for card in self.cards:
            if not card.is_matched:
                return
        self.victory = True
    
    def draw(self):
        # Draw background
        DISPLAY_SURFACE.fill(BACKGROUND_COLOR)
        
        # Draw all cards
        for card in self.cards:
            card.draw()
        
        # Draw moves counter
        moves_text = FONT.render(f"Moves: {self.moves}", True, WHITE)
        DISPLAY_SURFACE.blit(moves_text, (20, 20))
        
        # Draw victory message if all pairs are matched
        if self.victory:
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            DISPLAY_SURFACE.blit(overlay, (0, 0))
            
            # Victory message
            victory_text = FONT.render("Victory!", True, WHITE)
            moves_result = FONT.render(f"Total Moves: {self.moves}", True, WHITE)
            restart_text = FONT.render("Press R to restart", True, WHITE)
            
            DISPLAY_SURFACE.blit(victory_text, (WINDOW_WIDTH // 2 - victory_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
            DISPLAY_SURFACE.blit(moves_result, (WINDOW_WIDTH // 2 - moves_result.get_width() // 2, WINDOW_HEIGHT // 2))
            DISPLAY_SURFACE.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
    
    def save_game(self):
        """Save the current game state to a JSON file"""
        save_data = {
            'moves': self.moves,
            'victory': self.victory,
            'cards': []
        }
        
        for card in self.cards:
            card_data = {
                'x': card.x,
                'y': card.y,
                'value': card.value,
                'is_flipped': card.is_flipped,
                'is_matched': card.is_matched
            }
            save_data['cards'].append(card_data)
        
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f)
        
        print("Game saved!")
    
    def load_game(self):
        """Load the game state from a JSON file"""
        if not os.path.exists(SAVE_FILE):
            print("No save file found.")
            return False
        
        try:
            with open(SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            
            self.moves = save_data['moves']
            self.victory = save_data['victory']
            self.cards = []
            
            for card_data in save_data['cards']:
                card = Card(card_data['x'], card_data['y'], card_data['value'])
                card.is_flipped = card_data['is_flipped']
                card.is_matched = card_data['is_matched']
                if card.is_flipped or card.is_matched:
                    card.flip_progress = CARD_SIZE  # Set to fully flipped
                self.cards.append(card)
            
            self.first_selection = None
            self.second_selection = None
            self.wait_time = 0
            
            print("Game loaded!")
            return True
        except Exception as e:
            print(f"Error loading save file: {e}")
            return False

def main():
    game = Game()
    
    # Try to load a saved game at startup
    game.load_game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save the game before quitting
                if not game.victory:
                    game.save_game()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Restart the game
                    game = Game()
                elif event.key == pygame.K_s:
                    # Save the game
                    game.save_game()
                elif event.key == pygame.K_l:
                    # Load the game
                    game.load_game()
        
        game.update()
        game.draw()
        
        pygame.display.update()
        CLOCK.tick(FPS)

if __name__ == '__main__':
    main()