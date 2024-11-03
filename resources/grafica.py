import pygame
import numpy as np

# Inizializza Pygame
pygame.init()
screen_info = pygame.display.Info()
DISP_X = screen_info.current_w
DISP_Y = screen_info.current_h

pygame.font.init()
DEFAULT_FONT_SIZE = 36
font = pygame.font.SysFont(None, DEFAULT_FONT_SIZE)  
white = (255, 255, 255)
red = (255, 0 ,0)
green = (115, 160, 75)
black = (0,0,0)
light_blue = (100,190,230)
blue = (0,0,255)

radius_path = 240 # radius of the club's circular path
thickness_path = 5 # thickness in pixel of the path
# Punto di rotazione fisso (lo posizioniamo al centro della screen)
center = np.array([DISP_X // 2, DISP_Y // 2])


# Carica l'immagine della club
club_image = pygame.image.load("resources/mazza9.png")
# Image scaling
scale_club_image = 4
club_image = pygame.transform.smoothscale(club_image, (club_image.get_width() // scale_club_image, club_image.get_height() // scale_club_image))
# Ottieni il rettangolo associato all'immagine
club_rect = club_image.get_rect()
# Imposta la posizione iniziale della club
club_rect.center = center

# Carica l'immagine dello Smurf
Smurf_image = pygame.image.load("resources/puffo.png")
# Image scaling
scale_Smurf_image = 25
Smurf_image = pygame.transform.smoothscale(Smurf_image, (Smurf_image.get_width() // scale_Smurf_image, Smurf_image.get_height() // scale_Smurf_image))
# Rettangolo associato all'immagine
Smurf_rect = Smurf_image.get_rect()

# Carica l'immagine di Gargamel
gargamel_image = pygame.image.load("resources/gargamel.png")
# Image scaling
scale_gargamel_image = 12
gargamel_image = pygame.transform.smoothscale(gargamel_image, (gargamel_image.get_width() // scale_gargamel_image, gargamel_image.get_height() // scale_gargamel_image))
# Ottieni il rettangolo associato all'immagine
gargamel_rect = gargamel_image.get_rect()


background = pygame.image.load("resources/smurfs-village4.jpg")
background = pygame.transform.scale(background, (DISP_X, DISP_Y))  # Adatta l'immagine alla finestra

# Crea la screen
screen = pygame.display.set_mode((DISP_X, DISP_Y))
pygame.display.set_caption("MotoRescue - Oct 2024")

# geometric parameters describing the voltage bar
# rect_x and rect_y identify the top left corner of the background rectangle

rect_x = 30    
rect_y = DISP_Y - 70
rect_width = 300
rect_height = 30
border_thickness = 5 # distance between the moving bar inside the rectangle and the outer background rectangle 

def draw_bar(label_text, value, max_value, offset_x=0):
    label = font.render(label_text+" "+f": {value:.2f}", True, black)

    screen.blit(label, (rect_x + offset_x, rect_y - 30))
    col_background = white if abs(value) < max_value else red
    pygame.draw.rect(screen, col_background, (rect_x + offset_x, rect_y, rect_width, rect_height))

    start_x = rect_x + rect_width / 2 + offset_x
    start_y = rect_y + border_thickness
    height = rect_height - 2 * border_thickness
    width = (rect_width - 2 * border_thickness) * value / max_value / 2
    width = np.clip(width, -rect_width/2, rect_width/2) # To avoid the bar all over the place if not saturated

    if width > 1:
        pygame.draw.rect(screen, light_blue, (start_x, start_y, width, height))
    elif width < -1:
        pygame.draw.rect(screen, light_blue, (start_x + width, start_y, -width, height))
    else:
        pygame.draw.rect(screen, black, (start_x, start_y, 2, height))


def print_power(i,V,power_max):
    power = i*V
    if power<power_max:
        power_color=green
    else:
        power_color=red

    labelP = font.render(f"Power (W): {power:.1f}", True, power_color)
    offsetX = 2*(rect_width + 30)
    screen.blit(labelP, (rect_x+offsetX,rect_y))

def print_error(error):
    error_text = font.render(f"Error: {np.degrees(error):.2f}°", True, black)
    offsetX = 3*rect_width
    screen.blit(error_text, (rect_x+offsetX,rect_y))