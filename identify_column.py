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
    "Total Factory Overheads",
    "Total of Debits to Manufacturing Account",
    "Total Closing Stock",
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
    normalized_targets = {normalize(f): f for f in fields}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    joined_row = ' '.join([cell or '' for cell in row])
                    norm_joined = normalize(joined_row)

                    for norm_target, original_field in normalized_targets.items():
                        if norm_target in norm_joined and extracted[original_field] == "NA":
                            values = [cell for cell in row if cell and cell.strip()]
                            if values:
                                extracted[original_field] = values[-1].strip()

    return extracted

# Run it
pdf_path = "D:/ITR_Documnets/MAKRAM_A.Y_2020-21.pdf"
results = extract_field_values(pdf_path, target_fields)

# Output
for field, value in results.items():
    print(f"{field}: {value}")
