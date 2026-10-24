"""
segmentation.py - Core logic for Segmentation Simulation
Operating Systems Minor Project: Memory Management Visualizer

Formulas:
- Logical Address = (Segment Number, Offset)
- Condition: 0 <= Offset < Limit
- Physical Address = Base Address + Offset
- Trap: If Offset >= Limit or Offset < 0 => Memory Protection Violation / Segment Fault
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Segment:
    segment_id: int
    name: str
    base: int
    limit: int
    description: str = ""

    def contains_offset(self, offset: int) -> bool:
        return 0 <= offset < self.limit

    def end_address(self) -> int:
        return self.base + self.limit - 1


class SegmentationSystem:
    def __init__(self, physical_memory_size: int = 2048):
        """
        Initialize the Segmentation simulation system.
        :param physical_memory_size: Size of simulated physical memory.
        """
        if physical_memory_size <= 0:
            raise ValueError("Physical memory size must be strictly positive.")

        self.physical_memory_size = physical_memory_size
        self.segments: Dict[int, Segment] = {}
        self.load_default_segments()

    def load_default_segments(self):
        """Load standard OS segment layout (Code, Data, Heap, Stack)."""
        self.segments = {
            0: Segment(segment_id=0, name="Code / Text", base=100, limit=400, description="Read-only compiled machine instructions"),
            1: Segment(segment_id=1, name="Data", base=600, limit=250, description="Global & static initialized variables"),
            2: Segment(segment_id=2, name="Heap", base=900, limit=350, description="Dynamically allocated runtime memory (malloc/new)"),
            3: Segment(segment_id=3, name="Stack", base=1400, limit=300, description="Function call frames, local variables, return addresses")
        }

    def add_or_update_segment(self, segment_id: int, name: str, base: int, limit: int, description: str = "") -> Tuple[bool, str]:
        """Add or modify a segment with boundary validation."""
        if segment_id < 0:
            return False, "Segment ID must be non-negative (>= 0)."
        if base < 0:
            return False, "Base address cannot be negative."
        if limit <= 0:
            return False, "Segment limit (size) must be greater than 0."

        if base + limit > self.physical_memory_size:
            return False, (
                f"Segment exceeds physical memory! Base ({base}) + Limit ({limit}) = "
                f"{base + limit} bytes, which exceeds total physical memory ({self.physical_memory_size} bytes)."
            )

        self.segments[segment_id] = Segment(
            segment_id=segment_id,
            name=name.strip() or f"Segment {segment_id}",
            base=base,
            limit=limit,
            description=description
        )
        return True, f"Segment {segment_id} ('{name}') saved successfully."

    def remove_segment(self, segment_id: int) -> Tuple[bool, str]:
        if segment_id in self.segments:
            name = self.segments[segment_id].name
            del self.segments[segment_id]
            return True, f"Segment {segment_id} ('{name}') removed."
        return False, f"Segment {segment_id} does not exist."

    def check_overlaps(self) -> List[Tuple[int, int]]:
        """
        Check if any active segments overlap in physical memory.
        Returns a list of pairs of overlapping segment IDs.
        """
        overlapping = []
        seg_list = list(self.segments.values())
        for i in range(len(seg_list)):
            for j in range(i + 1, len(seg_list)):
                s1 = seg_list[i]
                s2 = seg_list[j]
                # Check overlap: (StartA <= EndB) and (EndA >= StartB)
                if s1.base <= s2.end_address() and s1.end_address() >= s2.base:
                    overlapping.append((s1.segment_id, s2.segment_id))
        return overlapping

    def translate_address(self, segment_id: int, offset: int) -> Dict[str, any]:
        """
        Translate a logical address (segment_id, offset) into a physical address.
        """
        steps = [
            f"1. Input Logical Address = Segment: {segment_id}, Offset: {offset}",
        ]

        # Check if segment exists in Segment Table
        if segment_id not in self.segments:
            steps.append(f"2. MMU Segment Table Lookup failed: Segment {segment_id} is not defined.")
            steps.append("Result: Trap - Invalid Segment Error (Segment does not exist).")
            return {
                "success": False,
                "error": f"Segment #{segment_id} does not exist in the Segment Table.",
                "segment_id": segment_id,
                "offset": offset,
                "base": None,
                "limit": None,
                "physical_address": None,
                "step_by_step": steps
            }

        seg = self.segments[segment_id]
        steps.append(
            f"2. Segment Table Lookup: Segment #{segment_id} ('{seg.name}') found. Base = {seg.base}, Limit = {seg.limit}"
        )

        # Check Offset validity
        if offset < 0:
            steps.append(f"3. Offset Validation: Offset ({offset}) < 0.")
            steps.append("Result: Trap - Negative Offset Violation (Segmentation Fault).")
            return {
                "success": False,
                "error": f"Invalid Offset: {offset} is negative. Offsets must be >= 0.",
                "segment_id": segment_id,
                "offset": offset,
                "base": seg.base,
                "limit": seg.limit,
                "physical_address": None,
                "step_by_step": steps
            }

        if offset >= seg.limit:
            steps.append(
                f"3. Offset Validation: Checking (Offset < Limit) => ({offset} < {seg.limit}) is FALSE!"
            )
            steps.append(
                f"4. The requested offset ({offset}) is greater than or equal to the segment limit ({seg.limit})."
            )
            steps.append(
                "Result: Trap - Segmentation Fault! Hardware MMU triggers an addressing boundary exception to prevent illegal memory access."
            )
            return {
                "success": False,
                "error": f"Segmentation Fault: Offset ({offset}) >= Segment Limit ({seg.limit}). Access Denied.",
                "segment_id": segment_id,
                "offset": offset,
                "base": seg.base,
                "limit": seg.limit,
                "physical_address": None,
                "step_by_step": steps
            }

        # Valid Translation
        physical_address = seg.base + offset
        steps.append(f"3. Offset Validation: {offset} < {seg.limit} (Valid access within segment boundary).")
        steps.append(
            f"4. Physical Address Calculation: Physical Address = Base Address + Offset = {seg.base} + {offset} = {physical_address} bytes."
        )
        steps.append(
            f"5. Memory Location Access: Access granted to Physical Address [{physical_address}]."
        )

        return {
            "success": True,
            "segment_id": segment_id,
            "segment_name": seg.name,
            "offset": offset,
            "base": seg.base,
            "limit": seg.limit,
            "physical_address": physical_address,
            "step_by_step": steps
        }

    def get_segment_table_records(self) -> List[Dict[str, any]]:
        records = []
        for s in sorted(self.segments.values(), key=lambda x: x.segment_id):
            records.append({
                "Segment ID": s.segment_id,
                "Segment Name": s.name,
                "Base Address": s.base,
                "Limit (Size)": s.limit,
                "Physical Range": f"[{s.base} - {s.end_address()}]",
                "Description": s.description
            })
        return records
