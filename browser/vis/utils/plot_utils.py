import random
import colorsys


def n_cell_to_marker_size(n_cells):
    if n_cells >= 100000:
        size = 1.5
    elif n_cells >= 50000:
        size = 2
    elif n_cells >= 20000:
        size = 2.5
    elif n_cells >= 10000:
        size = 3
    elif n_cells >= 5000:
        size = 3.5
    elif n_cells >= 1000:
        size = 4
    elif n_cells >= 500:
        size = 5
    elif n_cells >= 100:
        size = 6
    elif n_cells >= 50:
        size = 7
    elif n_cells >= 10:
        size = 8
    else:
        size = 9
    return size


def assign_colors_to_co_clusters(cluster_count, seed=1024):
    if seed is not None:
        random.seed(seed)

    def generate_color():
        return "#{:02X}{:02X}{:02X}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    color_mapping = set()
    while len(color_mapping) < cluster_count:
        color_mapping.add(generate_color())

    return list(color_mapping)


# guarantee the difference of generating colors
def assign_colors_to_co_clusters_selected(cluster_count, seed=1024, min_color_distance=150):
    if seed is not None:
        random.seed(seed)

    def generate_color():
        while True:
            # Generate random hue, saturation, and value (brightness)
            h = random.uniform(0, 360)
            s = random.uniform(0.7, 1.0)  # Adjust saturation for more vibrant colors
            v = random.uniform(0.7, 1.0)  # Adjust brightness for more vibrant colors

            # Convert HSV to RGB
            r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
            r = int(r * 255)
            g = int(g * 255)
            b = int(b * 255)

            return (r, g, b)

    def calculate_color_distance(color1, color2):
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)

    def is_color_distance_satisfied(new_color, existing_colors):
        for existing_color in existing_colors:
            if calculate_color_distance(new_color, existing_color) < min_color_distance:
                return False
        return True

    color_mapping = []
    while len(color_mapping) < cluster_count:
        new_color = generate_color()

        if is_color_distance_satisfied(new_color, color_mapping):
            color_mapping.append(new_color)

    hex_color_mapping = ["#{:02X}{:02X}{:02X}".format(r, g, b) for r, g, b in color_mapping]
    return hex_color_mapping


def extract_ids(element):
    ids = []

    if isinstance(element, dict):
        if 'props' in element and 'id' in element['props']:
            ids.append(element['props']['id'])

        if 'props' in element and 'children' in element['props']:
            children = element['props']['children']
            if isinstance(children, list):
                for child in children:
                    ids.extend(extract_ids(child))
            elif isinstance(children, dict):
                ids.extend(extract_ids(children))

    elif isinstance(element, list):
        for item in element:
            ids.extend(extract_ids(item))

    return ids


def generate_custom_marks(max_value, step_ranges):
    marks = {}
    for step_range in step_ranges:
        start = step_range[0]
        end = step_range[1]
        step = step_range[2]

        current_value = start
        if current_value < max_value:
            while current_value <= end and current_value <= max_value:
                marks[round(current_value, 2)] = str(round(current_value, 2))
                current_value += step

    return marks
