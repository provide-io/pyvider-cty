# `.provide/`

Working documents that belong to the repository but not to the published
documentation. Tracked in git, deliberately: several are referenced from
`CONTRIBUTING.md`, `AGENTS.md`, the changelog and at least one test, so they are
part of how this project is worked on rather than scratch notes.

| File | What it is |
|---|---|
| `GO-CTY-PARITY.md` | The parity tracker. A living document — the baseline commit, what each review round found, and what is actually left. Referenced from `CONTRIBUTING.md` and `AGENTS.md`. **Update it as work lands**; it has gone stale before and said so about itself. |
| `HANDOFF.md` | State at the end of a working session: what was asked, what changed, why, and a checklist for whoever picks it up next. |
| `ADVERSARIAL-REVIEW-PROMPT.md` | The prompt used to drive adversarial review rounds against this tree. |
| `UPSTREAM-GO-CTY-EQUALS-NONDETERMINISM.md` | A drafted upstream issue against go-cty, kept here until it is filed. |

## `foundry/` is not tracked, and `mkdocs.yml` depends on it

`.provide/foundry/` is gitignored (`.gitignore:71`) and holds shared
documentation scaffolding vendored from the sibling `provide-foundry`
repository — `base-mkdocs.yml`, `gen_ref_pages.py`, and a `docs/` tree.

`mkdocs.yml` opens with `INHERIT: .provide/foundry/base-mkdocs.yml`, so
**`mkdocs build` does not work from a fresh clone**: the inherited file is not
in the repository and nothing fetches it. No CI job builds the documentation
either, so nothing catches this — `make check-docs` executes the code blocks in
`docs/` and does not read `mkdocs.yml` at all.

Until that is resolved, building the docs locally needs `provide-foundry`
checked out beside this repository and its scaffolding present at
`.provide/foundry/`. The two candidate fixes are to track the inherited file
here, or to have a `make` target provision it from the sibling repository so a
clean checkout can build; either wants a CI job that actually runs
`mkdocs build --strict`, since an unbuilt documentation set is an unverified
one.
