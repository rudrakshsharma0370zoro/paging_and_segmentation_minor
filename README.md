# 🧠 Memory Management Visualizer for Paging and Segmentation

**Operating Systems Minor Project &bull; B.Tech / B.E. Semester V**  
*A standalone, interactive, educational simulator built with Python and Streamlit.*

---

## 📌 1. Project Overview & Educational Purpose

In modern operating systems, memory management is one of the most critical and complex core subsystems. Physical RAM is finite, whereas processes require protected, contiguous-appearing logical address spaces. Two foundational non-contiguous memory allocation paradigms used to achieve this are **Paging** and **Segmentation**.

Students frequently struggle to visualize how hardware **Memory Management Units (MMU)** map virtual addresses to physical memory addresses at runtime, what causes **Page Faults**, how **Segmentation Faults** are detected, and why **internal vs. external fragmentation** occurs.

This project provides an intuitive, interactive, visual simulator that enables students, professors, and systems enthusiasts to:
1. Dynamically configure simulated logical and physical memory architectures.
2. Experiment with page sizes, frame allocations, segment bases, and segment limits.
3. Perform step-by-step address translations with mathematical formulas and explanations.
4. Visualize physical RAM layout with color-coded memory blocks and free-hole markers.
5. Safely test edge cases, boundary violations, address traps, and out-of-memory states.

> [!NOTE]
> **Simulated Memory Disclaimer:**  
> This software runs purely in Python application memory. It simulates OS memory management concepts algorithmically. It **never** accesses, allocates, modifies, or inspects your computer's actual hardware RAM.

---

## 🚀 2. Features & Key Modules

### A. 📄 Paging Simulator
- **Flexible Memory Parameters:** Configure logical address space, physical RAM, and page/frame size ($2^n$ bytes).
- **Automated Metric Computation:** Computes number of logical pages, available physical frames, and memory constraints.
- **Dynamic Frame Allocation:**
  - *Contiguous Mapping:* Maps pages $0, 1, 2, \dots$ to consecutive frames.
  - *Randomized Allocation:* Simulates real OS scatter allocation into arbitrary frames.
  - *Manual Mapping:* Assign any specific page to any physical frame.
  - *Page Fault Simulation:* Demonstrates what happens when a page is unmapped (swapped out).
- **Physical RAM Frame Visualizer:** Interactive grid displaying frame status (`Mapped`, `Free`, `Access Target`) and physical byte ranges.
- **Step-by-Step Translation:** Detailed step-by-step mathematical breakdown of:
  - $\text{Page Number } (p) = \lfloor A_L / \text{Page Size} \rfloor$
  - $\text{Offset } (d) = A_L \pmod{\text{Page Size}}$
  - $\text{Physical Address } = (f \times \text{Page Size}) + d$

### B. 🧩 Segmentation Simulator
- **Logical Module Modeling:** Configure variable-sized segments such as **Code / Text**, **Data**, **Heap**, and **Stack**.
- **Segment Table Management:** Displays segment ID, name, hardware **Base Register**, **Limit (Length) Register**, and description.
- **Memory Map with Hole Visualization:** Visualizes physical RAM layout, distinctly marking allocated segments and free holes to demonstrate **External Fragmentation**.
- **Boundary & Collision Detection:** Detects memory collisions/overlaps between active segments.
- **Hardware Trap & Protection Verification:**
  - Validates $0 \le \text{Offset} < \text{Limit}$.
  - Rejects negative offsets and out-of-bounds offsets with simulated hardware Segmentation Fault traps.
  - Computes $\text{Physical Address} = \text{Base} + \text{Offset}$.

### C. ⚖️ Paging vs. Segmentation Comparative Matrix
- Comprehensive comparison table comparing unit size, programmer visibility, hardware registers, fragmentation types, and memory protection.
- Viva preparation and exam questions answering common university Operating Systems concepts (Page Fault, TLB, Internal vs. External fragmentation).

---

## 🛠️ 3. Technology Stack & Prerequisites

- **Language:** Python 3.9+ (Fully tested on Python 3.10, 3.11, 3.12, 3.13, and 3.14)
- **Web UI Framework:** [Streamlit](https://streamlit.io/) (`>= 1.30.0`)
- **Data Representation:** [Pandas](https://pandas.pydata.org/) (`>= 2.0.0`)
- **Testing Framework:** [Pytest](https://pytest.org/) (`>= 8.0.0`)
- **Hardware Requirements:** Any modern PC running Windows, macOS, or Linux (requires $< 100$ MB RAM to execute).
- **External Dependencies:** Zero! No database, no cloud services, no API keys, and no authentication required.

---

## 📂 4. Project Folder Structure

```text
paging and segmentation/
├── app.py                     # Main Streamlit dashboard and UI routing
├── paging.py                  # Paging algorithm, page table, and translation logic
├── segmentation.py            # Segmentation algorithm, segment table, and bounds check
├── visualization.py           # Styled HTML/CSS memory grids and step-by-step cards
├── conftest.py                # Pytest configuration and path resolution
├── requirements.txt           # Clean production and testing dependencies
├── .env.example               # Safe template demonstrating environment configuration
├── .gitignore                 # Excludes cache, venv, and IDE files
├── README.md                  # Complete project documentation and guide
└── tests/
    ├── test_paging.py         # 7 automated unit tests for paging logic
    └── test_segmentation.py   # 7 automated unit tests for segmentation logic
```

---

## 💻 5. Step-by-Step Installation & Run Guide

### Option A: Windows (PowerShell or Command Prompt)

1. **Clone or Download the Repository:**
   ```powershell
   git clone https://github.com/<your-username>/memory-management-visualizer.git
   cd "memory-management-visualizer"
   ```

2. **Create a Python Virtual Environment:**
   ```powershell
   python -m venv .venv
   ```

3. **Activate the Virtual Environment:**
   - In PowerShell:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
     *(If script execution is disabled, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` first)*
   - Or in Command Prompt (`cmd`):
     ```cmd
     .venv\Scripts\activate.bat
     ```

4. **Install Dependencies:**
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. **Launch the Application:**
   ```powershell
   streamlit run app.py
   ```

6. **Open in Browser:**
   The application will automatically launch at:
   `http://localhost:8501`

---

### Option B: macOS / Linux (Terminal)

1. **Clone or Download the Repository:**
   ```bash
   git clone https://github.com/<your-username>/memory-management-visualizer.git
   cd "memory-management-visualizer"
   ```

2. **Create a Python Virtual Environment:**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the Virtual Environment:**
   ```bash
   source .venv/bin/activate
   ```

4. **Install Dependencies:**
   ```bash
   python3 -m pip install --upgrade pip
   python3 -m pip install -r requirements.txt
   ```

5. **Launch the Application:**
   ```bash
   streamlit run app.py
   ```

6. **Open in Browser:**
   Visit: `http://localhost:8501`

---

## 🧪 6. Running Automated Tests

A comprehensive suite of 14 automated unit tests is included, verifying normal operations, edge boundaries, address arithmetic, and trap exceptions.

To run the tests, execute either of the following commands in your terminal:

```bash
pytest
```
or
```bash
python -m pytest
```

### Expected Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.x, pytest-9.x.x, pluggy-1.x.x
rootdir: ...
collected 14 items

tests\test_paging.py .......                                             [ 50%]
tests\test_segmentation.py .......                                       [100%]

============================= 14 passed in 0.10s ==============================
```

---

## 📖 7. Example Demonstrations & Expected Calculations

### Example 1: Paging Address Translation
- **System Parameters:**
  - Logical Memory = $64 \text{ Bytes}$
  - Physical RAM = $32 \text{ Bytes}$
  - Page Size = $8 \text{ Bytes}$
  - Total Pages = $64 / 8 = 8$ (Pages $0$ to $7$)
  - Total Frames = $32 / 8 = 4$ (Frames $0$ to $3$)
- **Frame Allocation:**
  - Page $2$ is allocated to Frame $1$.
- **User Input:**
  - Logical Address = `18`
- **Expected Calculation:**
  $$\text{Page Number } (p) = \lfloor 18 / 8 \rfloor = 2$$
  $$\text{Offset } (d) = 18 \pmod{8} = 2$$
  $$\text{Page Table Lookup: } \text{Page } 2 \rightarrow \text{Frame } 1$$
  $$\text{Physical Address } = (1 \times 8) + 2 = 10 \text{ Bytes}$$
- **Verification:**
  Entering `18` in the simulator yields Physical Address `10`, with Frame $1$ highlighted in the visual RAM grid.

---

### Example 2: Segmentation Fault / Limit Trap
- **System Parameters:**
  - Segment $1$ (`Data`): $\text{Base} = 600$, $\text{Limit} = 250$ (Valid offsets: $0$ to $249$).
- **User Input:**
  - Segment = `1`, Offset = `250`
- **Expected Calculation:**
  - Boundary check: $\text{Offset} < \text{Limit} \implies 250 < 250$ is **False**.
- **Result:**
  - Hardware MMU triggers an addressing exception: **Segmentation Fault**.
  - Access is denied and physical address calculation is aborted to protect memory.

---

## ⚠️ 8. Simulator Limitations & Scope

1. **Software Emulation:** Operates as a high-level educational simulator rather than executing within actual CPU kernel mode.
2. **Replacement Policies:** Focuses on the structural mapping of Paging and Segmentation; dynamic page replacement algorithms (FIFO, LRU, Optimal) are not included in this minor project scope.
3. **Single Process Model:** Simulates one active process address space at a time for classroom clarity.

---

## 🔧 9. Troubleshooting Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `streamlit : The term 'streamlit' is not recognized` | Virtual environment is not activated. | Run `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Mac/Linux). |
| `ModuleNotFoundError: No module named 'paging'` | Pytest run from wrong working directory. | Run `python -m pytest` or run `pytest` directly from the project root. |
| `Port 8501 is already in use` | Another Streamlit instance is running. | Run `streamlit run app.py --server.port 8502`. |
| Script execution disabled in PowerShell | Windows execution policy restriction. | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in PowerShell. |

---

## 📜 10. License & Academic Integrity

This project is created as an academic minor project for **Operating Systems (Semester V)**.  
Free to use, learn from, fork, and distribute for educational purposes.
