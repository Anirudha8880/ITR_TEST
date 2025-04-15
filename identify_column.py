import pdfplumber
import re

# List of clean target fields
target_fields = [
    "Total of other income (i + ii + iii + iv + v + vi + vii + viii + ix + x+ xi) ",
    "Issued, Subscribed and fully Paid up",
    "Total Share Capital",
    "Surplus i.e. Balance in profit and loss account",
    "Total Reserve and Surplus",
    "Money received against share warrants",
    "Total Shareholder’s fund",
    "From Banks",
    "Total Long Term Borrowings",
    "Deferred tax Liabilities ",
    "Other Long Term Liability",
    "Long-Term Provisions",
    "Total Non-Current Liabilities",
    "Total Loans repayable on demand",
    "Total Short Term Borrowings",
    "Trades Payables -> Others",
    "Total Trade Payables",
    "Current maturities of long-term debt",
    "Total Other current liabilities",
    "Total Short Term Provisions",
    "Total Current Liabilities",
    "Gross block",
    "Depreciation   -Tangible",
    "Capital work-in-progress",
    "Total Fixed Assets",
    "Unlisted equities",
    "Total Non Current Investment",
    "Deferred tax Assets",
    "Total Long Term Loan & Advances",
    "Total Other Non Current Asset",
    "Total Non-Current Assets",
    "Total Current Investments",
    "Raw materials",
    "Work-in-progress",
    "Total Inventories",
    "Outstanding for more than 6 months",
    "Trades Receivable -> Others",
    "Total Trade Receivables",
    "Total Cash & Cash Equivalents",
    "Total Short Term Loans & Advances",
    "Other Current Assets",
    "Total Current Assets",
    "Total Opening Inventory",
    "Purchasest",
    "Direct Wages",
    "Direct Expenses",
    "Factory Overheads",
    "Total of Debits to Manufacturing Account",
    "Closing Stock",
    "Cost of Goods Produced – transferred to Trading Account",
    "A Sales/ Gross receipts of business",
    "Gross receipts from Profession",
    "Total Duties, taxes and cess received",
    "Total Revenue from Operations",
    "Total of Credits to Trading Account",
    "Duties and taxes, paid or payable",
    "Goods Cost Produced to Manufacturing Account",
    "Gross Profit Transferred from Trading Account",
    "Total of Credits to Profit & Loss Account",
    "Interest income",
    "Total of other income",
    "Power and fuel",
    "Total compensation to employees",
    "Total Expenditure on Insurance",
    "Workmen and staff welfare expenses",
    "Entertainment",
    "Hospitality",
    "Conference",
    "Sales promotion including publicity",
    "Advertisement",
    "Total Commission",
    "Total Royality",
    "Total Professional / Consultancy Fees",
    "Hotel, boarding and Lodging",
    "Traveling expenses other than on foreign traveling",
    "Foreign travelling expenses",
    "Conveyance expenses",
    "Telephone expenses",
    "Guest House expenses",
    "Club expenses",
    "Festival celebration expenses",
    "Scholarship",
    "Gift",
    "Donation",
    "Total rates and taxes paid or payable",
    "Audit Fee",
    "Total Other Expenses",
    "Total Bad Debts",
    "Profit before interest, depreciation and taxes",
    "Total Interest Expenditure",
    "Depreciation and amortization",
    "Profit Before Taxes",
    "Provision for current tax",
    "Provision for Deferred Tax",
    "Profit after tax",
    "Balance brought forward from previous year",
    "Amount available for appropriation",
    "Total Appropriations",
    "Total of Other Income",
    "Income from House Property",
    "Total Profits and gains from business or profession",
    "Total Capital Gain",
    "Total Income from other source",
    "Total of headwise Income",
    "Total Deductions under Chapter VI-A",
    "Total Income",
    "Total Tax Payable u/s 115JB",
    "Tax Payable on Total Income",
    "Total Surcharge",
    "Tax Relief",
    "Net Tax Liability",
    "Total Interest & Fee Payable",
    "Total Taxes paid"
]


def normalize(text):
    # Normalize smart quotes and apostrophes
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    # Remove whitespace, commas, dashes, and quotes
    return re.sub(r'[\s,\'"-]+', '', text.strip().lower())


def extract_field_values(pdf_path, fields):
    extracted = {field: "NA" for field in fields}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for i, row in enumerate(table):
                    if not row:
                        continue

                    # 🟡 Debugging: print rows and check if 'Factory Overheads' or 'Closing Stock' is found
                    print(f"Raw Row: {row}")  # Debugging line

                    # 🟡 Check for "Factory Overheads" (directly check without normalization for now)
                    if 'factory overheads' in ' '.join([cell or '' for cell in row]).lower() and extracted[
                        "Factory Overheads"] == "NA":
                        print(f"Found Factory Overheads Row: {row}")  # Debugging line
                        extracted["Factory Overheads"] = row[
                            1].strip()  # Taking the value from the 2nd column (not the last)

                        # Now check the next rows for "Total"
                        for j in range(i + 1, len(table)):
                            next_row = table[j]
                            if not next_row:
                                continue
                            # Look for a "Total" row
                            if 'total' in ' '.join([cell or '' for cell in next_row]).lower():
                                extracted["Factory Overheads Total"] = next_row[-1].strip()
                                break

                    # 🔵 Check for "Closing Stock" (same logic as above)
                    if 'closing stock' in ' '.join([cell or '' for cell in row]).lower() and extracted[
                        "Closing Stock"] == "NA":
                        print(f"Found Closing Stock Row: {row}")  # Debugging line
                        extracted["Closing Stock"] = row[
                            1].strip()  # Taking the value from the 2nd column (not the last)

                        # Now check the next rows for "Total"
                        for j in range(i + 1, len(table)):
                            next_row = table[j]
                            if not next_row:
                                continue
                            # Look for a "Total" row
                            if 'total' in ' '.join([cell or '' for cell in next_row]).lower():
                                extracted["Closing Stock Total"] = next_row[-1].strip()
                                break

    return extracted


# Run it
pdf_path = "D:/ITR_Documnets/MAKRAM_A.Y_2020-21.pdf"
results = extract_field_values(pdf_path, target_fields)

# Output
for field, value in results.items():
    print(f"{field}: {value}")
