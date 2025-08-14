# WALDO-slicing
Python post-processing code used for merging nozzle-toolpath g-code with lamp-toolpath g-code

1. Slice the nozzle-toolpath as normal and export into a folder named "clean_gcodes"
2. Slice the lamp-toolpath and add the following to the post-processing script:

C:\Users\...\Python311\python.exe C:\Users\olesn\Documents\Superslicer\inject_gcode_v10.py "G-code1:\Users\...\clean_gcodes\your_model.gcode,X_offset:82,Y_offset:30.5,Z_offset:1.5,fan_control:on,start_layer:8,rest1_position:230_250,rest1_time:0,extrusion_multiplier:0,retraction:16,rest2_position:200_200,rest2_time:0;

3. Change X, Y and Z-offset to match the distance from the nozzle tip to the lamp
4. Change start_layer to the layer you wnat to start fusion
