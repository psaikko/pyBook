import math # ceil
import collections # deque
import sys # argv
import PyPDF2
import io # StringIO

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

def apply_padding(in_file, out_file, pad_to_length):
    """Pad PDF file to specified length with empty pages."""

    writer = PyPDF2.PdfFileWriter()
    reader = PyPDF2.PdfFileReader(in_file)

    in_page_count = reader.getNumPages()
    writer.appendPagesFromReader(reader)

    for _ in range(pad_to_length - in_page_count):
        writer.addBlankPage()
    
    writer.write(out_file)



    
