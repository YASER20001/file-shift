import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import openpyxl


class FileShiftApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Shift")
        self.root.geometry("750x550")
        self.root.resizable(False, False)

        self.excel_path = tk.StringVar()
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.operation = tk.StringVar(value="Copy")
        self.mapping = []  # list of (jo_ewo, file_id)

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # --- Step 1: Excel file ---
        frame1 = ttk.LabelFrame(self.root, text="Step 1: Excel File")
        frame1.pack(fill="x", **pad)

        ttk.Entry(frame1, textvariable=self.excel_path, state="readonly", width=70).pack(
            side="left", padx=(10, 5), pady=8
        )
        ttk.Button(frame1, text="Browse", command=self._browse_excel).pack(
            side="left", padx=5, pady=8
        )
        ttk.Button(frame1, text="Load", command=self._load_excel).pack(
            side="left", padx=5, pady=8
        )

        # --- Step 2: Source folder ---
        frame2 = ttk.LabelFrame(self.root, text="Step 2: Source Folder (where your files are)")
        frame2.pack(fill="x", **pad)

        ttk.Entry(frame2, textvariable=self.source_folder, state="readonly", width=70).pack(
            side="left", padx=(10, 5), pady=8
        )
        ttk.Button(frame2, text="Browse", command=self._browse_source).pack(
            side="left", padx=5, pady=8
        )

        # --- Step 3: Destination folder ---
        frame3 = ttk.LabelFrame(self.root, text="Step 3: Destination Folder (output)")
        frame3.pack(fill="x", **pad)

        ttk.Entry(frame3, textvariable=self.dest_folder, state="readonly", width=70).pack(
            side="left", padx=(10, 5), pady=8
        )
        ttk.Button(frame3, text="Browse", command=self._browse_dest).pack(
            side="left", padx=5, pady=8
        )

        # --- Step 4: Copy or Move ---
        frame4 = ttk.LabelFrame(self.root, text="Step 4: Operation")
        frame4.pack(fill="x", **pad)

        ttk.Radiobutton(frame4, text="Copy", variable=self.operation, value="Copy").pack(
            side="left", padx=(10, 20), pady=8
        )
        ttk.Radiobutton(frame4, text="Move", variable=self.operation, value="Move").pack(
            side="left", padx=20, pady=8
        )

        # --- Preview table ---
        table_frame = ttk.LabelFrame(self.root, text="Preview (JO/EWO  →  File ID)")
        table_frame.pack(fill="both", expand=True, **pad)

        columns = ("jo", "file_id")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("jo", text="JO/EWO")
        self.tree.heading("file_id", text="File ID")
        self.tree.column("jo", width=200)
        self.tree.column("file_id", width=480)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=5)

        # --- Run button ---
        ttk.Button(self.root, text="Run", command=self._run).pack(pady=10)

    # ------------------------------------------------------------ Callbacks
    def _browse_excel(self):
        path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )
        if path:
            self.excel_path.set(path)

    def _browse_source(self):
        path = filedialog.askdirectory(title="Select Source Folder")
        if path:
            self.source_folder.set(path)

    def _browse_dest(self):
        path = filedialog.askdirectory(title="Select Destination Folder")
        if path:
            self.dest_folder.set(path)

    def _load_excel(self):
        path = self.excel_path.get()
        if not path:
            messagebox.showwarning("No file", "Please select an Excel file first.")
            return

        try:
            self.mapping = parse_excel(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Populate the preview table
        self.tree.delete(*self.tree.get_children())
        for jo, file_id in self.mapping:
            self.tree.insert("", "end", values=(jo, file_id))

        messagebox.showinfo("Loaded", f"Found {len(self.mapping)} entries.")

    def _run(self):
        if not self.mapping:
            messagebox.showwarning("No data", "Load an Excel file first.")
            return
        if not self.source_folder.get():
            messagebox.showwarning("No source", "Select a source folder.")
            return
        if not self.dest_folder.get():
            messagebox.showwarning("No destination", "Select a destination folder.")
            return

        src = self.source_folder.get()
        dst = self.dest_folder.get()
        op = self.operation.get()

        # Build lookup of available source files (name -> full path)
        source_files = {}
        for f in os.listdir(src):
            full = os.path.join(src, f)
            if os.path.isfile(full):
                source_files[f] = full

        matched = 0
        not_found = []

        for jo, file_id in self.mapping:
            # Find the file (exact match, then case-insensitive)
            src_path = source_files.get(file_id)
            if src_path is None:
                for name, path in source_files.items():
                    if name.lower() == file_id.lower():
                        src_path = path
                        break

            if src_path is None:
                not_found.append(file_id)
                continue

            # Create job folder
            job_folder = os.path.join(dst, str(jo))
            os.makedirs(job_folder, exist_ok=True)

            dest_path = os.path.join(job_folder, os.path.basename(src_path))

            if op == "Copy":
                shutil.copy2(src_path, dest_path)
            else:
                shutil.move(src_path, dest_path)

            matched += 1

        # Summary
        msg = f"Done!\n\nMatched & {op.lower()}d: {matched} files"
        if not_found:
            msg += f"\nNot found in source folder: {len(not_found)} files\n\n"
            msg += "\n".join(not_found[:20])
            if len(not_found) > 20:
                msg += f"\n... and {len(not_found) - 20} more"

        messagebox.showinfo("Complete", msg)


def parse_excel(path):
    """Read an Excel file and return list of (jo_ewo, file_id) tuples."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active

    jo_col = None
    file_col = None
    header_row = None

    for row in ws.iter_rows(min_row=1, max_row=20):
        for cell in row:
            val = str(cell.value).strip().lower() if cell.value else ""
            if val in ("jo/ewo", "jo / ewo", "jo", "ewo", "jo/ewo number"):
                jo_col = cell.column - 1
                header_row = cell.row
            if val in ("file id", "fileid", "file_id", "file name", "filename"):
                file_col = cell.column - 1
                header_row = cell.row
        if jo_col is not None and file_col is not None:
            break

    if jo_col is None or file_col is None:
        wb.close()
        raise ValueError(
            "Could not find 'JO/EWO' and 'File ID' columns in the Excel file. "
            "Make sure the header row contains these column names."
        )

    results = []
    for row in ws.iter_rows(min_row=header_row + 1):
        cells = list(row)
        if jo_col < len(cells) and file_col < len(cells):
            jo_val = cells[jo_col].value
            file_val = cells[file_col].value
            if jo_val and file_val:
                results.append((str(jo_val).strip(), str(file_val).strip()))

    wb.close()
    return results


if __name__ == "__main__":
    root = tk.Tk()
    FileShiftApp(root)
    root.mainloop()
