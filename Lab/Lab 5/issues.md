# Lab 5 – Identified Issues and Fixes

**Name:** Divya Gupta | **SRN:** PES2UG24CS901 | **Section:** K
**File analysed:** `loan_calculator.py` (original kept as `loan_calculator_original.py`)

## Summary

| Tool | Before | After |
|------|--------|-------|
| Bandit | 8 issues (2 High, 1 Medium, 5 Low) | No issues identified |
| Pylint | 5.17/10 | 10.00/10 |
| Flake8 | 22 warnings | 0 warnings |

## Issue Table (High and Medium severity first)

| # | Issue | Tool / Code | Type | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|---------|-------------|--------------|
| 1 | Insecure FTP import | Bandit B402 (High) | Security | 3 | `ftplib` is imported; FTP sends data and credentials in plain text (CWE-319). | Removed `ftplib` and used `paramiko` (SFTP over SSH) instead. |
| 2 | Insecure FTP call | Bandit B321 (High) | Security | 68 | `ftplib.FTP(...)` uploads credit-bureau reports unencrypted. | Rewrote `upload_to_bureau()` to use `paramiko.Transport` and `SFTPClient` on port 22, with the transport closed in a `finally` block. |
| 3 | Unsafe deserialization | Bandit B302 (Medium) | Security | 64 | `marshal.loads()` on a file can execute or crash on crafted data (CWE-502). | Replaced `marshal` with `json`, and changed the data file from `loans.bin` to `loans.json`. |
| 4 | Hardcoded password | Bandit B107 (Low) | Security | 67 | Default argument `password="Bureau#2024"` puts a secret in the source code. | Default changed to `None`; the password is read from the `BUREAU_PASSWORD` environment variable. |
| 5 | Weak random for IDs | Bandit B311 (Low) | Security | 51 | `random.randint` is not suitable for generating application IDs. | Used `secrets.randbelow()` instead. |
| 6 | Subprocess with partial path | Bandit B404 / B603 / B607 (Low) | Security | 6, 74 | `subprocess.run(["mail", ...])` runs an external program found on PATH, with user-supplied input. | Removed `subprocess`; `notify_applicant()` now sends mail with `smtplib` and `EmailMessage`. |
| 7 | Mutable default argument | Pylint W0102 | Bug | 20 | `history=[]` in `checkEligibility` is shared across every call and grows forever. | Removed the unused `history` parameter, which also fixed R0913/R0917 (too many arguments). |
| 8 | Wrong eligibility logic | Pylint R1703 / R1705 / R1714 | Bug | 24–31 | High score *or* income returned `True` before the FOIR check, so applicants with heavy EMIs were approved. Any loan type was also accepted. | Reordered checks: validate age, loan type (`VALID_LOAN_TYPES`) and income first, then `MIN_CREDIT_SCORE`, then return `existing_emi / income <= MAX_FOIR`. |
| 9 | Redefining built-in / unused variables | Pylint W0622, W0612, W0613 | Bug | 33–38 | `sum` shadowed the built-in; `month` and `annual_rate` were unused, so `maxLoanAmount` ignored interest. | Rewrote `max_loan_amount()` with the present-value formula using `annual_rate`; removed the shadowed name. |
| 10 | Files not closed safely | Pylint R1732 | Bug | 56, 63, 70 | `open()` without `with` leaks the file handle if an error occurs. | Used `with open(..., encoding="utf-8")` everywhere. |
| 11 | Global statement | Pylint W0603 | Code smell | 62 | `global applications` reassigned the module-level dict. | `load_applications()` now uses `applications.clear()` and `.update()`, with no `global`. |
| 12 | `subprocess.run` without `check` | Pylint W1510 | Bug | 74 | Failure of the mail command was silently ignored. | Fixed by removing `subprocess` (see #6). |
| 13 | Naming convention | Pylint C0103 | Style | 14–81 | Functions used camelCase (`calculateEMI`, `checkEligibility`, …). | Renamed every function to snake_case (`calculate_emi`, `check_eligibility`, …). |
| 14 | Missing docstrings | Pylint C0114 / C0116 | Style | 1, 14–93 | No module docstring or function docstrings. | Added a module docstring and a docstring to every function. |
| 15 | Unused import | Flake8 F401 / Pylint W0611 | Style | 2 | `math` was imported but never used. | Removed the import. |
| 16 | f-string without placeholders | Flake8 F541 / Pylint W1309 | Style | 104 | An f-string had no `{}` placeholders. | Changed it to a normal string. |
| 17 | Blank lines | Flake8 E302 / E305 | Formatting | 14–106 | Only one blank line between top-level definitions. | Added two blank lines before and after each function. |
| 18 | Line too long | Flake8 E501 / Pylint C0301 | Formatting | 20, 55, 70, 78, 95, 96, 100 | Lines over 79 characters. | Wrapped long calls across multiple lines inside parentheses. |
| 19 | Unnecessary else / elif / parens | Pylint R1705, C0325 | Style | 28, 79, 82 | `else` after `return` and parentheses around a return value. | De-indented the code, used plain `if`, and removed the parentheses. |

## Additional correctness fixes made while cleaning up
- `calculate_emi()` now handles a 0% interest rate (avoids division by zero).
- The demo in `main()` passed `9` instead of `0.09` as the annual rate; corrected.
- `risk_band()` checks for an invalid score (outside 300–900) first, so 950 now returns `"INVALID"`.
