import pytest
import booklet
import math
import PyPDF2
import io

@pytest.fixture
def pdf_stream():
    reader = PyPDF2.PdfFileReader("testdata/test.pdf")
    buffer = io.BytesIO()
    writer = PyPDF2.PdfFileWriter()
    writer.appendPagesFromReader(reader)
    writer.write(buffer)
    return buffer

def test_leaf_order_size_1():
    order = booklet.leaf_order(4, 1)
    assert order == [2, 3, 4, 1]

def test_leaf_order_size_2():
    order = booklet.leaf_order(8, 2)
    assert order == [4, 5, 6, 3, 2, 7, 8, 1]

def test_leaf_order_size_3():
    order = booklet.leaf_order(12, 3)
    assert order == [6, 7, 8, 5, 4, 9, 10, 3, 2, 11, 12, 1]

def test_leaf_order_two_sections():
    for n_leaves in range(5, 9):
        order = booklet.leaf_order(n_leaves, 1)
        assert order == [2, 3, 4, 1, 6, 7, 8, 5]

def test_leaf_order_padding():
    for n_leaves in range(1,20):
        for section_size in range(1, 5):
            order = booklet.leaf_order(n_leaves, section_size)
            n_booklet_leaves = len(order)
            n_sections = math.ceil(n_leaves / (section_size * 4))
            assert n_booklet_leaves == n_sections * section_size * 4

def test_pdf_padding(pdf_stream):
    out_stream = io.BytesIO()
    booklet.apply_padding(pdf_stream, out_stream, 18)
    reader = PyPDF2.PdfFileReader(out_stream)
    assert reader.getNumPages() == 18
    
def test_reordering(pdf_stream):
    reader = PyPDF2.PdfFileReader(pdf_stream)
    n_content_pages = reader.getNumPages()
    order = booklet.leaf_order(n_content_pages, 1)

    padded_stream = io.BytesIO()
    booklet.apply_padding(pdf_stream, padded_stream, len(order))

    ordered_stream = io.BytesIO()
    booklet.reorder_pages(padded_stream, ordered_stream, order)

    ordered_reader = PyPDF2.PdfFileReader(ordered_stream)
    n_booklet_leaves = ordered_reader.getNumPages()

    for i in range(n_booklet_leaves):
        if order[i] < n_content_pages:
            page_i = ordered_reader.getPage(i)
            page_text = page_i.extractText()
            page_string = "Page%d" % order[i]
            assert page_string in page_text

def test_merging(pdf_stream):
    reader = PyPDF2.PdfFileReader(pdf_stream)
    n_content_pages = reader.getNumPages()
    order = booklet.leaf_order(n_content_pages, 1)

    padded_stream = io.BytesIO()
    ordered_stream = io.BytesIO()
    merged_stream = io.BytesIO()

    booklet.apply_padding(pdf_stream, padded_stream, len(order))
    booklet.reorder_pages(padded_stream, ordered_stream, order)
    booklet.merge_sheets(ordered_stream, merged_stream)

    merged_reader = PyPDF2.PdfFileReader(merged_stream)

    for i in range(merged_reader.getNumPages()):
        sheet_i = merged_reader.getPage(i)
        if sheet_i.getContents():
            sheet_text = sheet_i.extractText()
            left_i = order[i*2]
            right_i = order[i*2 + 1]

            right_page_string = "Page%d" % left_i
            left_page_string = "Page%d" % right_i

            if left_i < n_content_pages:
                assert left_page_string in sheet_text
            if right_i < n_content_pages:
                assert right_page_string in sheet_text