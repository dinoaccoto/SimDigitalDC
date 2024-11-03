# SimDigitalDC - Simulation of DC motors digital control
## What is it about
This program allows testing of digital controllers for position control of an armature-controlled DC motor. The controller can be expressed in the most general form as a finite difference equation (FDE). If one wishes to simulate the behavior of a PID controller, it is possible to use the naive approach in which the three gains are explicitly specified.

## Instructions
bla bla

## Example controllers
ca = [2.931, -2.991, 1.165, -0.09988, -0.005737]
cb = [0, 0.06544, -0.007137, -0.1576, 0.0941, 0.005737]

ca = [1.0, 0.0]
cb = [200.5, -400, 199.5]

ca = [0.3333, 0.6667]
cb = [334.2, -666.7, 332.5]

## Interesting facts
1) The encoder resolution "cpt" has an impact not only on precision, but also on time.
2) A position control problem can be seen from the load perspective or from the motor perspective. The difference is which angle (theta_l or theta) are used for closing the loop. If the motor perspective (use of theta instead of thetha_l) is adopted, there will be larger oscillations at regime. Note: to change perspective it is necessary to modify the main python script.



### by Dino Accoto (dino.accoto@kuleuven.be)
### History
- 25-30 October 2024: physics engine, external settings file, graphic interface, mouse interaction 
- 3 November 2024: better file organization; also the motor model to be used is now declared in settings.txt. As a result, the main Python code does not need to be modified anymore.

