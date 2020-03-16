import math
import collections 

def leaf_order(n_leaves, section_size):
    """Compute leaf order for booklet printing."""
    
    n_sections = math.ceil(n_leaves / (section_size * 4))
    leaves = list(range(1, 1 + n_sections * section_size * 4))

    out_order = []

    for _ in range(n_sections):
        section_order = []
        section_leaves, leaves = collections.deque(leaves[:section_size*4]), leaves[section_size*4:]
        for _ in range(section_size):
            outside_left = section_leaves.pop()
            outside_right = section_leaves.popleft()
            inside_left = section_leaves.popleft()
            inside_right = section_leaves.pop()

            section_order = [inside_left, inside_right, outside_left, outside_right] + section_order
        out_order += section_order

    return out_order