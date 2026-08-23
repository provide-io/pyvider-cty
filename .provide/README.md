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

## `foundry/` is not tracked, and is provisioned rather than committed

`.provide/foundry/` is gitignored (`.gitignore:71`) and holds documentation
scaffolding whose home is the `provide-foundry` package — `base-mkdocs.yml`,
`gen_ref_pages.py`, and a theme tree. `mkdocs.yml` opens with
`INHERIT: .provide/foundry/base-mkdocs.yml`.

Run `make docs-scaffold` to put it there, or `make docs-build` to do that and
build. Both pull `provide-foundry` from the `docs` dependency group and call the
`extract_base_mkdocs` helper it ships for exactly this.

It used to be neither tracked nor provisioned: nothing in this repository put it
there, so `mkdocs build` worked only where some other tool had already vendored
it and failed from a clean clone. No CI job built the documentation either, and
`make check-docs` executes the code blocks in `docs/` without reading
`mkdocs.yml` at all, so the docs gate stayed green while the build was broken.
The `📚 Docs build` job now builds it strictly on a fresh checkout, which is the
case that was failing.
