#####################   Dino Accoto, 25-30 October 2024   #######################
# 
#### 3/11:  - module "grafica.py" moved into "resources"
#           - creater folder "motors"
#           - also the motor model to be used is now declared in settings.txt rather than in this file 
#           - to do the above, importlib is used
# 
#################################################################################
import numpy as np
import sys # Used only for closing the window upon pressing ESC
import pygame # to manage the graphic interface 
from resources import grafica as gr # module to handle some graphic elements (to keep this file short)
import importlib
import ast

def load_settings(file_path):  # Load and parse settings.txt
    settings = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):  # Skip comments and blank lines
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.split("#")[0].strip()  # Remove any inline comments
                try:
                    # Safely evaluate the value, handling integers, floats, lists, etc.
                    settings[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    settings[key] = value  # Fallback to raw string if parsing fails
                    print(f"Warning: Unable to parse setting '{key}' with value '{value}'")
    return settings

# Load settings from settings.txt
settings = load_settings("settings.txt")

# Read the motor model from settings.txt
motor_model = settings.get("MOTOR_MODEL")

# Construct the module path in dot notation (e.g., "motors.MaxonEC60flat") as required by importlib
module_path = f"motors.{motor_model}"

# Import the motor module:
try:
    mt = importlib.import_module(module_path)
    print(f"Successfully imported {module_path}")
except ModuleNotFoundError as e:
    print(f"Error: {e}")

# Set parameters from settings; default values are used if any parameter is missing
target_angle = np.radians(settings.get("target_angle", 90.0))
angle_diff = np.radians(settings.get("angle_diff", 15.0))
tolerance = np.radians(settings.get("tolerance", 7.0))
cpt = settings.get("cpt", 12)
FDE_mode = settings.get("FDE_mode", True)
ca = settings.get("ca", [])
cb = settings.get("cb", [10.0])
#print("ca: ",ca,"cb: ",cb)
Kp = settings.get("Kp", 10.0)
Kd = settings.get("Kd", 0.0)
Ki = settings.get("Ki", 0.0)

CHECK_VOLTAGE_SATURATION = settings.get("CHECK_VOLTAGE_SATURATION", True)
CHECK_CURRENT_SATURATION = settings.get("CHECK_CURRENT_SATURATION", True)
max_voltage_overhoot = settings.get("max_voltage_overhoot", 2.0)
max_current_overshoot = settings.get("max_current_overshoot", 2.0)
REDUCTION_RATIO = settings.get("REDUCTION_RATIO", 9)
LOAD_INERTIA = settings.get("LOAD_INERTIA", 0.4)
AMPLIFIER = settings.get("AMPLIFIER", 1)
FPS = settings.get("FPS", 40)
N_control = settings.get("N_control", 5)
N_physics = settings.get("N_physics", 50)

max_voltage = mt.NOMINAL_VOLTAGE * max_voltage_overhoot
max_current = mt.NOMINAL_CURRENT * max_current_overshoot
J = mt.ROTOR_INERTIA + LOAD_INERTIA / REDUCTION_RATIO**2
K = mt.TORQUE_CONSTANT
b = mt.NO_LOAD_CURRENT * mt.TORQUE_CONSTANT / mt.NO_LOAD_SPEED
R = mt.TERMINAL_RESISTANCE
L = mt.TERMINAL_INDUCTANCE
time_refresh = 1 / FPS
Ts = time_refresh / N_control
dt = Ts / N_physics
step_angle = 2.0 * np.pi / cpt

print("Sampling time:", Ts * 1000, "ms")

# Set initial conditions
t = 0.0
y = [0]*len(ca) # Initialize output sequence y so to have the same length as ca
e = [0]*len(cb) # Initialize input sequence y so to have the same length as cb
theta = theta_l = 0.0 #theta angolo motore; theta_l angolo load
omega = 0.0 # initial angular speed
i = 0.0 # initial current
V = 0.0
error = 0.0
integral_error = 0.0
previous_error = 0.0

# Place Gargamel at target_angle:
gr.gargamel_rect.center = gr.center+gr.radius_path*np.array([np.cos(target_angle),-np.sin(target_angle)])

max_angle = target_angle + angle_diff # Smurf position
# place a Smurf at max_angle
gr.Smurf_rect.center = gr.center+gr.radius_path*np.array([np.cos(max_angle),-np.sin(max_angle)])

# Discrete angular values read by the encoder (attached to rotor): 
def encoder_theta(theta):
    return np.floor(theta / step_angle) * step_angle

def check_collisions(alpha):
    alpha = np.mod(alpha, 2.0*np.pi) # angle brought back to [0, 2pi], useful e.g. in case of CCW rotations 
    Gargamel_hit = False
    Smurf_hit = False
    if np.abs(alpha-target_angle)< tolerance:
        Gargamel_hit = True
    if np.abs(alpha-max_angle) < tolerance:
        Smurf_hit = True
    return [Gargamel_hit, Smurf_hit]

def insert(element, target_list):
    return [element] + target_list[:-1] # shifta a dx di uno e inserisce error in prima posizione

def saturation(val,lim_val):
    return np.clip(val, -lim_val, lim_val)

Gargamel_has_been_hit = False
Smurf_has_been_hit = False
Gargamel_hit_text = gr.font.render("Gargamel not hit", True, gr.red)
Smurf_hit_text = gr.font.render("Smurf safe", True, gr.green)

########## --- MAIN LOOP --- ##########
mouse_dragging = False
previous_mouse_angle = None

running = True
while running:
    # Update mouse position at the beginning of each loop iteration
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_dragging = True
            # Record the initial angle based on the first click
            relative_pos = np.array(mouse_pos) - gr.center
            previous_mouse_angle = np.arctan2(-relative_pos[1], relative_pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_dragging = False
            previous_mouse_angle = None  # Reset the previous angle when releasing
            theta = theta_l * REDUCTION_RATIO  # Apply the final dragged position
            omega = 0  # Reset angular velocity

    # Process mouse dragging
    if mouse_dragging and previous_mouse_angle is not None:
        # Update current mouse angle:
        relative_pos = np.array(mouse_pos) - gr.center
        current_mouse_angle = np.arctan2(-relative_pos[1], relative_pos[0])
        angle_difference = current_mouse_angle - previous_mouse_angle
        # Normalize angle_difference to be within the range [-π, π]
        angle_difference = (angle_difference + np.pi) % (2 * np.pi) - np.pi

        theta_l += angle_difference  # Update club angle based on incremental change
        previous_mouse_angle = current_mouse_angle  # Update previous angle

    # Record key strokes
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:  # Quit game if ESC is pressed
        running = False
        pygame.quit()
        sys.exit()


    ############################## DIGITAL CONTROLLER ##############################
    # Only apply controller if not dragging with the mouse
    if not mouse_dragging:
        for i in range(0, N_control):
            encoder_reading = encoder_theta(theta)
            reference = target_angle

            # Error calculation
            error = reference - encoder_reading / REDUCTION_RATIO  # From load perspective
            error = (error + np.pi) % (2 * np.pi) - np.pi  # Normalize to [-π, π]
            e = insert(error, e)  # Add error to the sequence using "insert"

            if not FDE_mode:  # Compute output using explicit formulas
                integral_error += error * Ts
                derivative_error = (error - previous_error) / Ts
                previous_error = error
                output = Kp * error + Ki * integral_error + Kd * derivative_error
            else:
                # Compute output using FDE
                output = sum(ca[i] * y[i] for i in range(len(ca))) + sum(cb[i] * e[i] for i in range(len(cb)))
                y = insert(output, y)  # Add output to the sequence of previous outputs

            # Apply voltage with saturation
            if CHECK_VOLTAGE_SATURATION:
                V = saturation(output * AMPLIFIER, max_voltage)
            else:
                V = output * AMPLIFIER

            ############################## Physics Loop ##############################
            for j in range(0, N_physics):
                omega += 1 / J * (K * i - b * omega) * dt
                i += 1 / L * (-R * i + V - K * omega) * dt
                if CHECK_CURRENT_SATURATION:
                    i = saturation(i, max_current)  # Current saturation
                theta += omega * dt
                theta_l = theta / REDUCTION_RATIO  # Angle of the club (load)
                G_hit, P_hit = check_collisions(theta_l)
                t += dt

    ############################## Graphics and Display ##############################
    if G_hit and not Gargamel_has_been_hit:
        Gargamel_has_been_hit = True
        Gargamel_hit_text = gr.font.render(f"Gargamel hit at t = {t:.3f}", True, gr.green)

    if P_hit and not Smurf_has_been_hit:
        Smurf_has_been_hit = True
        Smurf_hit_text = gr.font.render(f"Smurf hit at t = {t:.3f}", True, gr.red)

    # Draw the static and dynamic elements
    gr.screen.blit(gr.background, (0, 0))
    pygame.draw.circle(gr.screen, gr.light_blue, gr.center, 15)  # Center of rotation
    pygame.draw.circle(gr.screen, gr.light_blue, gr.center, gr.radius_path, gr.thickness_path)  # Path circle
    gr.screen.blit(gr.Smurf_image, gr.Smurf_rect)
    gr.screen.blit(gr.gargamel_image, gr.gargamel_rect)
    
    # Draw club rotated according to theta_l
    gr.club_rotated = pygame.transform.rotate(gr.club_image, np.degrees(theta_l))
    gr.club_rect_rotated = gr.club_rotated.get_rect(center=gr.center)
    gr.screen.blit(gr.club_rotated, gr.club_rect_rotated)

    # Display time and status texts
    time_text = gr.font.render(f"time: {t:.2f}", True, gr.black)
    gr.screen.blit(time_text, (30, 30))
    pygame.draw.circle(gr.screen, gr.black, (gr.DISP_X // 8, gr.DISP_Y // 2), 30, 2)
    pygame.draw.circle(gr.screen, gr.red, (gr.DISP_X // 8, gr.DISP_Y // 2 - 80 * error), 30, 1)
    gr.screen.blit(Gargamel_hit_text, (gr.DISP_X - 350, 30))
    gr.screen.blit(Smurf_hit_text, (gr.DISP_X - 350, 80))

    # Draw bars for voltage and current
    gr.draw_bar("Voltage (V)", V, max_voltage)
    gr.draw_bar("Current (A)", i, max_current, offset_x=gr.rect_width + 30)
    gr.print_power(i, V, mt.NOMINAL_POWER)
    gr.print_error(error)
    

    pygame.display.flip()  # Update the window
    pygame.time.Clock().tick(FPS)  # Set the framerate

pygame.quit()  # Quit if not running