# Contributing to SmartHire API

Thank you for your interest in contributing to **SmartHire API**! We welcome contributions from developers of all skill levels.

---

## 📋 Code of Conduct

This project and everyone participating in it is governed by the [SmartHire Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## 🛠️ How to Contribute

### 1. Reporting Bugs
- Check existing issues to see if the bug has already been reported.
- If not, create a new issue using the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).
- Include detailed reproduction steps, Django error traces, and environment details.

### 2. Suggesting Features
- Open a feature request issue using the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).
- Describe the motivation, use case, and proposed implementation details.

### 3. Pull Request (PR) Workflow
1. **Fork** the repository and create your branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Follow PEP-8** standards for Python formatting.
3. **Write tests** for any new features or bug fixes.
4. **Run migrations** and verify tests pass:
   ```bash
   python manage.py test
   ```
5. **Commit your changes** following conventional commit syntax:
   - `feat:` New features
   - `fix:` Bug fixes
   - `refactor:` Code refactoring without behavioral changes
   - `docs:` Documentation updates
   - `test:` Adding or updating tests
6. **Push** to your fork and submit a Pull Request to `main`.

---

## 📝 Commit Conventions
We use the [Conventional Commits](https://www.conventionalcommits.org/) specification:
```
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```
Example:
```
feat(ai_engine): add weighted skill matching threshold
fix(candidates): resolve resume upload parsing timeout
```

---

## 📄 License
By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
