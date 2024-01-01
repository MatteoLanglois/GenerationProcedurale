from numba import njit
import numpy as np
import glm
import math

# Résolution
WIN_RES = glm.vec2(1920, 1080)

# Camera
ASPECT_RATIO = WIN_RES.x / WIN_RES.y
FOV_DEG = 50
V_FOV = glm.radians(FOV_DEG)
H_FOV = 2 * math.atan(math.tan(V_FOV * 50) * ASPECT_RATIO)
NEAR = 0.1
FAR = 2000
PITCH_MAX = glm.radians(89)

# Player
PLAYER_SPEED = 0.005
PLAYER_ROT_SPEED = 0.003
PLAYER_POS = glm.vec3(0, 0, 1)
MOUSE_SENSITIVITY = 0.002

# Colors
BG_COLORS = glm.vec3(0.1, 0.16, 0.25)
