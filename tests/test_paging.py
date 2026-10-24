"""
tests/test_paging.py - Unit tests for Paging Simulation
Operating Systems Minor Project
"""

import pytest
from paging import PagingSystem


def test_paging_initialization():
    ps = PagingSystem(logical_memory_size=64, physical_memory_size=32, page_size=8)
    assert ps.num_pages == 8
    assert ps.num_frames == 4
    assert len(ps.page_table) == 8
    assert len(ps.frame_allocation) == 4


def test_paging_invalid_init_parameters():
    with pytest.raises(ValueError, match="Logical memory size must be strictly positive"):
        PagingSystem(0, 32, 8)

    with pytest.raises(ValueError, match="Physical memory size must be strictly positive"):
        PagingSystem(64, -10, 8)

    with pytest.raises(ValueError, match="Page size must be strictly positive"):
        PagingSystem(64, 32, 0)

    with pytest.raises(ValueError, match="must be divisible by page size"):
        PagingSystem(65, 32, 8)


def test_paging_allocation_and_reallocation():
    ps = PagingSystem(logical_memory_size=64, physical_memory_size=32, page_size=8)
    ok, msg = ps.allocate_page_to_frame(0, 2)
    assert ok is True
    assert ps.page_table[0] == 2
    assert ps.frame_allocation[2] == 0

    # Out of bounds page
    ok_oob, _ = ps.allocate_page_to_frame(99, 1)
    assert ok_oob is False

    # Out of bounds frame
    ok_oob2, _ = ps.allocate_page_to_frame(1, 99)
    assert ok_oob2 is False


def test_paging_address_translation_normal_case():
    # 64B logical, 32B physical, 8B page size
    # Page 0: [0 - 7], Page 1: [8 - 15], Page 2: [16 - 23], etc.
    ps = PagingSystem(logical_memory_size=64, physical_memory_size=32, page_size=8)
    ps.allocate_page_to_frame(page_number=2, frame_number=1)

    # Logical address 18:
    # Page = 18 // 8 = 2
    # Offset = 18 % 8 = 2
    # Frame = 1
    # Physical = (1 * 8) + 2 = 10
    res = ps.translate_address(18)
    assert res["success"] is True
    assert res["page_number"] == 2
    assert res["offset"] == 2
    assert res["frame_number"] == 1
    assert res["physical_address"] == 10


def test_paging_boundary_addresses():
    ps = PagingSystem(logical_memory_size=32, physical_memory_size=32, page_size=8)
    ps.auto_allocate_contiguous()

    # Lower boundary: Address 0
    res_zero = ps.translate_address(0)
    assert res_zero["success"] is True
    assert res_zero["page_number"] == 0
    assert res_zero["offset"] == 0
    assert res_zero["physical_address"] == 0

    # Exact page boundary: Address 8 (start of page 1)
    res_eight = ps.translate_address(8)
    assert res_eight["success"] is True
    assert res_eight["page_number"] == 1
    assert res_eight["offset"] == 0
    assert res_eight["physical_address"] == 8

    # Upper valid boundary: Address 31 (last byte of logical space)
    res_last = ps.translate_address(31)
    assert res_last["success"] is True
    assert res_last["page_number"] == 3
    assert res_last["offset"] == 7
    assert res_last["physical_address"] == 31


def test_paging_out_of_bounds_and_negative():
    ps = PagingSystem(logical_memory_size=64, physical_memory_size=64, page_size=8)
    ps.auto_allocate_contiguous()

    # Negative address
    res_neg = ps.translate_address(-5)
    assert res_neg["success"] is False
    assert "negative" in res_neg["error"].lower()

    # Address equal to logical memory size (out of range, valid is 0..63)
    res_edge = ps.translate_address(64)
    assert res_edge["success"] is False
    assert "exceeds maximum" in res_edge["error"].lower()

    # Huge out of range address
    res_huge = ps.translate_address(5000)
    assert res_huge["success"] is False


def test_paging_page_fault_unallocated():
    ps = PagingSystem(logical_memory_size=64, physical_memory_size=32, page_size=8)
    # No pages allocated yet
    res = ps.translate_address(10)
    assert res["success"] is False
    assert "Page Fault" in res["error"]
    assert res["page_number"] == 1
    assert res["offset"] == 2
    assert res["physical_address"] is None
