"""
3D Car Racing Game - Main Entry Point
Run this file to start the game.
"""

import pygame
import sys
from game import Game

def main():
    pygame.init()
    pygame.mixer.init()
    
    # Screen setup
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 700
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("🏎️  TURBO RACE 3D")
    
    clock = pygame.time.Clock()
    game = Game(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
