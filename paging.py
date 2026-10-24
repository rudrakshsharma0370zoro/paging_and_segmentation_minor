"""
paging.py - Core logic for Paging Simulation
Operating Systems Minor Project: Memory Management Visualizer

Formulas:
- Page Number = floor(Logical Address / Page Size)
- Page Offset = Logical Address % Page Size
- Physical Address = (Frame Number * Page Size) + Page Offset
"""

from typing import Dict, List, Optional, Tuple
import math


class PagingSystem:
    def __init__(
        self,
        logical_memory_size: int,
        physical_memory_size: int,
        page_size: int,
    ):
        """
        Initialize the paging simulation system.

        :param logical_memory_size: Total logical memory space (in Bytes or KB)
        :param physical_memory_size: Total physical memory space (in Bytes or KB)
        :param page_size: Size of a single page/frame (must be a power of 2, e.g., 2, 4, 8)
        """
        if logical_memory_size <= 0:
            raise ValueError("Logical memory size must be strictly positive.")
        if physical_memory_size <= 0:
            raise ValueError("Physical memory size must be strictly positive.")
        if page_size <= 0:
            raise ValueError("Page size must be strictly positive.")
        if logical_memory_size % page_size != 0:
            raise ValueError(
                f"Logical memory size ({logical_memory_size}) must be divisible by page size ({page_size})."
            )
        if physical_memory_size % page_size != 0:
            raise ValueError(
                f"Physical memory size ({physical_memory_size}) must be divisible by page size ({page_size})."
            )

        self.logical_memory_size = logical_memory_size
        self.physical_memory_size = physical_memory_size
        self.page_size = page_size

        self.num_pages = self.logical_memory_size // self.page_size
        self.num_frames = self.physical_memory_size // self.page_size

        # Page table: page_number -> frame_number (or None if unallocated/swapped out)
        self.page_table: Dict[int, Optional[int]] = {p: None for p in range(self.num_pages)}

        # Frame allocation map: frame_number -> page_number (or None if free)
        self.frame_allocation: List[Optional[int]] = [None] * self.num_frames

    def allocate_page_to_frame(self, page_number: int, frame_number: int) -> Tuple[bool, str]:
        """
        Map a specific page to a specific frame.
        """
        if page_number < 0 or page_number >= self.num_pages:
            return False, f"Page number {page_number} is out of bounds [0, {self.num_pages - 1}]."
        if frame_number < 0 or frame_number >= self.num_frames:
            return False, f"Frame number {frame_number} is out of bounds [0, {self.num_frames - 1}]."

        # If the frame is occupied by another page, free that page's mapping first
        existing_page = self.frame_allocation[frame_number]
        if existing_page is not None and existing_page != page_number:
            self.page_table[existing_page] = None

        # If this page was previously mapped elsewhere, clear the previous frame
        prev_frame = self.page_table[page_number]
        if prev_frame is not None:
            self.frame_allocation[prev_frame] = None

        self.page_table[page_number] = frame_number
        self.frame_allocation[frame_number] = page_number
        return True, f"Page {page_number} successfully allocated to Frame {frame_number}."

    def auto_allocate_contiguous(self) -> Tuple[int, int]:
        """
        Automatically allocate pages into frames contiguously or up to available capacity.
        Returns (allocated_count, unallocated_count).
        """
        self.reset_allocations()
        allocated = 0
        limit = min(self.num_pages, self.num_frames)
        for i in range(limit):
            self.allocate_page_to_frame(page_number=i, frame_number=i)
            allocated += 1
        unallocated = self.num_pages - allocated
        return allocated, unallocated

    def auto_allocate_randomized(self, seed: Optional[int] = 42) -> Tuple[int, int]:
        """
        Simulate real operating system non-contiguous frame allocation.
        """
        import random
        self.reset_allocations()
        rng = random.Random(seed)
        available_frames = list(range(self.num_frames))
        rng.shuffle(available_frames)

        limit = min(self.num_pages, self.num_frames)
        for p in range(limit):
            f = available_frames[p]
            self.allocate_page_to_frame(page_number=p, frame_number=f)

        return limit, self.num_pages - limit

    def reset_allocations(self):
        """Clears all page and frame mappings."""
        self.page_table = {p: None for p in range(self.num_pages)}
        self.frame_allocation = [None] * self.num_frames

    def translate_address(self, logical_address: int) -> Dict[str, any]:
        """
        Translate a logical address into a physical address.
        Returns a dictionary with calculation steps, intermediate values, and status.
        """
        # Validate input
        if not isinstance(logical_address, int):
            return {
                "success": False,
                "error": "Logical address must be an integer.",
                "step_by_step": ["Invalid address format: must be an integer."]
            }

        if logical_address < 0:
            return {
                "success": False,
                "error": f"Address {logical_address} is negative. Memory addresses must be non-negative integers (>= 0).",
                "step_by_step": ["Logical addresses cannot be negative in standard architectures."]
            }

        if logical_address >= self.logical_memory_size:
            return {
                "success": False,
                "error": f"Address {logical_address} exceeds maximum logical memory capacity ({self.logical_memory_size - 1} B).",
                "step_by_step": [
                    f"Given Logical Address = {logical_address}",
                    f"Total Logical Memory Range = [0 to {self.logical_memory_size - 1}]",
                    f"Result: Segmentation Fault / Address Out of Bounds Trap triggered by Memory Management Unit (MMU)."
                ]
            }

        # Step 1: Calculate Page Number and Offset
        page_number = logical_address // self.page_size
        offset = logical_address % self.page_size

        steps = [
            f"1. Given Logical Address = {logical_address} bytes, Page Size = {self.page_size} bytes.",
            f"2. Page Number = floor(Logical Address / Page Size) = floor({logical_address} / {self.page_size}) = {page_number}",
            f"3. Page Offset (d) = Logical Address mod Page Size = {logical_address} % {self.page_size} = {offset}",
        ]

        # Step 2: Check Page Table mapping
        frame_number = self.page_table.get(page_number)
        if frame_number is None:
            steps.append(
                f"4. Lookup Page Table at index {page_number}: Frame = [Not Allocated / Page Fault]."
            )
            steps.append(
                f"Result: Page Fault! Page {page_number} is not currently loaded in physical memory (RAM)."
            )
            return {
                "success": False,
                "error": f"Page Fault: Page {page_number} is not loaded into any physical memory frame.",
                "page_number": page_number,
                "offset": offset,
                "frame_number": None,
                "physical_address": None,
                "step_by_step": steps
            }

        # Step 3: Compute Physical Address
        physical_address = (frame_number * self.page_size) + offset
        steps.append(
            f"4. Page Table Lookup: Page {page_number} maps to Physical Frame {frame_number}."
        )
        steps.append(
            f"5. Base Address of Frame {frame_number} = Frame Number * Page Size = {frame_number} * {self.page_size} = {frame_number * self.page_size}"
        )
        steps.append(
            f"6. Physical Address = (Frame Number * Page Size) + Offset = ({frame_number} * {self.page_size}) + {offset} = {physical_address} bytes."
        )

        return {
            "success": True,
            "logical_address": logical_address,
            "page_number": page_number,
            "offset": offset,
            "frame_number": frame_number,
            "physical_address": physical_address,
            "step_by_step": steps
        }

    def get_summary_metrics(self) -> Dict[str, any]:
        allocated_pages = sum(1 for f in self.page_table.values() if f is not None)
        free_frames = sum(1 for p in self.frame_allocation if p is None)
        return {
            "logical_memory_size": self.logical_memory_size,
            "physical_memory_size": self.physical_memory_size,
            "page_size": self.page_size,
            "num_pages": self.num_pages,
            "num_frames": self.num_frames,
            "allocated_pages": allocated_pages,
            "unallocated_pages": self.num_pages - allocated_pages,
            "free_frames": free_frames,
            "used_frames": self.num_frames - free_frames
        }
