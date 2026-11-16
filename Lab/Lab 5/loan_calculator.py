"""Loan eligibility and EMI calculator."""
import json
import os
import secrets
import smtplib
from datetime import datetime
from email.message import EmailMessage

import paramiko

# Global loan book
applications = {}
MAX_FOIR = 0.5
MIN_CREDIT_SCORE = 600
VALID_LOAN_TYPES = ("home", "car", "personal")
BUREAU_HOST = "ftp.creditbureau.example"


def calculate_emi(principal, annual_rate, years):
    """Return the monthly EMI (annual_rate is a fraction, e.g. 0.09)."""
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def check_eligibility(age, income, credit_score, existing_emi, loan_type):
    """Return True if the applicant qualifies for the loan."""
    if not 21 <= age <= 60:
        return False
    if loan_type not in VALID_LOAN_TYPES or income <= 0:
        return False
    if credit_score < MIN_CREDIT_SCORE:
        return False
    return existing_emi / income <= MAX_FOIR


def max_loan_amount(income, existing_emi, annual_rate, years):
    """Return the largest loan the applicant's free income can service."""
    available = income * MAX_FOIR - existing_emi
    if available <= 0:
        return 0
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return available * n
    return available * ((1 + r) ** n - 1) / (r * (1 + r) ** n)


def amortisation_schedule(principal, annual_rate, years):
    """Return a list of (month, interest, balance) rows."""
    emi = calculate_emi(principal, annual_rate, years)
    balance = principal
    rows = []
    for month in range(1, years * 12 + 1):
        interest = balance * annual_rate / 12
        balance = balance - (emi - interest)
        rows.append((month, round(interest, 2), round(balance, 2)))
    return rows


def application_id():
    """Return a random application ID."""
    return "LN-" + str(secrets.randbelow(90000000) + 10000000)


def save_application(name, amount, file="loans.json"):
    """Store an application in the loan book and write it to disk."""
    app_id = application_id()
    applications[app_id] = {
        "name": name,
        "amount": amount,
        "date": str(datetime.now()),
    }
    with open(file, "w", encoding="utf-8") as f:
        json.dump(applications, f)
    return app_id


def load_applications(file="loans.json"):
    """Load applications from disk into the loan book."""
    with open(file, "r", encoding="utf-8") as f:
        applications.clear()
        applications.update(json.load(f))


def upload_to_bureau(report_path, user="loanops", password=None):
    """Upload a report to the credit bureau over SFTP."""
    password = password or os.environ["BUREAU_PASSWORD"]
    transport = paramiko.Transport((BUREAU_HOST, 22))
    try:
        transport.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(report_path, os.path.basename(report_path))
    finally:
        transport.close()


def notify_applicant(email, status):
    """Email the applicant about their loan status."""
    msg = EmailMessage()
    msg["Subject"] = "Loan " + status
    msg["From"] = "loans@bank.example"
    msg["To"] = email
    msg.set_content("Your loan status: " + status)
    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)


def interest_saved(principal, annual_rate, years, prepayment):
    """Return the total interest saved by prepaying part of the loan."""
    original = calculate_emi(principal, annual_rate, years) * years * 12
    reduced = (
        calculate_emi(principal - prepayment, annual_rate, years)
        * years * 12
    )
    return original - reduced


def risk_band(credit_score):
    """Return the risk band for a credit score."""
    if not 300 <= credit_score <= 900:
        return "INVALID"
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    return "VERY HIGH"


def main():
    """Run a short demo of the calculator."""
    print("EMI for 5L @ 9% for 5 years:", calculate_emi(500000, 0.09, 5))
    print(
        "Eligible (score 760, income 15000, EMIs 12000):",
        check_eligibility(35, 15000, 760, 12000, "personal"),
    )
    print(
        "Eligible (unknown loan type 'crypto'):",
        check_eligibility(30, 80000, 650, 0, "crypto"),
    )
    print("Max loan for income 40000:", max_loan_amount(40000, 5000, 0.09, 5))
    print("Last schedule row:", amortisation_schedule(100000, 0.12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    print(
        "Interest saved by prepaying 50000:",
        interest_saved(500000, 0.09, 5, 50000),
    )
    print("Saved as:", save_application("Anil", 500000))
    load_applications()
    print("Applications on file:", len(applications))
    print("Upload to bureau skipped (no network)")


if __name__ == "__main__":
    main()
