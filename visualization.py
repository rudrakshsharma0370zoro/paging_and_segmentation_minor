"""
visualization.py - Educational UI & Memory Layout Visualizer
Provides styled, responsive components, memory maps, and step-by-step visual cards.
"""

from typing import List, Dict, Optional
import streamlit as st


def render_header(title: str, subtitle: str, icon: str = "🧠"):
    """Render a clean modern hero header."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            padding: 24px;
            border-radius: 12px;
            color: #F8FAFC;
            margin-bottom: 24px;
            border-left: 6px solid #38BDF8;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        ">
            <h2 style="margin: 0; color: #38BDF8; display: flex; align-items: center; gap: 10px;">
                <span>{icon}</span> {title}
            </h2>
            <p style="margin: 8px 0 0 0; color: #94A3B8; font-size: 15px;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_paging_memory_grid(
    num_frames: int,
    frame_allocation: List[Optional[int]],
    page_size: int,
    highlighted_frame: Optional[int] = None,
    cols_per_row: int = 4
):
    """
    Renders the physical memory frames as clean, colorful interactive blocks.
    """
    st.markdown("#### 🖥️ Physical Memory Frame Map (Simulated RAM)")
    st.caption("Visual distribution of fixed-size frames in physical memory. Highlighted frame indicates the active memory access.")

    cards_html = []
    for frame_idx, page_idx in enumerate(frame_allocation):
        start_addr = frame_idx * page_size
        end_addr = start_addr + page_size - 1

        is_highlighted = (highlighted_frame is not None and frame_idx == highlighted_frame)

        if is_highlighted:
            border_style = "3px solid #2563EB"
            bg_color = "#EFF6FF"
            status_badge = '<span style="background:#2563EB; color:white; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;">ACCESS TARGET</span>'
        elif page_idx is not None:
            border_style = "1px solid #10B981"
            bg_color = "#F0FDF4"
            status_badge = f'<span style="background:#10B981; color:white; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:bold;">Mapped to Page {page_idx}</span>'
        else:
            border_style = "1px dashed #CBD5E1"
            bg_color = "#F8FAFC"
            status_badge = '<span style="background:#94A3B8; color:white; padding:2px 8px; border-radius:12px; font-size:11px;">FREE FRAME</span>'

        card = f"""
        <div style="
            background: {bg_color};
            border: {border_style};
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            font-family: monospace;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        ">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-weight:bold; font-size:14px; color:#1E293B;">Frame #{frame_idx}</span>
                {status_badge}
            </div>
            <div style="font-size:12px; color:#64748B;">Physical Addr: <strong>{start_addr} - {end_addr} B</strong></div>
            <div style="font-size:11px; color:#0F172A; margin-top:4px;">
                Content: <strong>{'Page ' + str(page_idx) if page_idx is not None else 'Unallocated (Free)'}</strong>
            </div>
        </div>
        """
        cards_html.append(card)

    # Render in columns
    rows = [cards_html[i:i + cols_per_row] for i in range(0, len(cards_html), cols_per_row)]
    for row in rows:
        cols = st.columns(cols_per_row)
        for i, card in enumerate(row):
            with cols[i]:
                st.markdown(card, unsafe_allow_html=True)


def render_segmentation_memory_map(
    segments: Dict[int, any],
    total_memory: int,
    highlight_segment_id: Optional[int] = None,
    highlight_physical_addr: Optional[int] = None
):
    """
    Renders physical memory layout for segmentation, clearly showing external fragmentation / free holes.
    """
    st.markdown("#### 🗺️ Physical Memory Layout (Variable-Size Allocation)")
    st.caption("Visual demonstration of segments in physical memory. Notice unallocated gaps (external fragmentation).")

    # Sort segments by base address
    sorted_segs = sorted(segments.values(), key=lambda s: s.base)

    blocks = []
    current_ptr = 0

    palette = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#14B8A6"]

    for idx, seg in enumerate(sorted_segs):
        # Check for free hole before this segment
        if seg.base > current_ptr:
            hole_size = seg.base - current_ptr
            blocks.append({
                "type": "hole",
                "start": current_ptr,
                "end": seg.base - 1,
                "size": hole_size,
                "name": "Free Memory / Hole",
                "color": "#F1F5F9",
                "text_color": "#64748B",
                "is_active": False
            })

        color = palette[idx % len(palette)]
        is_active = (highlight_segment_id is not None and seg.segment_id == highlight_segment_id)
        blocks.append({
            "type": "segment",
            "segment_id": seg.segment_id,
            "start": seg.base,
            "end": seg.end_address(),
            "size": seg.limit,
            "name": f"Segment #{seg.segment_id}: {seg.name}",
            "color": color,
            "text_color": "#FFFFFF",
            "is_active": is_active
        })
        current_ptr = seg.end_address() + 1

    # Check for free space at end of memory
    if current_ptr < total_memory:
        blocks.append({
            "type": "hole",
            "start": current_ptr,
            "end": total_memory - 1,
            "size": total_memory - current_ptr,
            "name": "Free Memory / Hole",
            "color": "#F1F5F9",
            "text_color": "#64748B",
            "is_active": False
        })

    # Render visual layout strip
    st.markdown(
        """
        <div style="margin-bottom: 8px; font-weight:600; font-size:13px; color:#475569;">
            Memory Space: 0 to """ + str(total_memory - 1) + """ Bytes
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render segments cards list
    for b in blocks:
        if b["type"] == "segment":
            active_border = "border: 3px solid #1D4ED8; box-shadow: 0 4px 12px rgba(29, 78, 216, 0.2);" if b["is_active"] else "border: 1px solid #CBD5E1;"
            active_badge = "<span style='background:#1D4ED8; color:white; padding:2px 8px; border-radius:10px; font-size:11px; margin-left:8px;'>ACTIVE SEGMENT</span>" if b["is_active"] else ""
            
            ptr_marker = ""
            if b["is_active"] and highlight_physical_addr is not None:
                ptr_marker = f"""
                <div style="background:#FEF3C7; color:#92400E; padding:6px 10px; border-radius:6px; margin-top:6px; font-weight:bold; font-size:12px;">
                    🎯 Translated Physical Address: {highlight_physical_addr} B
                </div>
                """

            st.markdown(
                f"""
                <div style="
                    background: #FFFFFF;
                    {active_border}
                    border-left: 8px solid {b['color']};
                    border-radius: 6px;
                    padding: 12px;
                    margin-bottom: 8px;
                    font-family: monospace;
                ">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#0F172A; font-size:14px;">{b['name']}</strong>
                        <div>
                            <span style="background:{b['color']}; color:white; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:600;">Size: {b['size']} B</span>
                            {active_badge}
                        </div>
                    </div>
                    <div style="color:#475569; font-size:12px; margin-top:4px;">
                        Base Address: <strong>{b['start']} B</strong> | Limit: <strong>{b['size']} B</strong> | Range: <strong>[{b['start']} - {b['end']}]</strong>
                    </div>
                    {ptr_marker}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Free hole
            st.markdown(
                f"""
                <div style="
                    background: #F8FAFC;
                    border: 1px dashed #CBD5E1;
                    border-radius: 6px;
                    padding: 8px 12px;
                    margin-bottom: 8px;
                    font-family: monospace;
                    color: #64748B;
                    font-size: 12px;
                ">
                    ⚪ <em>{b['name']}</em> &mdash; Range: [{b['start']} - {b['end']}] &bull; Size: <strong>{b['size']} Bytes Available</strong> (External Fragmentation)
                </div>
                """,
                unsafe_allow_html=True
            )


def render_step_by_step_box(steps: List[str], success: bool = True):
    """Render educational step-by-step breakdown cards."""
    header_color = "#10B981" if success else "#EF4444"
    header_title = "✅ Step-by-Step Address Translation (MMU Execution)" if success else "❌ Address Translation Trap / Fault"

    steps_html = "".join([f"<li style='margin-bottom: 6px; color:#334155;'>{step}</li>" for step in steps])

    st.markdown(
        f"""
        <div style="
            background: #FFFFFF;
            border-left: 5px solid {header_color};
            border-radius: 8px;
            padding: 16px 20px;
            margin: 16px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.06);
            border-top: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
            border-bottom: 1px solid #E2E8F0;
        ">
            <h4 style="margin: 0 0 12px 0; color: {header_color}; font-size: 16px; display:flex; align-items:center; gap:8px;">
                {header_title}
            </h4>
            <ol style="margin: 0; padding-left: 20px; font-size: 13.5px; line-height: 1.6;">
                {steps_html}
            </ol>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_comparison_table():
    """Renders a comprehensive comparison matrix between Paging and Segmentation."""
    st.markdown(
        """
        <div style="overflow-x:auto; margin-top:16px;">
            <table style="width:100%; border-collapse:collapse; font-size:13.5px; text-align:left;">
                <thead>
                    <tr style="background:#1E293B; color:#FFFFFF;">
                        <th style="padding:10px 14px; border:1px solid #334155;">Feature / Criteria</th>
                        <th style="padding:10px 14px; border:1px solid #334155; background:#0284C7;">Paging (Fixed Size)</th>
                        <th style="padding:10px 14px; border:1px solid #334155; background:#7C3AED;">Segmentation (Variable Size)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background:#F8FAFC;">
                        <td style="padding:10px 14px; font-weight:600; border:1px solid #E2E8F0;">Unit Size</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Fixed-size blocks (e.g., 4 KB pages)</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Variable size determined by program modules</td>
                    </tr>
                    <tr style="background:#FFFFFF;">
                        <td style="padding:10px 14px; font-weight:600; border:1px solid #E2E8F0;">Programmer Visibility</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Invisible to programmer (Handled transparently by OS/MMU)</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Visible to programmer (Code, Data, Heap, Stack modules)</td>
                    </tr>
                    <tr style="background:#F8FAFC;">
                        <td style="padding:10px 14px; font-weight:600; border:1px solid #E2E8F0;">Logical Address Format</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Page Number (p) + Offset (d)</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Segment Number (s) + Offset (d)</td>
                    </tr>
                    <tr style="background:#FFFFFF;">
                        <td style="padding:10px 14px; font-weight:600; border:1px solid #E2E8F0;">Physical Address Formula</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;"><code>Physical = (Frame × Page Size) + Offset</code></td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;"><code>Physical = Base + Offset</code> (if Offset &lt; Limit)</td>
                    </tr>
                    <tr style="background:#F8FAFC;">
                        <td style="padding:10px 14px; font-weight:600; border:1px solid #E2E8F0;">Fragmentation Type</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;"><span style="color:#D97706; font-weight:bold;">Internal Fragmentation</span> (unused bytes inside the last page)</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;"><span style="color:#DC2626; font-weight:bold;">External Fragmentation</span> (variable free holes between segments)</td>
                    </tr>
                    <tr style="background:#FFFFFF;">
                        <td style="padding:10px 14px; font-weight:600; border:1px solid #E2E8F0;">Hardware Table</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Page Table (Maps Page &rarr; Frame)</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Segment Table (Contains Base &amp; Limit registers)</td>
                    </tr>
                    <tr style="background:#F8FAFC;">
                        <td style="padding:10px 14px; font-weight:600; border:1px solid #E2E8F0;">Protection &amp; Sharing</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Page-level protection bits (Read/Write/Execute)</td>
                        <td style="padding:10px 14px; border:1px solid #E2E8F0;">Natural logical module protection &amp; library sharing</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )
