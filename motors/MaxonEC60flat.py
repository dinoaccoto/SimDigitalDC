from math import pi

# From the datasheet of Maxon EC 60 flat, brushless, 100W (part no. 645604)
NOMINAL_VOLTAGE = 24.0 # V
NO_LOAD_SPEED = 4300.0 # rpm
NO_LOAD_SPEED *= 2.0*pi/60 # convert rpm into rad/sec
NO_LOAD_CURRENT = 0.493 # A
NOMINAL_SPEED = 3730 # rpm
NOMINAL_SPEED *= 2*pi/60 # rad/sec
NOMINAL_TORQUE = 0.272 # Nm (max continuous torque)
NOMINAL_CURRENT = 5.18 # A (max continuous current)
STALL_TORQUE = 2.51 # Nm
STALL_CURRENT = 83.2 # A
MAX_EFFICIENCY = 0.832

TERMINAL_RESISTANCE = 0.288 # Ohm
TERMINAL_INDUCTANCE = 0.279e-3 # Henry
TORQUE_CONSTANT = 52.5e-3 # Nm/A
SPEED_CONSTANT = 182 # rpm/V
SPEED_CONSTANT *= 2*pi/60 # convert rpm/V into rad/sec/V
ROTOR_INERTIA = 0.835e-4 # kg * m^2
NOMINAL_POWER = 100

# now all units are in SI