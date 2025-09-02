from Vector import vector
from Segment import segment
from Sorted_array import sorted_array


def build_half_polygon(i: vector, j: vector, verticies: list, left_obstructors: list, right_obstructors: list, midline: segment, whitelisted: any = "whitelisted", end_multiplier: float = 2.5) -> list:
    '''
    :param i: vector to use as "unit" vector in "+x" direction (a unit is the min clearance value)
    :param j: "unit" (magnitude of min clearance value) vector in "+y" direction
    :param verticies: a sorted list of verticies going in acending order in i component
    :param left_obstructors: list of all possible obstructing points on the "left" side
    :param right_obstructors: list of all possible obstructing points on the "right" side
    :param midline: a segment used for evaluating whether or not to completely box a blacklisted point
    :param whitelisted: the attribute name for determining if we are working with whitelisted vectors or not
    :param end_multiplier: a multiplier for the height of endpoints, used to solve some edge cases with intersection
    '''

    possible_obstructions = left_obstructors + verticies + right_obstructors
    offset = len(left_obstructors)

    if len(verticies) == 0:
        return []
    
    segments = []

    half_polygon = [verticies[0] - i + j, verticies[0] + i + (end_multiplier * j)] # top left, top right    for endpoint
    
    if len(verticies) == 1:
        if verticies[0][whitelisted]:
            half_polygon.append(verticies[0] + i - j)
        return half_polygon
    
    prev_vertex = verticies[0]
    index = 0
    for vertex in verticies[1:]:
        index += 1
        if abs((vertex - prev_vertex) * i) >= 2 * i * i: # if we don't have any overlapping
            if not prev_vertex[whitelisted] and midline.line_distance(prev_vertex)**2 <= 4 * i * i:
                half_polygon.append(prev_vertex + i + j) # top right
            if vertex[whitelisted]:
                if index == len(verticies) - 1:
                    half_polygon += [vertex - i + (end_multiplier * j), vertex + i + j]
                else:
                    half_polygon += [vertex - i + j, vertex + i + j] # top left, top right
            else:
                if midline.line_distance(vertex)**2 <= 4 * i * i:
                    half_polygon.append(vertex - i + j) # top left
                half_polygon += [vertex - i - j, vertex + i - j] # bottom left, bottom right
        else: # now we have some overlap we must account for
            exclusion_zone = form_exclusion_rectangle(i, j, prev_vertex, vertex)
            path = make_segments(i, j, exclusion_zone, find_obstructions(i, j, exclusion_zone, possible_obstructions, index + offset), find_obstructive_segments(i, j, exclusion_zone, segments))
            going_up = True
            if vertex * j < prev_vertex * j: # if we are going down
                going_up = False
                path.reverse()
                if not prev_vertex[whitelisted]:
                    half_polygon.pop(-1)
                else:
                    half_polygon.append(prev_vertex + i - j)
            elif prev_vertex[whitelisted]:
                half_polygon.pop(-1)
            else:
                half_polygon.append(prev_vertex + i + j)
            prev_midpoint = path[0].midpoint()
            half_polygon.append(prev_midpoint)
            for line_segment in path[1:]:
                current_midpoint = line_segment.midpoint()
                half_polygon.append(current_midpoint)
                segments.append(segment(prev_midpoint, current_midpoint))
                prev_midpoint = current_midpoint
            if vertex[whitelisted]:
                if going_up:
                    half_polygon += [vertex - i - j, vertex - i + j]
                half_polygon.append(vertex + i + j)
            else:
                if not going_up:
                    half_polygon += [vertex - i + j, vertex - i - j]
                half_polygon.append(vertex + i - j)
        prev_vertex = vertex
    return half_polygon

def form_exclusion_rectangle(i: vector, j: vector, prev_vertex: vector, vertex: vector) -> list:
    '''
    :param i: vector to use as "unit" vector in "+x" direction (a unit is the min clearance value)
    :param j: "unit" (magnitude of min clearance value) vector in "+y" direction
    :param prev_vertex: the previous vertex
    :param vertex: the current vertex we are workng with
    '''

    # just a check
    if prev_vertex * i > vertex * i or abs((vertex - prev_vertex) * i) >= 2 * i * i:
        raise ValueError("improper input")
    
    # corner order (in i - j space)
    # 4----3
    #      |
    #      |
    # 1----2
    
    if vertex * j > prev_vertex * j:
        corner4 = vertex - i - j
        corner2 = prev_vertex + i + j
        corner1 = segment(corner4, corner4 - j).intersection(segment(corner2, corner2 - i))
        corner3 = segment(corner4, corner4 + i).intersection(segment(corner2, corner2 + j))
    else:
        corner1 = vertex - i + j
        corner3 = prev_vertex + i - j
        corner2 = segment(corner1, corner1 + i).intersection(segment(corner3, corner3 - j))
        corner4 = segment(corner1, corner1 + j).intersection(segment(corner3, corner3 - i))
    return [corner1, corner2, corner3, corner4]

def make_segments(i: vector, j: vector, exclusion_zone: list, obstructions: list, obstructive_segments: list) -> list:
    '''
    :param i: vector to use as "unit" vector in "+x" direction (a unit is the min clearance value)
    :param j: "unit" (magnitude of min clearance value) vector in "+y" direction
    :param exclusion_zone: exclusion polygon in list form
    :param obstructions: list of obstructing nodes in acending order of height
    :param obstructive_segments: all previous segments in exclusion zones that intersect with the current exclusion zone
    '''

    for corner in exclusion_zone:
        corner["j"] = corner * j

    starts = sorted_array.sort([exclusion_zone[0], exclusion_zone[3]], "j")
    ends = sorted_array.sort([exclusion_zone[1], exclusion_zone[2]], "j")

    index = 0
    for v in obstructions:
        neighbors = []
        if index > 0:
            neighbors.append(obstructions[index - 1])
        index += 1
        if index < len(obstructions):
            neighbors.append(obstructions[index])
        if (v - i) * i < exclusion_zone[0] * i:
            I = i
            end_segment = segment(exclusion_zone[1], exclusion_zone[2])
        else:
            I = -1 * i
            end_segment = segment(exclusion_zone[0], exclusion_zone[3])
        for J in (-1 * j, j):
            end_line = end_segment
            start_point = v + I + J
            bottom_line = segment(start_point, start_point + I)
            end_point = bottom_line.intersection(end_line)
            for neighbor in neighbors:
                new_end_line = segment(neighbor - I + j, neighbor - I - j)
                new_end_point = bottom_line.intersection(new_end_line)
                if end_point * I > new_end_point * I and new_end_line.in_segment(new_end_point):
                    end_point = new_end_point
            
            # making sure that start point is on the "left" and end point is on the "right"
            if start_point * i > end_point * i:
                start_point, end_point = end_point, start_point
            
            path_line = segment(start_point, end_point)

            # making sure no other segments are in the way
            for line in obstructive_segments:
                if not path_line.parallel(line):
                    intersection = path_line.intersection(line)
                    if path_line.in_segment(intersection) and line.in_segment(intersection):
                        start_point = intersection
                        path_line = segment(start_point, end_point)
            
            start_point["j"] = start_point * j
            end_point["j"] = end_point * j
            starts.insert(start_point)
            ends.insert(end_point)
    lines = []
    for index in range(len(starts)):
        lines.append(segment(starts[index], ends[index]))
    return lines

def find_obstructions(i: vector, j:vector, exclusion_zone: list, verticies: list, index: int) -> list:
    '''
    :param i: vector to use as "unit" vector in "+x" direction (a unit is the min clearance value)
    :param j: "unit" (magnitude of min clearance value) vector in "+y" direction
    :param exclusion_zone: exclusion polygon in list form
    :param vertcicies: a sorted list of all verticies we are working with
    :param index: the index of the vertex we are working on
    '''

    # returns obstructions in acending order by j value

    obstructions = sorted_array([], "j_hat")

    # behind
    n = index - 2
    while n >= 0 and (verticies[n] + i) * i >= exclusion_zone[0] * i:
        if exclusion_zone[0] * j <= verticies[n] * j <= exclusion_zone[3] * j:
            obstructions.insert(verticies[n])
        n -= 1
    
    # infront
    n = index + 1
    while n < len(verticies) and (verticies[n] - i) * i <= exclusion_zone[1] * i:
        if exclusion_zone[0] * j <= verticies[n] * j <= exclusion_zone[3] * j:
            obstructions.insert(verticies[n])
        n += 1
    
    return list(obstructions)

def find_obstructive_segments(i: vector, j: vector, exclusion_zone: list, segments: list) -> list:
    '''
    :param i: vector to use as "unit" vector in "+x" direction (a unit is the min clearance value)
    :param j: "unit" (magnitude of min clearance value) vector in "+y" direction
    :param exclusion_zone: exclusion polygon in list form
    :param segments: list of all generated segments in exclusion zones
    '''
    l1 = segment(exclusion_zone[1], exclusion_zone[2])
    l2 = segment(exclusion_zone[0], exclusion_zone[3])

    obstructive_segments = []
    for line in segments:
        if l2.intersecting(line):
            obstructive_segments.append(line)
        elif l1.intersecting(line):
            obstructive_segments.append(line)
        else:
            for point in line:
                if exclusion_zone[0] * i <= point * i <= exclusion_zone[2] * i and exclusion_zone[0] * j <= point * j <= exclusion_zone[2] * j:
                    obstructive_segments.append(line)
                    break
    return obstructive_segments