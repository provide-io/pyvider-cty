# Documentation Restructuring Plan for pyvider-cty

## Executive Summary

This document tracks the complete restructuring of pyvider-cty documentation to align with provide.io ecosystem patterns established in provide-foundation, pyvider, and flavorpack projects.

**Start Date:** 2025-01-24
**Status:** 🔴 Not Started
**Target Completion:** TBD

---

## 📋 Current State Assessment

### Issues Identified

#### 🔴 Critical Issues (Must Fix)
- [ ] **Python Version Mismatch**: Docs claim "Python 3.13+ Required" but `pyproject.toml` specifies `>=3.11`
- [ ] **Wrong Property Name**: Documentation uses `.value` but actual property is `.raw_value`
- [ ] **Missing Functions**: Docs reference `to_json`/`from_json` which don't exist
- [ ] **Duplicate Files**: Two ch15 files exist (`ch15_api_reference.md` and `ch15_terraform_interop.md`)

#### 🟡 Structural Issues
- [ ] **Incomplete Navigation**: mkdocs.yml only has Home + API Reference
- [ ] **Missing Chapter**: ch13_path_navigation.md not in index
- [ ] **Wrong Links**: Index.md has incorrect chapter links
- [ ] **No Getting Started Section**: Mixed with chapter content

#### 🟢 Documentation Gaps
- [ ] **Stale Release Doc**: release_readiness.md claims mypy errors that don't exist
- [ ] **No How-To Guides**: Missing practical task-oriented guides
- [ ] **No Troubleshooting**: Missing dedicated troubleshooting section
- [ ] **Limited Examples Organization**: Examples use old chapter numbering

---

## 🎯 Target Structure

### Directory Layout
```
docs/
├── index.md                    # Home page
├── getting-started/            # New section
├── user-guide/                 # Renamed from guide/
│   ├── core-concepts/
│   ├── type-reference/
│   └── advanced/
├── how-to/                     # New section
├── api/                        # Existing, reorganized
└── reference/                  # New section
```

---

## ✅ Implementation Checklist

### Phase 1: Preparation
- [ ] Create backup of current docs structure
- [ ] Set up tracking branches in git
- [ ] Review all existing documentation for accuracy

### Phase 2: Fix Critical Issues

#### Fix Python Version Requirements
- [ ] Update README.md line 75: Change "Python 3.13+" to "Python 3.11+"
- [ ] Update docs/guide/ch01_welcome.md line 17: Change "Python 3.13+" to "Python 3.11+"
- [ ] Verify all other Python version references

#### Fix Property Names
- [ ] Update docs/guide/ch02_getting_started.md: Replace `.value` with `.raw_value`
  - [ ] Line 84: `person_value['name'].value` → `person_value['name'].raw_value`
  - [ ] Line 85: `person_value['age'].value` → `person_value['age'].raw_value`
  - [ ] Line 90: `tag_value.value` → `tag_value.raw_value`
- [ ] Update ALL documentation files with correct property name
- [ ] Update example files to use `.raw_value`

#### Handle Missing Functions
- [ ] Decision: Implement `to_json`/`from_json` OR update docs to use msgpack
- [ ] If implementing JSON:
  - [ ] Add to_json function to codec.py
  - [ ] Add from_json function to codec.py
  - [ ] Add tests for JSON serialization
  - [ ] Export in __init__.py
- [ ] If using msgpack only:
  - [ ] Update ch02_getting_started.md to use msgpack functions
  - [ ] Update all examples to use msgpack

#### Remove Duplicate Files
- [ ] Delete docs/guide/ch15_terraform_interop.md (duplicate)
- [ ] Keep docs/guide/ch14_terraform_interop.md as the canonical version

### Phase 3: Create New Structure

#### Create Directory Structure
- [ ] Create `docs/getting-started/` directory
- [ ] Create `docs/user-guide/` directory
  - [ ] Create `docs/user-guide/core-concepts/`
  - [ ] Create `docs/user-guide/type-reference/`
  - [ ] Create `docs/user-guide/advanced/`
- [ ] Create `docs/how-to/` directory
- [ ] Create `docs/reference/` directory
- [ ] Create `examples/getting-started/` directory
- [ ] Create `examples/core-concepts/` directory
- [ ] Create `examples/types/` directory
- [ ] Create `examples/advanced/` directory

#### Move and Rename Files

##### Getting Started Section
- [ ] Split ch02_getting_started.md into:
  - [ ] `docs/getting-started/installation.md`
  - [ ] `docs/getting-started/quick-start.md`
  - [ ] `docs/getting-started/first-type-system.md`

##### User Guide Section
- [ ] Move ch03 → `user-guide/core-concepts/types.md`
- [ ] Move ch04 → `user-guide/core-concepts/values.md`
- [ ] Move ch05 → `user-guide/type-reference/primitives.md`
- [ ] Move ch06 → `user-guide/type-reference/collections.md`
- [ ] Move ch07 → `user-guide/type-reference/structural.md`
- [ ] Move ch08 → `user-guide/type-reference/dynamic.md`
- [ ] Move ch09 → `user-guide/type-reference/capsule.md`
- [ ] Move ch10 → `user-guide/advanced/marks.md`
- [ ] Move ch11 → `user-guide/advanced/functions.md`
- [ ] Move ch12 → `user-guide/advanced/serialization.md`
- [ ] Move ch13 → `user-guide/advanced/path-navigation.md`
- [ ] Move ch14 → `user-guide/advanced/terraform-interop.md`

##### Reference Section
- [ ] Move ch16 → `reference/troubleshooting.md`
- [ ] Move ch17 → `reference/glossary.md`
- [ ] Move ch18 → `reference/go-cty-comparison.md`
- [ ] Move release_readiness.md → `reference/release-notes.md`

##### API Section
- [ ] Consolidate `api/types/*.md` into `api/types.md`
- [ ] Keep other API files in place

##### Examples Reorganization
- [ ] Move example files to match new structure:
  - [ ] ch02_getting_started.py → `getting-started/quick-start.py`
  - [ ] ch05_primitive_types.py → `types/primitives.py`
  - [ ] ch06_collection_types.py → `types/collections.py`
  - [ ] ch07_structural_types.py → `types/structural.py`
  - [ ] ch08_dynamic_types.py → `types/dynamic.py`
  - [ ] ch09_capsule_types.py → `types/capsule.py`
  - [ ] ch10_marks.py → `advanced/marks.py`
  - [ ] ch11_functions.py → `advanced/functions.py`
  - [ ] ch12_serialization.py → `advanced/serialization.py`
  - [ ] ch13_path_navigation.py → `advanced/path-navigation.py`
  - [ ] ch15_terraform_interop.py → `advanced/terraform-interop.py`

### Phase 4: Create New Content

#### Index Pages
- [ ] Create `docs/index.md` (enhanced home page)
- [ ] Create `docs/getting-started/index.md`
- [ ] Create `docs/user-guide/index.md`
- [ ] Create `docs/how-to/index.md`
- [ ] Create `docs/getting-started/examples.md`

#### Core Concepts (Extract from existing)
- [ ] Create `docs/user-guide/core-concepts/validation.md`
- [ ] Create `docs/user-guide/core-concepts/conversion.md`

#### How-To Guides (New)
- [ ] Create `docs/how-to/validate-data.md`
- [ ] Create `docs/how-to/serialize-values.md`
- [ ] Create `docs/how-to/work-with-terraform.md`
- [ ] Create `docs/how-to/create-custom-types.md`
- [ ] Create `docs/how-to/migrate-from-go-cty.md`

### Phase 5: Update Configuration

#### Update mkdocs.yml
- [ ] Add complete navigation structure
- [ ] Configure plugins (mkdocstrings, search, etc.)
- [ ] Set up Material theme features
- [ ] Add social links and repo info

#### Update Cross-References
- [ ] Fix all internal documentation links
- [ ] Update example references
- [ ] Update API documentation links
- [ ] Update README.md links

### Phase 6: Content Updates

#### Update Release Documentation
- [ ] Update release_readiness.md with current status
- [ ] Note that mypy passes with no errors
- [ ] Update test coverage percentage
- [ ] Remove outdated information

#### Simplify README.md
- [ ] Remove detailed examples (link to docs)
- [ ] Keep only installation and quick example
- [ ] Add clear links to documentation sections
- [ ] Remove "# CI Test" comment

### Phase 7: Testing and Validation

#### Documentation Testing
- [ ] Build docs locally with mkdocs serve
- [ ] Test all navigation links
- [ ] Verify all code examples run
- [ ] Check for broken cross-references
- [ ] Validate mkdocs.yml configuration

#### Example Testing
- [ ] Run all example files
- [ ] Verify examples match documentation
- [ ] Test run_all_examples.py script
- [ ] Ensure examples use correct imports

#### Content Review
- [ ] Review all fixes for accuracy
- [ ] Ensure consistency in terminology
- [ ] Check for any remaining `.value` references
- [ ] Verify Python version requirements

### Phase 8: Finalization

#### Final Checks
- [ ] Run spell check on all documentation
- [ ] Verify all TODOs are addressed
- [ ] Ensure all checklist items complete
- [ ] Create PR for review

#### Post-Implementation
- [ ] Update this tracking document with completion status
- [ ] Document any deviations from plan
- [ ] Note any follow-up items needed
- [ ] Archive old documentation structure

---

## 📊 Progress Tracking

| Phase | Status | Progress | Notes |
|-------|--------|----------|-------|
| Phase 1: Preparation | 🔴 Not Started | 0% | |
| Phase 2: Fix Critical Issues | 🔴 Not Started | 0% | |
| Phase 3: Create New Structure | 🔴 Not Started | 0% | |
| Phase 4: Create New Content | 🔴 Not Started | 0% | |
| Phase 5: Update Configuration | 🔴 Not Started | 0% | |
| Phase 6: Content Updates | 🔴 Not Started | 0% | |
| Phase 7: Testing | 🔴 Not Started | 0% | |
| Phase 8: Finalization | 🔴 Not Started | 0% | |

**Overall Progress:** 0/70 tasks (0%)

---

## 🎖️ Success Criteria

### Documentation Quality
- ✅ All critical issues fixed (Python version, property names, functions)
- ✅ No broken links or missing references
- ✅ All code examples are executable
- ✅ Consistent terminology throughout

### Structure Alignment
- ✅ Matches provide.io ecosystem patterns
- ✅ Clear information architecture (Getting Started → Guide → How-To → Reference)
- ✅ Logical navigation structure in mkdocs.yml
- ✅ Examples organized by topic

### User Experience
- ✅ Easy to find information
- ✅ Progressive disclosure (simple → complex)
- ✅ Task-oriented guides available
- ✅ Clear learning path for new users

---

## 📝 Notes and Decisions

### Key Decisions Needed
1. **JSON Serialization**: Implement `to_json`/`from_json` or document msgpack-only approach?
2. **API Documentation**: Use mkdocstrings for auto-generation?
3. **Theme Assets**: Include .shared-theme from provide.io?

### Deviations from Original Plan
- (To be documented during implementation)

### Follow-up Items
- (To be documented during implementation)

---

## 🔗 Related Documents
- Original Documentation: `docs/guide/`
- mkdocs.yml: Project documentation configuration
- README.md: Project overview
- CONTRIBUTING.md: Contribution guidelines

---

## 📅 Timeline

- **Documentation Review Completed:** 2025-01-24
- **Implementation Start:** TBD
- **Target Completion:** TBD
- **Actual Completion:** TBD

---

*Last Updated: 2025-01-24*