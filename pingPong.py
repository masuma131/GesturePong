"""
Hand Gesture Pong Game

This program uses OpenCV and MediaPipe for hand gesture detection to control a Pong paddle in Pygame. 
The player's paddle movement is controlled by the y-coordinate of the index finger detected from the webcam. 
The opponent paddle is controlled by a simple AI, which tracks the ball's position. 

Key Features:
- Real-time hand gesture detection for paddle control
- Pygame handles rendering, scoring, and game mechanics
- Smooth gameplay with frame rate capped at 120 FPS

Modules:
- OpenCV: Captures webcam feed and processes hand landmarks.
- MediaPipe: Detects hand landmarks, focusing on index finger position.
- Pygame: Manages game display, ball physics, paddle collision, and score tracking.

Instructions:
- The game starts with the ball in the center.
- Move your hand up and down to control the player paddle on the right side.
- Score by bouncing the ball past the opponent paddle.
- The game displays the score in real-time, with an automatic reset after scoring.
- To exit the game, close the game window, not the webcam.
"""


import cv2 as cv
import random
import pygame
import sys
from _handDetector import HandDetector

# Initialize OpenCV
cap = cv.VideoCapture(0)
# Set width and height
cap.set(cv.CAP_PROP_FRAME_WIDTH, 300)  
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 750) 

# Initialize HandDetector
hand_detector = HandDetector()

# Global variables
max_speed = 15  # Paddle speed limit
player_speed = 5
ball_speed_x = 10 * random.choice((1, -1))  # Ball speed increase
ball_speed_y = 10 * random.choice((1, -1))  # Ball speed increase
screen_width = 1280
screen_height = 750
player_score = 0
opponent_score = 0
score_time = True

# Initialize pygame
pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.init()
clock = pygame.time.Clock()

# Screen setup
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Hand Gesture Pong')

# Colors
light_grey = (200, 200, 200)
bg_color = pygame.Color('grey12')

# Game Rectangles
ball = pygame.Rect(screen_width / 2 - 15, screen_height / 2 - 15, 30, 30)
player = pygame.Rect(screen_width - 20, screen_height / 2 - 70, 10, 140)
opponent = pygame.Rect(10, screen_height / 2 - 70, 10, 140)

# Font setup
basic_font = pygame.font.Font('freesansbold.ttf', 32)

# Get hand position - return y
def get_hand_position(frame):
    hand_detector.processHandImg(frame)
    hand_detector.showLandMarks(img=frame)

    landmarks = hand_detector.getLandmarksPosByIndex(frame, index=[8])  # Index 8 is the tip of the index finger
    if landmarks:
        _, hand_y = landmarks[0][1], landmarks[0][2]  # (id, x, y) = landmarks[0]
        return hand_y
    return None

# Ball animation
def ball_animation():
    global ball_speed_x, ball_speed_y, player_score, opponent_score, score_time

    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.top <= 0 or ball.bottom >= screen_height:
        ball_speed_y *= -1

    # Player Score
    if ball.left <= 0:
        score_time = pygame.time.get_ticks()
        player_score += 1

    # Opponent Score
    if ball.right >= screen_width:
        score_time = pygame.time.get_ticks()
        opponent_score += 1

    if ball.colliderect(player) and ball_speed_x > 0:
        if abs(ball.right - player.left) < 10:
            ball_speed_x *= -1
        elif abs(ball.bottom - player.top) < 10 and ball_speed_y > 0:
            ball_speed_y *= -1
        elif abs(ball.top - player.bottom) < 10 and ball_speed_y < 0:
            ball_speed_y *= -1

    if ball.colliderect(opponent) and ball_speed_x < 0:
        if abs(ball.left - opponent.right) < 10:
            ball_speed_x *= -1
        elif abs(ball.bottom - opponent.top) < 10 and ball_speed_y > 0:
            ball_speed_y *= -1
        elif abs(ball.top - opponent.bottom) < 10 and ball_speed_y < 0:
            ball_speed_y *= -1

# Player animation - window
def player_animation(frame):
    global player_speed  # Declare player_speed as global to modify it

    # Get the hand Y position using OpenCV
    hand_y = get_hand_position(frame)

    if hand_y is not None:
        # Normalize the hand_y position to the screen height
        normalized_hand_y = int(hand_y * screen_height / frame.shape[0])

        # Update player position
        if player.centery < normalized_hand_y:
            player_speed = min(max_speed, player_speed + 3)  # Move down faster
        elif player.centery > normalized_hand_y:
            player_speed = max(-max_speed, player_speed - 3)  # Move up faster
        else:
            player_speed = 0  # Stop if aligned with hand

        # Apply the speed to the player position
        player.y += player_speed

        # Boundary checks to keep the paddle within screen limits
        if player.top <= 0:
            player.top = 0
        if player.bottom >= screen_height:
            player.bottom = screen_height

# Player animation - mac/linux
# def player_animation(frame):
#     global player_speed  # Declare player_speed as global to modify it
    
#     # Normalize the hand_y position to the screen height - for window
#     # normalized_hand_y = int(hand_y * screen_height / frame.shape[0])

#     # Get the hand Y position using OpenCV
#     hand_y = get_hand_position(frame)

#     if hand_y is not None:
#         # Increase speed faster if the hand moves more quickly or further
#         if player.centery < hand_y:
#             # Move paddle down faster
#             player_speed = min(max_speed, player_speed + 3)  # Increase by speed increment
#         elif player.centery > hand_y:
#             # Move paddle up faster
#             player_speed = max(-max_speed, player_speed - 3)  # Decrease by speed increment
#         else:
#             player_speed = 0  # Stop if aligned with hand

#         # Apply the speed to the player position
#         player.y += player_speed

#         # Boundary checks to keep the paddle within screen limits
#         if player.top <= 0:
#             player.top = 0
#         if player.bottom >= screen_height:
#             player.bottom = screen_height

# Opponent AI
def opponent_ai():
    # Move the opponent paddle towards the ball's y position at a controlled speed
    if opponent.centery < ball.centery:
        opponent.y += 9  # Move down if the paddle's center is above the ball
    elif opponent.centery > ball.centery:
        opponent.y -= 9  # Move up if the paddle's center is below the ball

    # Boundary checks to keep the paddle within screen limits
    if opponent.top <= 0:
        opponent.top = 0
    if opponent.bottom >= screen_height:
        opponent.bottom = screen_height


# Ball start/reset after scoring
def ball_start():
    global ball_speed_x, ball_speed_y, score_time

    ball.center = (screen_width / 2, screen_height / 2)
    current_time = pygame.time.get_ticks()

    if current_time - score_time < 700:
        number_three = basic_font.render("3", False, light_grey)
        screen.blit(number_three, (screen_width / 2 - 10, screen_height / 2 + 20))
    if 700 < current_time - score_time < 1400:
        number_two = basic_font.render("2", False, light_grey)
        screen.blit(number_two, (screen_width / 2 - 10, screen_height / 2 + 20))
    if 1400 < current_time - score_time < 2100:
        number_one = basic_font.render("1", False, light_grey)
        screen.blit(number_one, (screen_width / 2 - 10, screen_height / 2 + 20))

    if current_time - score_time < 2100:
        ball_speed_y, ball_speed_x = 0, 0
    else:
        ball_speed_x = 10 * random.choice((1, -1))  # Increase multiplier
        ball_speed_y = 10 * random.choice((1, -1))  # Increase multiplier
        score_time = None

################ main ##############
while True:
    # Capture the frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame!")
        break
    
    # Flip the frame horizontally for mirror effect
    frame = cv.flip(frame, 1)
    
    # Process the hand detection and update paddle
    player_animation(frame)

    # Handle events (including quitting)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Game Logic (ball movement, opponent AI, etc.)
    ball_animation()
    opponent_ai()

    # Visuals and rendering (game screen drawing)
    screen.fill(bg_color)
    pygame.draw.rect(screen, light_grey, player)
    pygame.draw.rect(screen, light_grey, opponent)
    pygame.draw.ellipse(screen, light_grey, ball)
    pygame.draw.aaline(screen, light_grey, (screen_width / 2, 0), (screen_width / 2, screen_height))

    # Show score
    if score_time:
        ball_start()

    player_text = basic_font.render(f'{player_score}', False, light_grey)
    screen.blit(player_text, (660, 470))

    opponent_text = basic_font.render(f'{opponent_score}', False, light_grey)
    screen.blit(opponent_text, (600, 470))

    # Update the display
    pygame.display.flip()

    # Display the webcam frame with landmarks (OpenCV window)
    cv.imshow('Hand Detection', frame)

    # Check for the 'ESC' key to close the OpenCV window and quit the program
    if cv.waitKey(1) & 0xFF == 27:
        break

    # Cap the frame rate to 120 FPS for smoother gameplay
    clock.tick(120)

# Release the OpenCV window and resources when done
cv.destroyAllWindows()
