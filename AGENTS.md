# Diburim Content Integrity Rules

Diburim is the Torah library of Rabbi Binyamin Goldberg.

## Critical content rule

NEVER invent, extrapolate, paraphrase, summarize, or fabricate Torah content, biographical information, project descriptions, Hebrew quotations, sources, article titles, article summaries, dates, teachings, or claims attributed to Rabbi Binyamin Goldberg.

The coding agent is responsible for **implementation**, not **authorship**.

If required content has not been supplied:

1. Leave the field empty, OR
2. Use an explicitly marked development placeholder from `data/ui.json`, OR
3. Render the component only when content exists.

Never create realistic filler content.

## Layer separation

| Layer | Location | Agent may edit |
| --- | --- | --- |
| Design | HTML structure, CSS, JS renderers | Yes |
| Site configuration | `data/site.json`, `data/ui.json`, `data/navigation.json`, `data/projects.json` (labels/URLs only) | Only when explicitly instructed |
| Torah content | `content/articles/*`, approved metadata in `data/catalog.json` | **Never** unless user supplied the text |

## Hebrew

Never generate Hebrew quotations merely to fill a design.

Hebrew displayed as Torah or source text must come from supplied content or an explicitly verified source.

Do not generate Divine Names for decorative or placeholder use.

Do not place complete pesukim into decorative imagery or placeholder content unless explicitly supplied and approved.

## Existing content

Do not rewrite approved text for style, length, SEO, or layout unless explicitly instructed.

Truncation for a visual excerpt must be programmatic and must not rewrite the source text.

## Metadata

Do not invent:

- article descriptions
- SEO descriptions
- summaries
- keywords
- reading times (unless computed from supplied body text)
- dates
- source references
- Hebrew titles
- project status prose
- author biography

Derive metadata only from approved source files where possible.

## Development placeholders

When a UI requires content that does not yet exist, use strings from `data/ui.json`, for example:

- `[CONTENT PENDING]`
- `Audio not available`

Do not create convincing substitute content.

## Principle

**Missing content is acceptable. Invented content is not.**

The coding agent builds the publishing system. It does not author Rabbi Goldberg's Torah.
