"""
tests/test_segmentation.py - Unit tests for Segmentation Simulation
Operating Systems Minor Project
"""

import pytest
from segmentation import SegmentationSystem, Segment


def test_segmentation_initialization():
    ss = SegmentationSystem(physical_memory_size=2048)
    assert ss.physical_memory_size == 2048
    assert len(ss.segments) == 4
    assert 0 in ss.segments  # Code
    assert 1 in ss.segments  # Data
    assert 2 in ss.segments  # Heap
    assert 3 in ss.segments  # Stack


def test_segmentation_normal_translation():
    ss = SegmentationSystem(physical_memory_size=2048)
    # Segment 0: Code, base=100, limit=400
    # Valid offset = 50 -> Physical = 100 + 50 = 150
    res = ss.translate_address(segment_id=0, offset=50)
    assert res["success"] is True
    assert res["physical_address"] == 150
    assert res["base"] == 100
    assert res["limit"] == 400


def test_segmentation_boundary_offsets():
    ss = SegmentationSystem(physical_memory_size=2048)
    # Segment 1: Data, base=600, limit=250
    # Valid offsets: 0 .. 249

    # Lower boundary: offset 0
    res_zero = ss.translate_address(segment_id=1, offset=0)
    assert res_zero["success"] is True
    assert res_zero["physical_address"] == 600

    # Upper boundary: offset 249 (limit - 1)
    res_last = ss.translate_address(segment_id=1, offset=249)
    assert res_last["success"] is True
    assert res_last["physical_address"] == 849

    # Boundary violation: offset = limit (250) -> MUST FAIL (offset must be strictly < limit)
    res_limit = ss.translate_address(segment_id=1, offset=250)
    assert res_limit["success"] is False
    assert "Segmentation Fault" in res_limit["error"]

    # Boundary violation: offset > limit (300) -> MUST FAIL
    res_over = ss.translate_address(segment_id=1, offset=300)
    assert res_over["success"] is False
    assert "Segmentation Fault" in res_over["error"]


def test_segmentation_negative_offset():
    ss = SegmentationSystem(physical_memory_size=2048)
    res_neg = ss.translate_address(segment_id=0, offset=-1)
    assert res_neg["success"] is False
    assert "negative" in res_neg["error"].lower()


def test_segmentation_invalid_segment_number():
    ss = SegmentationSystem(physical_memory_size=2048)
    res = ss.translate_address(segment_id=99, offset=10)
    assert res["success"] is False
    assert "does not exist" in res["error"]


def test_segmentation_add_update_remove():
    ss = SegmentationSystem(physical_memory_size=2048)
    ok, msg = ss.add_or_update_segment(4, "SharedLib", 1800, 150, "Shared C Library")
    assert ok is True
    assert 4 in ss.segments
    assert ss.segments[4].name == "SharedLib"

    # Exceeding physical memory: Base 2000 + Limit 100 = 2100 > 2048
    ok_exceed, _ = ss.add_or_update_segment(5, "OverflowSeg", 2000, 100)
    assert ok_exceed is False

    # Remove segment
    ok_del, _ = ss.remove_segment(4)
    assert ok_del is True
    assert 4 not in ss.segments


def test_segmentation_overlap_check():
    ss = SegmentationSystem(physical_memory_size=2048)
    # Default layout has no overlaps:
    # 0: [100-499], 1: [600-849], 2: [900-1249], 3: [1400-1699]
    assert len(ss.check_overlaps()) == 0

    # Add overlapping segment at 150-300 (overlaps with Segment 0)
    ss.add_or_update_segment(9, "ClashSeg", 150, 100)
    overlaps = ss.check_overlaps()
    assert len(overlaps) > 0
    assert (0, 9) in overlaps or (9, 0) in overlaps
