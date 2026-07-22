# OPALX Documents

This repository stores presentations, reports, archived examples, datasets,
and other supporting files that do not belong in the text-first OPALX manual.
The manual links to these files through a configurable repository base URL.

## Layout

Documents are grouped first by purpose, then by creation year:

```text
presentations/YYYY/{features,bugs,project-updates}/
reports/YYYY/{design,investigations}/
meetings/YYYY/
tutorials/YYYY/
examples/YYYY/
datasets/YYYY/
```

Use `<category>/undated/` only when the creation year cannot be established.
Exact dates use a `YYYY-MM-DD-` filename prefix. Month-only and year-only
prefixes are allowed when that is all the source material establishes.

This repository is exclusively for OPALX material. Historical OPAL documents
remain with the separate OPAL documentation and must not be copied here.

## Adding a document

1. Put the file in the appropriate category, year, and topic directory.
2. Use a lowercase, descriptive filename without spaces.
3. Add its provenance and SHA-256 digest to `manifest.yml`.
4. Run `ruby scripts/validate_repository.rb`.
5. Confirm that Git LFS tracks the file before committing it.

The repository deliberately has no generated website, Doxygen output, LaTeX
auxiliary files, or generated archives of documentation sites.
