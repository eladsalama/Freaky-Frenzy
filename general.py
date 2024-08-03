import math
import random


import math
import heapq


def get_closest(pos, targets, white_list=None, avoid=0, max_distance=float('inf'), k=1):
    distances = []

    for target in targets:
        if (white_list and target in white_list) or random.random() < avoid:
            continue

        dist = math.hypot(target.pos[0] - pos[0], target.pos[1] - pos[1])

        if dist <= max_distance:
            distances.append((dist, target))

    # Get the k closest targets
    closest_targets = heapq.nsmallest(k, distances, key=lambda x: x[0])

    return [target for _, target in closest_targets]


def line_circle_collision(line, circle):
    # Simple line-circle collision detection
    x1, y1 = line[0]
    x2, y2 = line[1]
    cx, cy = circle.pos
    r = circle.size / 2  # Assuming enemy.size is the diameter

    # Check if either end of the line is inside the circle
    if math.dist((x1, y1), (cx, cy)) <= r or math.dist((x2, y2), (cx, cy)) <= r:
        return True

    # Check if the closest point on the line to the circle center is within the circle
    line_length = math.dist((x1, y1), (x2, y2))
    dot = ((cx - x1) * (x2 - x1) + (cy - y1) * (y2 - y1)) / (line_length ** 2)
    closest_x = x1 + dot * (x2 - x1)
    closest_y = y1 + dot * (y2 - y1)

    if 0 <= dot <= 1:  # Closest point is on the line segment
        return math.dist((closest_x, closest_y), (cx, cy)) <= r

    return False
