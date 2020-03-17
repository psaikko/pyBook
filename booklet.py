import math # ceil
import collections # deque
import sys # argv
import PyPDF2
import io # StringIO
import argparse

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

def reorder_pages(in_file, out_file, page_order):
    """Permute pages of in_file to out_file according to page_order."""

    writer = PyPDF2.PdfFileWriter()
    reader = PyPDF2.PdfFileReader(in_file)
    n_leaves = reader.getNumPages()

    assert n_leaves == len(page_order)

    for i in page_order:
        writer.addPage(reader.getPage(i-1))
    
    writer.write(out_file)

def merge_sheets(in_file, out_file):
    """Merge leaf-pairs into sheets for printing."""

    writer = PyPDF2.PdfFileWriter()
    reader = PyPDF2.PdfFileReader(in_file)
    n_leaves = reader.getNumPages()

    assert n_leaves % 2 == 0

    for i in range(n_leaves // 2):
        i_left = i*2
        i_right = i*2 + 1

        left_leaf = reader.getPage(i_left)
        right_leaf = reader.getPage(i_right)

        w = left_leaf.mediaBox.getWidth()

        left_leaf.mergeTranslatedPage(right_leaf, w, 0, expand=True)
        writer.addPage(left_leaf)

    writer.write(out_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A tool for reordering and merging pages for book(let) binding.")
    parser.add_argument("infile", type=argparse.FileType('rb'), 
        help="Input document")
    parser.add_argument("outfile", type=argparse.FileType('wb'),
        help="Filepath for booklet-format output")
    parser.add_argument("-s", "--section-size", type=int, default=4,
        help="Sheets per bound section. Each sheet holds four pages of the input document, two front and two back.\
             (e.g. with portraint A4-size input, sheets are landscape A3-size)")
    args = parser.parse_args()

    infile = args.infile
    outfile = args.outfile
    section_size = args.section_size

    reader = PyPDF2.PdfFileReader(infile)
    n_content_pages = reader.getNumPages()
    order = leaf_order(n_content_pages, section_size)

    padded_stream = io.BytesIO()
    ordered_stream = io.BytesIO()

    apply_padding(infile, padded_stream, len(order))
    reorder_pages(padded_stream, ordered_stream, order)
    merge_sheets(ordered_stream, outfile)
