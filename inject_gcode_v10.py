#!/usr/bin/env python3

import sys
import os
import re

def apply_offset(gcode_lines, x_offset=0.0, y_offset=0.0, z_offset=0.0, extrusion_multiplier=1.0):
    """
    Applies X, Y, and Z offsets and an extrusion multiplier to G0/G1 commands.
    This function is intended for Model 2 G-code.
    """
    offset_gcode = []
    for line in gcode_lines:
        modified_line = line
        if line.startswith("G0") or line.startswith("G1"):
            try:
                parts = line.split()
                x_found = False
                y_found = False
                z_found = False
                e_found = False 

                for i, part in enumerate(parts):
                    if part.startswith("X"):
                        try:
                            x_val = float(part[1:]) + x_offset
                            parts[i] = f"X{x_val:.3f}"
                            x_found = True
                        except ValueError:
                            pass
                    elif part.startswith("Y"):
                        try:
                            y_val = float(part[1:]) + y_offset
                            parts[i] = f"Y{y_val:.3f}"
                            y_found = True
                        except ValueError:
                            pass
                    elif part.startswith("Z"):
                        try:
                            z_val = float(part[1:]) + z_offset
                            parts[i] = f"Z{z_val:.3f}"
                            z_found = True
                        except ValueError:
                            pass
                    elif part.startswith("E"):
                        try:
                            e_val = float(part[1:]) * extrusion_multiplier
                            parts[i] = f"E{e_val:.5f}" # Use more precision for E values
                            e_found = True
                        except ValueError:
                            pass
                
                if x_found or y_found or z_found or e_found:
                    modified_line = " ".join(parts) + "\n"
            except Exception as e:
                print(f"Warning: Error processing G0/G1 line '{line.strip()}': {e}")
                pass
        offset_gcode.append(modified_line)
    return offset_gcode

def extract_layers(filepath):
    """Extracts layers from a G-code file based on ;LAYER_CHANGE."""
    layers = []
    current_layer = []
    in_layer = False
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith(";LAYER_CHANGE"):
                    if current_layer:
                        layers.append(current_layer)
                    current_layer = [line]
                    in_layer = True
                elif in_layer:
                    current_layer.append(line)
                else:
                    current_layer.append(line)
            if current_layer:
                layers.append(current_layer)
    except FileNotFoundError:
        print(f"Error: G-code file not found at {filepath}")
        sys.exit(1)
    return layers

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) != 3:
        print("Usage: append_gcode_offset.py <script_path> \"G-code1:<path_after_C>,X_offset:<value>,Y_offset:<value>,Z_offset:<value>,fan_control:<on/off>,start_layer:<value>,rest1_position:(x,y),rest1_time:<value>,extrusion_multiplier:<value>,retraction:<value>,rest2_position:(x,y),rest2_time:<value>\" <sliced_gcode_path>")
        sys.exit(1)

    argument_string = sys.argv[1]
    arguments = {}
    for item in argument_string.split(','):
        if ':' in item:
            key, value = item.split(':', 1)
            arguments[key.strip()] = value.strip()

    sliced_gcode_path = sys.argv[2]

    partial_gcode1_path = arguments.get("G-code1")
    full_gcode1_path = None
    if partial_gcode1_path:
        full_gcode1_path = "C:" + partial_gcode1_path

    x_offset_str = arguments.get("X_offset", "0.0")
    y_offset_str = arguments.get("Y_offset", "0.0")
    z_offset_str = arguments.get("Z_offset", "0.0")
    fan_control = arguments.get("fan_control", "off").lower() == "on"
    start_layer_str = arguments.get("start_layer", "1")
    rest1_position_str = arguments.get("rest1_position")
    rest1_time_str = arguments.get("rest1_time", "0.0")
    extrusion_multiplier_str = arguments.get("extrusion_multiplier", "1.0")
    retraction_str = arguments.get("retraction", "0.0")
    rest2_position_str = arguments.get("rest2_position")
    rest2_time_str = arguments.get("rest2_time", "0.0")

    try:
        x_offset = float(x_offset_str)
        y_offset = float(y_offset_str)
        z_offset = float(z_offset_str)
    except ValueError:
        print("Error: X_offset, Y_offset, and Z_offset must be numeric values.")
        sys.exit(1)

    try:
        start_layer = int(start_layer_str)
        if start_layer < 1:
            print("Warning: start_layer must be 1 or greater. Defaulting to 1.")
            start_layer = 1
    except ValueError:
        print("Error: start_layer must be an integer value. Defaulting to 1.")
        start_layer = 1

    try:
        extrusion_multiplier = float(extrusion_multiplier_str)
        if extrusion_multiplier < 0:
            print("Warning: extrusion_multiplier cannot be negative. Defaulting to 1.0.")
            extrusion_multiplier = 1.0
    except ValueError:
        print("Error: extrusion_multiplier must be a numeric value. Defaulting to 1.0.")
        extrusion_multiplier = 1.0

    try:
        retraction_length = float(retraction_str)
        if retraction_length < 0:
            print("Warning: retraction length cannot be negative. Defaulting to 0.0.")
            retraction_length = 0.0
    except ValueError:
        print("Error: retraction must be a numeric value. Defaulting to 0.0.")
        retraction_length = 0.0

    try:
        rest1_time = float(rest1_time_str)
        if rest1_time < 0:
            print("Warning: rest1_time cannot be negative. Defaulting to 0.0.")
            rest1_time = 0.0
    except ValueError:
        print("Error: rest1_time must be a numeric value. Defaulting to 0.0.")
        rest1_time = 0.0

    try:
        rest2_time = float(rest2_time_str)
        if rest2_time < 0:
            print("Warning: rest2_time cannot be negative. Defaulting to 0.0.")
            rest2_time = 0.0
    except ValueError:
        print("Error: rest2_time must be a numeric value. Defaulting to 0.0.")
        rest2_time = 0.0


    rest1_x, rest1_y = None, None
    if rest1_position_str:
        try:
            coords = rest1_position_str.split('_')
            if len(coords) == 2:
                rest1_x = float(coords[0].strip())
                rest1_y = float(coords[1].strip())
            else:
                print(f"Warning: Invalid rest1_position format: '{rest1_position_str}'. Expected x,y. Ignoring rest1 position.")
        except ValueError:
            print(f"Warning: Invalid rest1_position values: '{rest1_position_str}'. Expected numeric values. Ignoring rest1 position.")
    
    rest2_x, rest2_y = None, None
    if rest2_position_str:
        try:
            coords = rest2_position_str.split('_')
            if len(coords) == 2:
                rest2_x = float(coords[0].strip())
                rest2_y = float(coords[1].strip())
            else:
                print(f"Warning: Invalid rest2_position format: '{rest2_position_str}'. Expected x,y. Ignoring rest2 position.")
        except ValueError:
            print(f"Warning: Invalid rest2_position values: '{rest2_position_str}'. Expected numeric values. Ignoring rest2 position.")

    if full_gcode1_path:
        print(f"Currently sliced G-code path: {sliced_gcode_path}")
        print(f"G-code1 path (reconstructed): {full_gcode1_path}")
        print(f"X Offset: {x_offset}")
        print(f"Y Offset: {y_offset}")
        print(f"Z Offset: {z_offset}")
        print(f"Fan Control: {'On' if fan_control else 'Off'}")
        print(f"Interleaving starts from layer: {start_layer}")
        if rest1_x is not None and rest1_y is not None:
            print(f"Rest1 Position (Model 2 travel): X={rest1_x}, Y={rest1_y}")
        else:
            print("Rest1 Position (Model 2 travel): Not specified or invalid.")
        print(f"Rest1 Time (Model 2 travel): {rest1_time} seconds")
        if rest2_x is not None and rest2_y is not None:
            print(f"Rest2 Position (After Model 2 layer): X={rest2_x}, Y={rest2_y}")
        else:
            print("Rest2 Position (After Model 2 layer): Not specified or invalid.")
        print(f"Rest2 Time (After Model 2 layer): {rest2_time} seconds")
        print(f"Extrusion Multiplier for Model 2: {extrusion_multiplier}")
        print(f"Retraction Length: {retraction_length} mm")

        layers1 = extract_layers(full_gcode1_path)
        layers2 = extract_layers(sliced_gcode_path)

        offset_layers2 = [apply_offset(layer, x_offset, y_offset, z_offset, extrusion_multiplier) for layer in layers2]

        combined_gcode = []
        len1 = len(layers1)
        len2 = len(offset_layers2)

        combined_gcode.append("; --- Combined G-code with alternating layers and fan control ---")
        combined_gcode.append(f"; --- Interleaving starts from layer {start_layer} ---\n")

        is_filament_retracted = False 

        # Phase 1: Print layers from Model 1 only, up to (start_layer - 1)
        for i in range(min(len1, start_layer - 1)):
            combined_gcode.extend(layers1[i])
            combined_gcode.append(f"; --- Layer {i+1} from Model 1 (Pre-interleave) ---\n")
            
            # If Model 2 will follow this Model 1 layer in the interleaving phase, retract
            if retraction_length > 0 and (i + 1) >= (start_layer - 1) and (i + 1) < len2:
                combined_gcode.append(f"G1 E-{retraction_length:.3f} F3000 ; Retract filament before Model 2 (Pre-interleave)\n")
                is_filament_retracted = True

        # Phase 2: Interleave layers from start_layer onwards
        max_interleave_len = max(len1, len2)
        for i in range(start_layer - 1, max_interleave_len):
            # Print layer from Model 1
            if i < len1:
                # Unretract filament if it was retracted from the previous Model 2 layer
                if is_filament_retracted:
                    combined_gcode.append(f"G1 E{retraction_length:.3f} F3000 ; Unretract filament for Model 1\n")
                    is_filament_retracted = False

                if fan_control:
                    combined_gcode.append("M107 ; Turn off fan (Model 1)\n")
                combined_gcode.extend(layers1[i])
                combined_gcode.append(f"; --- Layer {i+1} from Model 1 ---\n")

                # Retract filament after Model 1 layer, if Model 2 is next in this cycle
                if retraction_length > 0 and (i + 1) < len2:
                    combined_gcode.append(f"G1 E-{retraction_length:.3f} F3000 ; Retract filament before Model 2\n")
                    is_filament_retracted = True

            # Print layer from Model 2
            if i < len2:
                # Find the initial X, Y, and Z coordinates for Model 2's layer
                initial_x_model2, initial_y_model2, initial_z_model2 = None, None, None
                for line_in_layer in offset_layers2[i]:
                    if (line_in_layer.startswith("G0") or line_in_layer.startswith("G1")):
                        match_x = re.search(r"X([\d.-]+)", line_in_layer)
                        match_y = re.search(r"Y([\d.-]+)", line_in_layer)
                        match_z = re.search(r"Z([\d.-]+)", line_in_layer)
                        
                        if match_x:
                            initial_x_model2 = float(match_x.group(1))
                        if match_y:
                            initial_y_model2 = float(match_y.group(1))
                        if match_z:
                            initial_z_model2 = float(match_z.group(1))
                        
                        if initial_x_model2 is not None and initial_y_model2 is not None and initial_z_model2 is not None:
                            break
                        elif initial_x_model2 is not None and initial_y_model2 is not None and initial_z_model2 is None:
                            break 


                # Add commands to combined_gcode (outside of offset_layers2[i])
                # to control the full move-to-rest-and-back sequence.
                if rest1_x is not None and rest1_y is not None:
                    combined_gcode.append(f"G0 X{rest1_x:.3f} Y{rest1_y:.3f} ; Move to rest1 position (Model 2 travel)\n")
                    if rest1_time > 0:
                        combined_gcode.append(f"G4 P{int(rest1_time * 1000)} ; Dwell at rest1 position for {rest1_time} seconds\n")

                if fan_control:
                    combined_gcode.append("M106 S255 ; Turn on fan (Model 2)\n")
                
                if rest1_x is not None and rest1_y is not None and \
                   initial_x_model2 is not None and initial_y_model2 is not None:
                    if initial_z_model2 is not None:
                        combined_gcode.append(f"G0 Z{initial_z_model2:.3f} ; Return Z from rest position (Model 2 travel)\n")
                    
                    combined_gcode.append(f"G0 X{initial_x_model2:.3f} Y{initial_y_model2:.3f} ; Return X/Y from rest position (Model 2 travel)\n")
                
                combined_gcode.extend(offset_layers2[i])
                combined_gcode.append(f"; --- Layer {i+1} from Model 2 (offset) ---\n")

                # Logic for rest2_position and rest2_time
                if rest2_x is not None and rest2_y is not None:
                    combined_gcode.append(f"G0 X{rest2_x:.3f} Y{rest2_y:.3f} ; Move to rest2 position (after Model 2 layer)\n")
                    if rest2_time > 0 and fan_control: # Turn off fan if fan_control is enabled
                        combined_gcode.append("M107 ; Turn off fan during rest2_time (Model 2)\n")
                        combined_gcode.append(f"G4 P{int(rest2_time * 1000)} ; Dwell at rest2 position for {rest2_time} seconds\n")
                    elif rest2_time > 0: # Dwell without fan control
                        combined_gcode.append(f"G4 P{int(rest2_time * 1000)} ; Dwell at rest2 position for {rest2_time} seconds\n")


        # Final unretraction if the last layer processed was Model 2 and filament is still retracted
        if is_filament_retracted:
            combined_gcode.append(f"G1 E{retraction_length:.3f} F3000 ; Final unretract after last Model 2 layer\n")
            is_filament_retracted = False # Reset state


        # Try to preserve initial commands from the sliced G-code
        initial_commands = []
        with open(sliced_gcode_path, 'r') as infile:
            for line in infile:
                if not line.startswith(";LAYER_CHANGE"):
                    initial_commands.append(line)
                else:
                    break

        # Overwrite the original sliced G-code file with the combined content
        with open(sliced_gcode_path, 'w') as outfile:
            outfile.writelines(initial_commands)
            outfile.writelines(combined_gcode)

        print("Successfully interleaved layers with fan control, start_layer, rest positions, extrusion multiplier, and retraction into the sliced G-code file.")

    else:
        print("Error: G-code1 path not specified in the arguments.")

    print("Post-processing script finished.")