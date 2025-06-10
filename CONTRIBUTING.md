# Contributing to SWE‑Flow

First off, thanks for taking the time to contribute! This project benefits greatly from community involvement, whether that’s reporting issues, improving documentation, or adding new functionality.

---



## 📜 Code of Conduct

Please read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md) (coming soon) to keep the community open and welcoming.



## 🏁 Getting Started

1. **Fork** the repository and clone your fork locally.
2. Install the development environment:

   ```bash
   conda create -n sweflow python=3.12
   conda activate sweflow
   python -m pip install -e .[dev]
   ```
3. Run the full test suite to ensure everything passes on your machine:

   ```bash
   python -m pytest
   ```



## 🔖 Types of Contributions

| Type                         | What to do                                                   |
| ---------------------------- | ------------------------------------------------------------ |
| **🐞 Bug Report**             | Open an issue with a **minimal reproducible example**.       |
| **✨ Feature Idea**           | Start a discussion or issue describing the motivation and possible design. |
| **🛠️ Code Fix / Enhancement** | Create a pull request (PR) from a feature branch.            |
| **📚 Documentation**          | Improve README, API docs, or tutorial notebooks.             |
| **📊 Benchmark / Dataset**    | Share new evaluation scripts or dataset extensions.          |

---



## 🧰 Development Workflow

1. **Branch naming**
   Use `feat/<brief-description>` for new features or `fix/<issue-#>` for bug fixes.

2. **Commit style** — follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

   ```text
   feat(rdg): add call‑graph pruning for unused functions
   fix(cli): handle missing --output argument
   docs: clarify installation steps in README
   ```

3. **Keep commits small & focused**; separate formatting-only commits (`style:`) if necessary.

4. **Run linters & tests** before pushing:

   ```bash
   pre-commit run --all-files
   pytest
   ```

5. **Open a PR** against the `main` branch.
   Include context, screenshots (if UI), and reference related issues (e.g. `Fixes #42`).

6. **Review process**
   A maintainer will review within a few business days. Please be responsive to feedback.



## 🖌️ Code Style Guide

| Tool       | Purpose                                 | Command         |
| ---------- | --------------------------------------- | --------------- |
| **yapf**  | Auto-formatting (line length 100)       | `yapf .`       |
| **isort**  | Import ordering (profile=black)         | `isort .`       |



These tools run automatically via *pre-commit* hooks.

---



## 🧪 Testing Guidelines

* Place unit tests under `tests/` and mirror the package structure.
* Use **pytest** fixtures for common setups.
* When fixing a bug, add a test that fails before the fix and passes after.
* CI (GitHub Actions) will run the full suite on every PR.

---



## 📜 Documentation Updates

*Docstrings* follow the *Google* style. Significant user‑facing changes should also update:

* `README.md`
* `docs/` markdown pages
* Example notebooks in `examples/`

---



## 📜 License

By submitting a contribution you agree to license your work under the [MIT License](./LICENSE). You also certify that you have the right to license it under those terms.

---



## 🙋 Need help?

Open an issue with the **question** label or reach out to the maintainer:

* **James Zhang** – [https://github.com/Hambaobao](https://github.com/Hambaobao)

Thanks for helping make **SWE‑Flow** better! 🚀