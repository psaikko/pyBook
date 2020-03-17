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
    

