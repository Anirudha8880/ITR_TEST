import fitz  # PyMuPDF
import pdfplumber
import os
import re
import json
import tempfile
from paddleocr import PaddleOCR
from sentence_transformers import SentenceTransformer, util

# Load model and embed target fields
model = SentenceTransformer('all-MiniLM-L6-v2')

with open("field_list.txt", "r", encoding="utf-8") as f:
    TARGET_FIELDS = [line.strip() for line in f if line.strip()]

field_embeddings = model.encode(TARGET_FIELDS, convert_to_tensor=True)

def is_scanned_pdf(filepath):
    with fitz.open(filepath) as doc:
        for page in doc:
            if page.get_text().strip():
                return False
    return True

def extract_with_tables_and_lines(filepath):
    lines = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.splitlines())
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row:
                        combined = " ".join(cell.strip() for cell in row if cell)
                        if combined:
                            lines.append(combined)
    return lines

def extract_with_layout_ocr(filepath):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    doc = fitz.open(filepath)
    lines = []
    for i in range(len(doc)):
        page = doc[i]
        pix = page.get_pixmap()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            pix.save(tmp.name)
            result = ocr.ocr(tmp.name, cls=True)
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    if text.strip():
                        lines.append(text.strip())
    return lines

def clean_value(val):
    return val.replace(",", "").strip()

def extract_value_from_line(line):
    matches = re.findall(r"[-]?\d+[\d,]*\.?\d*", line)
    if matches:
        return clean_value(matches[-1])
    return None

def match_fields(lines):
    results = {}
    context_flags = {
        "in_pnl": False,
        "in_trading": False,
        "in_balance": False
    }

    interest_income_found = False

    for idx, line in enumerate(lines):
        lower_line = line.lower()

        if "profit and loss account" in lower_line:
            context_flags["in_pnl"] = True
        if "trading account" in lower_line:
            context_flags["in_trading"] = True
        if "balance sheet" in lower_line or "balance as on" in lower_line:
            context_flags["in_balance"] = True

        # Special case for Total Non-Current Assets
        if "2. current assets" in lower_line:
            for i in range(idx - 3, idx):
                if "1f" in lines[i].lower():
                    val = extract_value_from_line(lines[i])
                    if val:
                        results["Total Non-Current Assets"] = val

        # Extract "Other Current Assets" value from the line above "Total Current Assets"
        if "total current assets" in lower_line:
            if idx > 0:  # Make sure we have a line above
                prev_line = lines[idx - 1]
                value = extract_value_from_line(prev_line)
                if value:
                    results["Other Current Assets"] = value

        # Extract "Total Opening Inventory" from line below "Opening stock of Work in progress" that contains "Total"
        if "opening stock of work in progress" in lower_line:
            found_total = False
            for offset in range(1, 4):  # look 3 lines ahead
                if idx + offset < len(lines):
                    next_line = lines[idx + offset]
                    if "total" in next_line.lower():
                        value = extract_value_from_line(next_line)
                        if value:
                            results["Total Opening Inventory"] = value
                            found_total = True
                            break
            if not found_total:
                results["Total Opening Inventory"] = "NA"

        # Handle case where "Total of Debits to Manufacturing Account" is present but no value
        if "total of debits to manufacturing account" in lower_line:
            value = extract_value_from_line(line)
            if value:
                results["Total of Debits to Manufacturing Account"] = value
            else:
                results["Total of Debits to Manufacturing Account"] = "NA"

        # Extract "Closing Stock" value from line containing "Total" after "Closing Stock"
        if "closing stock" in lower_line and "closing stock as per books" not in lower_line:
            found_closing_total = False
            for offset in range(1, 4):
                if idx + offset < len(lines):
                    next_line = lines[idx + offset]
                    if "total" in next_line.lower():
                        # Extract only if number is at end of line
                        match = re.search(r"([-+]?\d{1,3}(?:,\d{2,3})*(?:\.\d+)?|\d+(?:\.\d+)?)[\s]*$", next_line)
                        if match:
                            value = clean_value(match.group(1))
                            results["Closing Stock"] = value
                            found_closing_total = True
                            break
            if not found_closing_total:
                results["Closing Stock"] = "NA"



        clean_line = re.sub(r"[^\w\s:\-.()&]", "", line)
        label_val = extract_value_from_line(clean_line)
        if not label_val:
            continue

        label_part = clean_line.replace(label_val, "").strip()
        if not label_part:
            continue

        label_embedding = model.encode(label_part, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(label_embedding, field_embeddings)[0]
        best_idx = int(scores.argmax())
        best_score = float(scores[best_idx])

        if best_score > 0.75:
            field = TARGET_FIELDS[best_idx]

            if field in ["Depreciation and amortization", "Provision for Deferred Tax", "Interest income"] and not context_flags["in_pnl"]:
                continue

            if field not in results:
                results[field] = label_val
            else:
                try:
                    if float(label_val) > float(results[field]):
                        results[field] = label_val
                except:
                    continue

            if field == "Interest income":
                interest_income_found = True

    final_results = {field: results.get(field, None) for field in TARGET_FIELDS}
    return final_results

def extract_itr_data(filepath):
    print(f"\n📄 Processing: {os.path.basename(filepath)}")
    lines = extract_with_layout_ocr(filepath) if is_scanned_pdf(filepath) else extract_with_tables_and_lines(filepath)
    matched = match_fields(lines)
    print("\n📝 JSON Output:")
    print(json.dumps({k: v for k, v in matched.items() if v is not None}, indent=2))
    return matched

if __name__ == "__main__":
    extract_itr_data(r"D:/ITR_Documnets/MAKRAM_A.Y_2020-21.pdf")
