# Security Policy

## Supported Versions

The following versions of pyvider-cty are currently supported with security updates:

| Version   | Supported          | Status |
| --------- | ------------------ | ------ |
| 0.0.x     | :white_check_mark: | Alpha  |

**Note:** As this project is in Alpha status, security updates will be provided on a best-effort basis. Once the project reaches Beta or stable release (1.0.0+), a formal security update policy will be established.

## Security Status

### Current Security Measures

✅ **Static Analysis**
- Bandit security scanner (clean scan - 0 issues in 5,426 lines)
- Strict type checking with mypy and ty
- Comprehensive linting with ruff

✅ **Dependency Management**
- Lockfile-based dependency pinning (uv.lock)
- Minimal dependency surface (attrs, msgpack, provide-foundation)
- Python ≥ 3.11 (modern, maintained versions)

✅ **Code Quality**
- 94% test coverage
- Immutable value semantics
- Comprehensive error handling with error boundaries

✅ **CI/CD Security**
- Automated security scanning in CI pipeline
- Code quality gates before merge
- Protected main branch

### Security Considerations

**Serialization Safety**
- MessagePack deserialization uses strict settings
- No arbitrary code execution in codec
- Type validation on all deserialized data

**Input Validation**
- All user inputs validated through type system
- Path traversal protection in path navigation
- String normalization (Unicode NFC) prevents normalization attacks

**Error Handling**
- Structured error contexts avoid information leakage
- Error messages sanitized (values truncated)
- No stack traces in production error messages

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in pyvider-cty, please report it responsibly.

### Reporting Process

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security issues via:

1. **Email**: Send details to **[code@provide.io](mailto:code@provide.io)**
   - Subject: `[SECURITY] pyvider-cty: Brief Description`
   - Include detailed reproduction steps
   - Attach proof-of-concept if applicable

2. **Private Security Advisory**: Use GitHub's [private vulnerability reporting](https://github.com/provide-io/pyvider-cty/security/advisories/new)

### What to Include

Please include the following in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact and attack scenarios
- Affected versions
- Suggested mitigation or fix (if available)
- Your name/handle for acknowledgment (optional)

### Response Timeline

| Stage | Timeline | Description |
|-------|----------|-------------|
| **Acknowledgment** | 48 hours | We'll confirm receipt of your report |
| **Initial Assessment** | 7 days | We'll evaluate severity and impact |
| **Fix Development** | 30 days | We'll develop and test a fix |
| **Disclosure** | 90 days | We'll coordinate public disclosure |

**Note:** Timelines may vary based on vulnerability complexity and severity.

### Disclosure Policy

- We follow **coordinated vulnerability disclosure**
- We will work with you to understand and address the issue
- We will credit you in the security advisory (unless you prefer to remain anonymous)
- We ask that you give us reasonable time to fix the issue before public disclosure

## Security Best Practices for Users

### For Production Use

1. **Pin Dependencies**
   ```toml
   pyvider-cty = "==0.0.1000"  # Pin exact version
   ```

2. **Validate Input Data**
   ```python
   # Always validate untrusted data
   try:
       value = cty_type.validate(untrusted_input)
   except CtyValidationError as e:
       # Handle validation failure
       logger.error(f"Validation failed: {e}")
   ```

3. **Use Error Boundaries**
   ```python
   from provide.foundation.errors import error_boundary

   with error_boundary(context={"source": "user_input"}):
       result = process_cty_value(data)
   ```

4. **Limit Deserialization**
   ```python
   # Only deserialize from trusted sources
   if is_trusted_source(source):
       value = cty_from_msgpack(data, expected_type)
   ```

### For Development

1. **Keep Dependencies Updated**
   ```bash
   uv lock --upgrade-package pyvider-cty
   ```

2. **Run Security Scans**
   ```bash
   bandit -r src/
   pip-audit  # Check for known vulnerabilities
   ```

3. **Enable All Type Checking**
   ```bash
   mypy --strict src/
   ty check src/
   ```

## Known Limitations

### Alpha Status Limitations

As an Alpha release, please be aware:

- **API Stability**: API may change between versions
- **Production Use**: Not recommended for critical production systems yet
- **Security Audits**: No formal third-party security audit has been conducted
- **Cryptography**: This library does not implement cryptography; use dedicated crypto libraries

### Not a Security Boundary

pyvider-cty is a data type system and serialization library. It is **not designed** to:

- ❌ Protect against malicious code execution (use sandboxing)
- ❌ Provide cryptographic guarantees (use crypto libraries)
- ❌ Enforce access control (implement at application level)
- ❌ Protect against DoS attacks (implement rate limiting)

## Security Roadmap

### Planned Improvements

- [ ] Third-party security audit (planned for 1.0.0)
- [ ] Automated dependency vulnerability scanning (Dependabot)
- [ ] Fuzzing integration (hypothesis property-based testing expansion)
- [ ] Security-focused test scenarios
- [ ] CVE monitoring and notifications
- [ ] Security section in release notes

## Acknowledgments

We thank the security research community for responsible disclosure and helping keep pyvider-cty secure.

### Security Researchers

(This section will list security researchers who have responsibly disclosed vulnerabilities)

## Contact

For security-related questions or concerns:
- Email: code@provide.io
- Security Advisory: https://github.com/provide-io/pyvider-cty/security/advisories

For general questions, please use GitHub Issues or Discussions.

---

Last Updated: 2025-10-24
