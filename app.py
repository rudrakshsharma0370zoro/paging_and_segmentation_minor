"""
app.py - Main Streamlit Application
Memory Management Visualizer for Paging and Segmentation
Operating Systems Minor Project
"""

import streamlit as st
import pandas as pd
from paging import PagingSystem
from segmentation import SegmentationSystem, Segment
from visualization import (
    render_header,
    render_paging_memory_grid,
    render_segmentation_memory_map,
    render_step_by_step_box,
    render_comparison_table,
)

# Page configuration
st.set_page_config(
    page_title="OS Memory Visualizer | Paging & Segmentation",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for modern academic look
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
        }
        .stAlert {
            border-radius: 8px;
        }
        .badge-sim {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 12px;
            border: 1px solid #FDE68A;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize default state variables safely."""
    if "paging_sys" not in st.session_state:
        # Default: 64 Bytes Logical Memory, 32 Bytes Physical Memory, 8 Bytes Page Size
        # (8 pages total, 4 frames total - great for demonstrating page faults / capacity limits)
        ps = PagingSystem(logical_memory_size=64, physical_memory_size=32, page_size=8)
        ps.auto_allocate_contiguous()
        st.session_state.paging_sys = ps

    if "seg_sys" not in st.session_state:
        st.session_state.seg_sys = SegmentationSystem(physical_memory_size=2048)


init_session_state()

# Sidebar Navigation & Educational Info
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    mode = st.radio(
        "Select Simulator Mode:",
        ["1. Paging Simulator", "2. Segmentation Simulator", "3. Paging vs. Segmentation", "4. Project & Theory Guide"],
        index=0,
    )

    st.markdown("---")
    st.markdown(
        """
        <div class="badge-sim">
            🛡️ Safe Sandbox: Simulated Memory Only
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "**Note:** This application executes pure algorithmic simulations in software. "
        "It does **not** access, inspect, or modify your computer's actual RAM hardware."
    )

    st.markdown("---")
    st.caption("OS Minor Project &bull; Python & Streamlit &bull; Semester V")


# -------------------------------------------------------------------------------------------------
# TAB 1: PAGING SIMULATOR
# -------------------------------------------------------------------------------------------------
if mode == "1. Paging Simulator":
    render_header(
        title="Paging Memory Management Simulator",
        subtitle="Explore fixed-size memory partitioning, frame allocations, page tables, and MMU address translation.",
        icon="📄",
    )

    # Configuration Controls
    with st.expander("⚙️ Memory Settings, Architecture & Presets (Click to open/close)", expanded=True):
        col_preset, col_reset = st.columns([3, 1])
        with col_preset:
            preset = st.selectbox(
                "Quick Presets:",
                [
                    "Custom Configuration",
                    "Classroom Demo 1: Balanced (64B Logical, 64B Physical, 8B Page)",
                    "Classroom Demo 2: Constrained RAM (64B Logical, 32B Physical, 8B Page)",
                    "Classroom Demo 3: Micro Pages (32B Logical, 32B Physical, 4B Page)",
                ],
            )
        with col_reset:
            st.write("")
            st.write("")
            if st.button("🔄 Reset Paging System", use_container_width=True):
                st.session_state.paging_sys = PagingSystem(64, 32, 8)
                st.session_state.paging_sys.auto_allocate_contiguous()
                st.rerun()

        # Handle Preset selection
        if preset == "Classroom Demo 1: Balanced (64B Logical, 64B Physical, 8B Page)":
            def_l, def_p, def_pg = 64, 64, 8
        elif preset == "Classroom Demo 2: Constrained RAM (64B Logical, 32B Physical, 8B Page)":
            def_l, def_p, def_pg = 64, 32, 8
        elif preset == "Classroom Demo 3: Micro Pages (32B Logical, 32B Physical, 4B Page)":
            def_l, def_p, def_pg = 32, 32, 4
        else:
            def_l = st.session_state.paging_sys.logical_memory_size
            def_p = st.session_state.paging_sys.physical_memory_size
            def_pg = st.session_state.paging_sys.page_size

        cfg_col1, cfg_col2, cfg_col3, cfg_col4 = st.columns(4)
        with cfg_col1:
            new_log_mem = st.number_input(
                "Logical Memory Size (Bytes):",
                min_value=8,
                max_value=1024,
                value=def_l,
                step=8,
                help="Total address space accessible to the running process.",
            )
        with cfg_col2:
            new_phys_mem = st.number_input(
                "Physical Memory Size (Bytes):",
                min_value=8,
                max_value=1024,
                value=def_p,
                step=8,
                help="Total available simulated physical RAM space.",
            )
        with cfg_col3:
            new_page_size = st.selectbox(
                "Page / Frame Size (Bytes):",
                options=[2, 4, 8, 16, 32, 64],
                index=[2, 4, 8, 16, 32, 64].index(def_pg) if def_pg in [2, 4, 8, 16, 32, 64] else 2,
                help="Fixed size of each page and physical frame (must be a power of 2).",
            )
        with cfg_col4:
            st.write("")
            st.write("")
            if st.button("Apply Parameters", type="primary", use_container_width=True):
                try:
                    new_sys = PagingSystem(new_log_mem, new_phys_mem, new_page_size)
                    new_sys.auto_allocate_contiguous()
                    st.session_state.paging_sys = new_sys
                    st.success("New memory configuration applied!")
                    st.rerun()
                except ValueError as err:
                    st.error(f"Configuration Error: {err}")

    ps: PagingSystem = st.session_state.paging_sys
    metrics = ps.get_summary_metrics()

    # KPI Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Logical Memory", f"{metrics['logical_memory_size']} B", f"{metrics['num_pages']} Pages")
    with m2:
        st.metric("Physical RAM", f"{metrics['physical_memory_size']} B", f"{metrics['num_frames']} Frames")
    with m3:
        st.metric("Page / Frame Size", f"{metrics['page_size']} B")
    with m4:
        st.metric("Allocated Pages", f"{metrics['allocated_pages']} / {metrics['num_pages']}")
    with m5:
        st.metric("Available Frames", f"{metrics['free_frames']} / {metrics['num_frames']}")

    if metrics["num_pages"] > metrics["num_frames"]:
        st.warning(
            f"⚠️ **Memory Constraint:** Logical space has {metrics['num_pages']} pages, but RAM only has {metrics['num_frames']} frames. "
            f"{metrics['num_pages'] - metrics['num_frames']} page(s) cannot reside in RAM simultaneously (Page Fault condition)."
        )

    st.markdown("---")

    # Main Paging Dashboard Layout: Left Column = Allocation & Page Table; Right Column = Memory Visual & Translation
    col_left, col_right = st.columns([1, 1.3])

    with col_left:
        st.markdown("### 📋 Page Table Configuration")
        st.caption("Inspect and map process pages to physical memory frames.")

        # Quick Allocation Buttons
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            if st.button("⚡ Contiguous Map", use_container_width=True):
                ps.auto_allocate_contiguous()
                st.rerun()
        with b_col2:
            if st.button("🔀 Randomize Frames", use_container_width=True):
                ps.auto_allocate_randomized(seed=None)
                st.rerun()
        with b_col3:
            if st.button("🗑️ Clear All", use_container_width=True):
                ps.reset_allocations()
                st.rerun()

        # Display Page Table
        table_rows = []
        for p in range(ps.num_pages):
            f = ps.page_table[p]
            status = "✅ Valid (Loaded in RAM)" if f is not None else "❌ Invalid (Page Fault)"
            frame_str = f"Frame {f}" if f is not None else "None (Swap / Disk)"
            table_rows.append({
                "Page #": p,
                "Logical Range": f"[{p * ps.page_size} - {(p + 1) * ps.page_size - 1}] B",
                "Allocated Frame": frame_str,
                "Status": status,
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        # Manual Frame Mapping
        with st.expander("✏️ Manually Map a Page to a Frame"):
            m_pcol, m_fcol, m_btncol = st.columns([1, 1, 1])
            with m_pcol:
                selected_page = st.selectbox("Select Page #:", list(range(ps.num_pages)))
            with m_fcol:
                selected_frame = st.selectbox("Assign to Frame #:", list(range(ps.num_frames)))
            with m_btncol:
                st.write("")
                st.write("")
                if st.button("Map Page", use_container_width=True):
                    ok, msg = ps.allocate_page_to_frame(selected_page, selected_frame)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with col_right:
        st.markdown("### 🔍 Logical Address Translation")
        st.caption("Enter any logical address to observe how the Memory Management Unit (MMU) calculates the physical address.")

        addr_col, btn_col = st.columns([3, 1])
        with addr_col:
            input_addr = st.number_input(
                "Enter Logical Address (in Bytes):",
                min_value=0,
                max_value=max(1024, ps.logical_memory_size * 2),
                value=min(18, ps.logical_memory_size - 1),
                step=1,
                help=f"Valid logical range for this configuration is 0 to {ps.logical_memory_size - 1} B.",
            )
        with btn_col:
            st.write("")
            st.write("")
            translate_btn = st.button("Translate Address", type="primary", use_container_width=True)

        # Translation calculation
        translation = ps.translate_address(int(input_addr))
        active_frame = translation.get("frame_number")

        if translation["success"]:
            st.success(
                f"**Physical Address Result:** `0x{translation['physical_address']:04X}` "
                f"({translation['physical_address']} Bytes) &bull; Page #{translation['page_number']} &rarr; Frame #{translation['frame_number']}, Offset = {translation['offset']} B"
            )
            render_step_by_step_box(translation["step_by_step"], success=True)
        else:
            st.error(f"**Error:** {translation['error']}")
            render_step_by_step_box(translation["step_by_step"], success=False)

        st.markdown("---")
        # Visual representation of physical memory frames
        render_paging_memory_grid(
            num_frames=ps.num_frames,
            frame_allocation=ps.frame_allocation,
            page_size=ps.page_size,
            highlighted_frame=active_frame,
            cols_per_row=4 if ps.num_frames >= 4 else ps.num_frames,
        )


# -------------------------------------------------------------------------------------------------
# TAB 2: SEGMENTATION SIMULATOR
# -------------------------------------------------------------------------------------------------
elif mode == "2. Segmentation Simulator":
    render_header(
        title="Segmentation Memory Management Simulator",
        subtitle="Explore variable-size logical program segmentation, segment tables (Base & Limit), and boundary protection.",
        icon="🧩",
    )

    seg_sys: SegmentationSystem = st.session_state.seg_sys

    with st.expander("⚙️ Segmentation Settings & Presets (Click to open/close)", expanded=True):
        p_col, r_col = st.columns([3, 1])
        with p_col:
            seg_preset = st.selectbox(
                "Presets:",
                [
                    "Standard 4-Segment OS Layout (Code, Data, Heap, Stack)",
                    "Compact Memory Layout (1024 Bytes Total)",
                    "High Fragmentation Layout",
                ],
            )
        with r_col:
            st.write("")
            st.write("")
            if st.button("🔄 Reset Segments", use_container_width=True):
                st.session_state.seg_sys = SegmentationSystem(2048)
                st.rerun()

        if seg_preset == "Compact Memory Layout (1024 Bytes Total)":
            if st.session_state.seg_sys.physical_memory_size != 1024:
                ns = SegmentationSystem(1024)
                ns.segments = {
                    0: Segment(0, "Code", base=50, limit=200, description="Compiled instructions"),
                    1: Segment(1, "Data", base=300, limit=150, description="Global data"),
                    2: Segment(2, "Stack", base=600, limit=200, description="Call stack"),
                }
                st.session_state.seg_sys = ns
                st.rerun()
        elif seg_preset == "High Fragmentation Layout":
            if len(st.session_state.seg_sys.segments) != 5 or 4 not in st.session_state.seg_sys.segments:
                ns = SegmentationSystem(2048)
                ns.segments = {
                    0: Segment(0, "Code_A", base=100, limit=150, description="Module A instructions"),
                    1: Segment(1, "Data_A", base=450, limit=180, description="Module A static data"),
                    2: Segment(2, "Code_B", base=850, limit=120, description="Module B instructions"),
                    3: Segment(3, "Heap", base=1200, limit=250, description="Dynamic allocation"),
                    4: Segment(4, "Stack", base=1700, limit=200, description="Call stack frames"),
                }
                st.session_state.seg_sys = ns
                st.rerun()

    # Metrics
    tot_mem = seg_sys.physical_memory_size
    allocated_bytes = sum(s.limit for s in seg_sys.segments.values())
    free_bytes = max(0, tot_mem - allocated_bytes)
    overlaps = seg_sys.check_overlaps()

    sm1, sm2, sm3, sm4 = st.columns(4)
    with sm1:
        st.metric("Total Simulated RAM", f"{tot_mem} Bytes")
    with sm2:
        st.metric("Configured Segments", f"{len(seg_sys.segments)} Segments")
    with sm3:
        st.metric("Allocated Segment Space", f"{allocated_bytes} Bytes")
    with sm4:
        st.metric("Unallocated Space (Free)", f"{free_bytes} Bytes")

    if overlaps:
        st.error(
            f"⚠️ **Memory Collision Detected!** The following segments overlap: {overlaps}. "
            f"In an operating system, overlapping base/limit ranges cause memory corruption."
        )

    st.markdown("---")

    seg_col_left, seg_col_right = st.columns([1.1, 1.2])

    with seg_col_left:
        st.markdown("### 📋 Segment Table")
        st.caption("Contains the hardware Base Address and Limit (Length) registers for each segment.")

        records = seg_sys.get_segment_table_records()
        if records:
            st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        else:
            st.info("No segments configured.")

        # Segment Configuration / Addition
        with st.expander("➕ Add / Edit Segment", expanded=False):
            with st.form("edit_segment_form"):
                seg_id_input = st.number_input("Segment ID #:", min_value=0, max_value=20, value=len(seg_sys.segments), step=1)
                seg_name_input = st.text_input("Segment Name:", value=f"Module_{seg_id_input}")
                seg_base_input = st.number_input("Base Address (in Bytes):", min_value=0, max_value=tot_mem - 1, value=1700, step=10)
                seg_limit_input = st.number_input("Limit / Length (in Bytes):", min_value=1, max_value=tot_mem, value=150, step=10)
                seg_desc_input = st.text_input("Description:", value="User custom segment")

                submitted = st.form_submit_button("Save Segment")
                if submitted:
                    ok, msg = seg_sys.add_or_update_segment(
                        seg_id_input, seg_name_input, seg_base_input, seg_limit_input, seg_desc_input
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        if seg_sys.segments:
            with st.expander("🗑️ Delete a Segment"):
                del_id = st.selectbox("Choose Segment ID to delete:", list(seg_sys.segments.keys()))
                if st.button("Confirm Delete", type="secondary"):
                    ok, msg = seg_sys.remove_segment(del_id)
                    st.success(msg)
                    st.rerun()

    with seg_col_right:
        st.markdown("### 🔍 Logical Address Translation")
        st.caption("Provide (Segment Number, Offset). The MMU checks `Offset < Limit` before generating the Physical Address.")

        seg_options = list(seg_sys.segments.keys()) if seg_sys.segments else [0]
        in_col1, in_col2 = st.columns(2)
        with in_col1:
            chosen_seg = st.selectbox("Select Segment Number (s):", options=seg_options, index=0)
        with in_col2:
            default_limit = seg_sys.segments[chosen_seg].limit if chosen_seg in seg_sys.segments else 100
            chosen_offset = st.number_input(
                "Enter Offset (d) in Bytes:",
                min_value=-50,
                max_value=2048,
                value=min(50, default_limit // 2),
                step=1,
                help=f"To demonstrate a trap / segmentation fault, try entering an offset >= {default_limit} or < 0.",
            )

        # Translation
        seg_res = seg_sys.translate_address(chosen_seg, int(chosen_offset))

        if seg_res["success"]:
            st.success(
                f"**Physical Address Result:** `{seg_res['physical_address']}` Bytes "
                f"(Base {seg_res['base']} + Offset {seg_res['offset']})"
            )
            render_step_by_step_box(seg_res["step_by_step"], success=True)
            highlight_seg = chosen_seg
            highlight_p_addr = seg_res["physical_address"]
        else:
            st.error(f"**Addressing Exception:** {seg_res['error']}")
            render_step_by_step_box(seg_res["step_by_step"], success=False)
            highlight_seg = chosen_seg if chosen_seg in seg_sys.segments else None
            highlight_p_addr = None

        st.markdown("---")
        # Visual physical memory map for segmentation
        render_segmentation_memory_map(
            segments=seg_sys.segments,
            total_memory=tot_mem,
            highlight_segment_id=highlight_seg,
            highlight_physical_addr=highlight_p_addr,
        )


# -------------------------------------------------------------------------------------------------
# TAB 3: PAGING VS SEGMENTATION COMPARISON
# -------------------------------------------------------------------------------------------------
elif mode == "3. Paging vs. Segmentation":
    render_header(
        title="Paging vs. Segmentation Comparative Analysis",
        subtitle="Detailed conceptual differences, hardware considerations, memory fragmentation, and trade-offs.",
        icon="⚖️",
    )

    st.markdown("### 📊 Comprehensive Comparison Matrix")
    render_comparison_table()

    st.markdown("---")
    st.markdown("### 🔬 In-Depth Concepts for Viva & Examinations")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            #### 📄 Why Paging Solves External Fragmentation
            - **Fixed Size Allocation:** In paging, physical memory is carved into uniform chunks called **frames**, and logical address space into **pages** of the identical size.
            - **No External Holes:** Because any free frame can accommodate any page, there are never scattered holes too small to fit a page.
            - **Trade-off:** Causes **Internal Fragmentation** because if a process allocates 4,097 bytes on a 4,096-byte page size system, it must consume 2 full pages (8,192 bytes), leaving 4,095 bytes unused inside the second page.
            """
        )
    with c2:
        st.markdown(
            """
            #### 🧩 Why Segmentation Matches Human Thinking
            - **Logical Structure:** Programmers do not think of their code in 4 KB blocks; they view programs as logical entities: functions (Code), global state (Data), dynamically allocated structures (Heap), and local variable stacks (Stack).
            - **Protection & Sharing:** Segments allow granular permissions (e.g., Code is marked `Execute-Only`, Data is `Read-Write`). Multiple processes can share the exact same Code segment (e.g., C Standard Library `libc`).
            - **Trade-off:** Leads to **External Fragmentation** as segments are loaded and released over time, creating unusable gaps between allocations.
            """
        )

    st.markdown("---")
    st.markdown(
        """
        #### 🚀 Modern Hybrid Approach: Segmented Paging (Intel x86)
        In modern operating systems (like Linux and Windows on x86-64), both techniques are combined:
        1. A program is divided into logical segments (Code, Data, Stack).
        2. Each segment is then internally divided into fixed-size **pages**.
        3. This captures the best of both worlds: logical modular protection and sharing without external fragmentation!
        """
    )


# -------------------------------------------------------------------------------------------------
# TAB 4: PROJECT & THEORY GUIDE
# -------------------------------------------------------------------------------------------------
elif mode == "4. Project & Theory Guide":
    render_header(
        title="Project Guide & Operating Systems Theory",
        subtitle="Mathematical derivations, educational walk-through, classroom viva questions, and architecture overview.",
        icon="📚",
    )

    t1, t2, t3 = st.tabs(["📐 Mathematical Formulations", "🎓 Teacher / Viva Questions", "🏗️ Software Architecture"])

    with t1:
        st.markdown(
            r"""
            ### Mathematical Models for Address Translation

            #### 1. Paging Translation Math
            Given:
            - Logical Address = $A_L$
            - Page Size = $S$ (Bytes)
            - Frame Number = $f$ (retrieved from Page Table at index $p$)

            $$\text{Page Number } (p) = \left\lfloor \frac{A_L}{S} \right\rfloor$$
            $$\text{Offset } (d) = A_L \pmod{S}$$
            $$\text{Physical Address } (A_P) = (f \times S) + d$$

            *Condition:* $0 \le d < S$

            ---

            #### 2. Segmentation Translation Math
            Given:
            - Logical Address Tuple = $(s, d)$ where $s$ is the Segment Index and $d$ is the Offset
            - Base Address = $B_s$ (from Segment Table at index $s$)
            - Limit / Length = $L_s$ (from Segment Table at index $s$)

            $$\text{Validity Check: } 0 \le d < L_s$$
            $$\text{If Valid: } A_P = B_s + d$$
            $$\text{If Invalid: } \text{Trap: Addressing Error / Segmentation Fault}$$
            """
        )

    with t2:
        st.markdown(
            """
            ### Common Viva & Examination Questions Answered

            **Q1: What is a Page Fault?**
            > **Answer:** A page fault is a hardware interrupt raised by the Memory Management Unit (MMU) when a program accesses a page that is mapped in its virtual address space but is not currently loaded into physical memory (RAM).

            **Q2: What is the primary difference between Internal and External Fragmentation?**
            > **Answer:** Internal fragmentation occurs when allocated storage is larger than requested storage (e.g., inside a fixed-size page). External fragmentation occurs when free memory is broken into small, non-contiguous chunks between allocated segments.

            **Q3: Can Page Size be an arbitrary number like 3,000 bytes?**
            > **Answer:** In hardware implementations, page sizes are almost always exact powers of 2 ($2^n$, such as 4,096 bytes / 4 KB). This allows the MMU hardware to extract the page number and offset using ultrafast bit-shift and bitwise-AND masking operations without performing slow integer division.

            **Q4: What is the role of the TLB (Translation Lookaside Buffer)?**
            > **Answer:** The TLB is a high-speed associative hardware cache inside the CPU that stores recent page-to-frame translations. It reduces the memory access penalty from requiring two RAM accesses (one for page table lookup, one for actual data) down to one fast cache lookup.
            """
        )

    with t3:
        st.markdown(
            """
            ### Software Architecture & Clean Code Principles
            The project is strictly modularized for educational readability:
            - `paging.py`: Clean, standalone object-oriented logic for paging, page tables, and address translation.
            - `segmentation.py`: Independent data models and bounds-checking for segment tables and offset verification.
            - `visualization.py`: Decoupled visual rendering layer using HTML/CSS memory maps and step-by-step trace boxes.
            - `app.py`: Streamlit reactive dashboard binding user inputs to simulation models.
            - `tests/`: Automated unit tests testing normal operations, zero offsets, boundary limits, and trap handling.
            """
        )
