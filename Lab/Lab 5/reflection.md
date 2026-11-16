# Lab 5 – Reflection

**Name:** Divya Gupta | **SRN:** PES2UG24CS901 | **Section:** K

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 formatting issues and the Pylint style warnings: missing blank lines (E302/E305), long lines (E501), the unused `math` import, the f-string without placeholders, missing docstrings, and camelCase function names. Each one points to an exact line and has a mechanical fix.

The hardest were the Bandit security issues. Replacing FTP (B402/B321) meant rewriting `upload_to_bureau()` with `paramiko` SFTP, which is a different API. Replacing `marshal` with `json` changed the storage format, so saving and loading both had to change together. Removing the hardcoded password needed a new way to supply it (an environment variable). The Pylint warnings in `checkEligibility` and `maxLoanAmount` were also hard, because they pointed to actual logic bugs. The eligibility check returned `True` before checking FOIR, and the max-loan calculation ignored the interest rate. Fixing them meant understanding what the function was supposed to do, not just silencing the warning.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Some findings were closer to "context-dependent" than real bugs. Bandit B404 flags *any* import of `subprocess` as Low severity, even though `subprocess` can be used safely with a fixed argument list and no shell. Bandit B311 flags `random` everywhere, though it only matters when the value must be unpredictable. For application IDs that is arguably the case, so I still switched to `secrets`. Pylint R0913/R0917 (too many arguments) is also a design opinion rather than an error. Here it disappeared once the unused `history` parameter was removed.

### 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint in the editor (VS Code extensions), and add them plus Bandit as **pre-commit hooks**, so issues are caught before a commit is made.
- **In CI:** add a GitHub Actions step that runs `flake8`, `pylint --fail-under=9.5` and `bandit -r .` on every push and pull request. The build fails on any High/Medium Bandit finding or a drop in the Pylint score.
- **Configuration:** keep a shared `.pylintrc`/`setup.cfg` so the whole team uses the same rules, and suppress a warning (`# nosec`, `# pylint: disable=`) only with a comment explaining why.

### 4. What tangible improvements did you observe in code quality, readability, or robustness after applying the fixes?

- **Security:** Bandit went from 8 issues (2 High, 1 Medium) to none. Reports are now uploaded over encrypted SFTP, there is no password in the source, data is stored as JSON instead of unsafe `marshal`, and no external shell command is run.
- **Correctness:** fixing the Pylint warnings uncovered real bugs. Applicants with heavy existing EMIs are no longer approved, invalid loan types like `"crypto"` are rejected, the max-loan amount now accounts for interest, and the shared mutable default list is gone.
- **Readability:** Pylint improved from **5.17/10 to 10.00/10** and Flake8 went from 22 warnings to 0. The code now follows PEP 8 naming and layout and every function has a docstring, which makes it much easier for someone else to read and maintain.
- **Robustness:** files are opened with `with` so they are always closed, the SFTP connection is closed in `finally`, and a 0% interest rate no longer causes a division by zero.
