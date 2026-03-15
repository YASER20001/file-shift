import io
import zipfile
from pathlib import Path

import openpyxl
import viktor as vkt


class Parametrization(vkt.Parametrization):
    intro = vkt.Text(
        "# File Shift\n"
        "Upload an Excel file containing **JO/EWO** (job numbers) and **File ID** (file names), "
        "then upload the source files. The app will organize them into folders by job number."
    )

    # Step 1: Excel file
    excel_heading = vkt.Text("## Step 1: Upload Excel File")
    excel_file = vkt.FileField("Excel File (.xlsx)", file_types=[".xlsx"], max_size=50_000_000)

    # Step 2: Source files
    source_heading = vkt.Text("## Step 2: Upload Source Files")
    source_files = vkt.MultiFileField("Source Files", file_types=[], max_size=50_000_000)

    # Step 3: Operation mode
    operation_heading = vkt.Text("## Step 3: Choose Operation")
    operation = vkt.OptionField(
        "Copy or Move?",
        options=["Copy", "Move"],
        default="Copy",
        description="Copy keeps originals in the download; Move only places files in job folders.",
    )


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Excel Preview", duration_guess=3)
    def preview_excel(self, params, **kwargs):
        """Show a preview of the JO/EWO and File ID columns extracted from the uploaded Excel."""
        if not params.excel_file:
            return vkt.TableResult([])

        mapping = _parse_excel(params.excel_file.file)
        data = []
        for jo, file_id in mapping:
            data.append([jo, file_id])

        return vkt.TableResult(data, column_headers=["JO/EWO", "File ID"])

    @vkt.DownloadButton("Download Organized Files", method="organize_files", longpoll=True)
    def download_btn(self, params, **kwargs):
        ...

    def organize_files(self, params, **kwargs):
        """Create a ZIP with files organized into job-number folders."""
        if not params.excel_file:
            raise vkt.UserError("Please upload an Excel file first.")
        if not params.source_files:
            raise vkt.UserError("Please upload source files first.")

        # Parse Excel to get (job_number, file_name) pairs
        mapping = _parse_excel(params.excel_file.file)

        # Build a lookup: file_name -> job_number
        file_to_job = {}
        for jo, file_id in mapping:
            file_to_job[file_id] = jo

        # Build source file lookup: filename -> file content
        source_lookup = {}
        for f in params.source_files:
            source_lookup[f.filename] = f.file

        # Create ZIP in memory
        buffer = io.BytesIO()
        matched_files = set()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_name, job_number in file_to_job.items():
                # Try exact match first, then case-insensitive
                source_file = source_lookup.get(file_name)
                if source_file is None:
                    # Try case-insensitive match
                    for src_name, src_file in source_lookup.items():
                        if src_name.lower() == file_name.lower():
                            source_file = src_file
                            file_name = src_name
                            break

                if source_file is not None:
                    matched_files.add(file_name)
                    # Place file inside job-number folder
                    archive_path = f"{job_number}/{file_name}"
                    content = source_file.getvalue_binary()
                    zf.writestr(archive_path, content)

            # If Copy mode, also include unmatched files in an "Unmatched" folder
            if params.operation == "Copy":
                for src_name, src_file in source_lookup.items():
                    if src_name not in matched_files:
                        zf.writestr(f"_Unmatched/{src_name}", src_file.getvalue_binary())

        buffer.seek(0)
        file_obj = vkt.File.from_data(buffer.read())
        return vkt.DownloadResult(file_obj, file_name="organized_files.zip")


def _parse_excel(file):
    """Parse the uploaded Excel file and return list of (jo_ewo, file_id) tuples.

    Searches for columns named 'JO/EWO' and 'File ID' (case-insensitive)
    in the header row.
    """
    content = file.getvalue_binary()
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    ws = wb.active

    # Find header row and column indices
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
        raise vkt.UserError(
            "Could not find 'JO/EWO' and 'File ID' columns in the Excel file. "
            "Please make sure the header row contains these column names."
        )

    # Extract data rows
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
