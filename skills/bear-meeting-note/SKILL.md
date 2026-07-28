---
name: bear-meeting-note
description: Create standardized Bear meeting notes with consistent title format, tags, attendees, and Next Steps while using meeting-specific section headers.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Bear, meetings, notes, MCP]
---

# Bear meeting note

Use this when the user wants a meeting note created in Bear with a consistent format.

## When to use
- The user asks to create a meeting note in Bear
- The note should follow the user's standard meeting-note structure
- Bear MCP tools are available

## Required defaults
- Always tag meeting notes with `work/+areas/meetings`
- Use title format:
  `Mon DD, YYYY | Meeting Title`
- Repeat the title as the first markdown heading
- Include an attendees line near the top
- Add a horizontal rule after attendees
- Include a `## Next Steps` section
- Use meeting-specific `##` section headings for the main body content

## Tag rules
- Always include:
  - `work/+areas/meetings`
- Add `work/+areas/granola` only when one of the following is true:
  - the user explicitly requests it
  - another agent explicitly indicates it
  - the user indicates the notes are from Granola
- Add any additional tags only if the user explicitly requests them

## Attendees rules
- If attendees are provided, list them in the attendees line
- If attendees are unknown, default to:
  `**Attendees:** Michael Danko`

## Next Step Rules
- If it's clear who is responsible for a next-step item, list their first name before displaying the item.
  - For example, `- Michael: Will follow up with City of Charlotte on what they need from us`
- If it's unclear who should be responsible for next steps, list `TBD: ` before displaying the item.
  - For example, `-TBD: Send client an email`


## Preferred note template

```markdown
# Mon DD, YYYY | Meeting Title
#work/+areas/meetings [#work/+areas/granola]

**Attendees:** Michael Danko, Name 2, Name 3

---

## Meeting-Specific Topic One
- Bullet
- Bullet

## Meeting-Specific Topic Two
- Bullet
- Bullet

## Next Steps
- Owner: action item
- Owner: action item
```

## Template rules
- Standardize only these structural elements:
  - title format
  - tags
  - attendees
  - `## Next Steps`
- Use meeting-specific section headers for the main content instead of forcing generic headings
- Omit empty sections rather than leaving placeholders
- If there are no clear action items, still include `## Next Steps` with concise bullets describing follow-up, open questions, or `- None yet` if necessary

## Body generation guidance
- Choose section headers that reflect the actual subject of the meeting
- Prefer specific headers such as:
  - `## Dashboard Tile Design for Payments`
  - `## Payment Status and Timing Challenges`
  - `## System Architecture Overview`
  - `## Reporting Requirements`
- Avoid overly generic headers when a more precise topic is clear

## Bear MCP creation guidance
When creating the note:
1. Build the title using the meeting date and meeting title
2. Build the markdown body using the preferred template and rules above
3. Apply tags including `work/+areas/meetings`
4. Add `work/+areas/granola` only when explicitly indicated or when the notes are from Granola
5. Use the Bear MCP create-note tool

## Output expectation
After creating the note, confirm:
- note title
- tags applied
- whether the note was successfully created in Bear
