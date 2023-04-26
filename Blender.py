import bpy
import numpy as np

voxel_data = np.load("C:/Users/mamac/Documents/Programmation/Python/Generation_Procédurale/map.npy", allow_pickle=True)

for x in range(voxel_data.shape[0]):
    for y in range(voxel_data.shape[1]):
        for z in range(voxel_data.shape[2]):
            if voxel_data[x][y][z] == 1:
                bpy.ops.mesh.primitive_cube_add(location=(x, y, z), size=1)