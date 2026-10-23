# Copy changes

Source: `Remarkable_2027_Current_Website_copy.docx`. The doc still holds the 2026 reg-site copy, so it was brought
into `copy.json` with only the edits needed to make it true for 2027 and to follow BRIEF.md §2 (no year-count or
anniversary wording). Everything else is verbatim.

| Where | Doc text | Mockup text | Why |
|---|---|---|---|
| Hero title | Remarkable 2026 | Remarkable 2027 | Event year |
| Hero date | `*/event-date/*` (Swoogo field) | February 18–19, 2027 | BRIEF.md §2 |
| Hero location | Downtown Toronto, Ontario, Canada | Hilton Toronto · 145 Richmond St W, Toronto, ON | BRIEF.md §2 venue |
| Intro ¶1 | **Now in its third year,** Vector Institute's Remarkable conference returns… | Vector Institute's Remarkable conference returns… | No year-count wording (BRIEF.md §2) |
| Intro ¶2 | **Building on two years of success,** Remarkable **2026** continues… | Remarkable 2027 continues… | No year-count wording; event year |
| Intro ¶3 | Remarkable **2026** offers a rare chance… | Remarkable 2027 offers… | Event year |
| Closer | …empowered at Remarkable **2026**! | …empowered at Remarkable 2027! | Event year |
| Invitation note | In-**P**erson attendance to this event… | In-person attendance to this event… | Capitalisation only |
| Agenda | Agenda: February 19 / 20, 2026 | Day 1 Thursday, February 18 / Day 2 Friday, February 19 | 2027 dates |
| Legal | Doc privacy paragraph | Doc privacy paragraph + the recording / English-only / produced-by sentences from the original handoff | Kept both |

Not from the doc (sources):
- Stats, recap heading, funders heading, day titles ("Research & keynotes", "From research to real-world impact"): original handoff `copy.json`.
- Footer "Questions about this event? Contact us at", "Find us on socials" and the Vector link list (Research … All Policies): the AI Summit 2026 Swoogo page.

## Written for the mockups (placeholders: replace before anything is shared externally)

| Where | What | Grounded in |
|---|---|---|
| Nav | EN / FR language switch | AI Summit 2026 Swoogo nav (Language: English / Français) |
| Home | "Remarkable 2026 in photos" carousel heading and "Highlights from last year’s conference" | New |
| Home | "View the full agenda", "See all speakers" links | New |
| Agenda page | Intro paragraph, every session (times, titles, descriptions, speakers, rooms), "Livestreamed" tags, placeholder note | Session topics reuse the 2026 themes from the original handoff (Agentic AI, LLMs & Inference, Privacy & Security); day structure from BRIEF.md §2. Times, rooms, sessions and all named people are fictitious |
| Speakers (Home and Speakers page) | Six fictitious speakers: names, titles, companies, bios, sessions | All invented. First names were changed on Oct 22, 2026 to match the gender shown in each stock portrait: Rowan → Hannah, Avery → Arjun, Morgan → David, Jordan → Mei, Sam → Marcus, Riley → Amara (also in the agenda's speaker lines). No 2027 speakers are confirmed. Company and university names are made up; check them against real organizations before anything leaves the team. Portraits are the requester's stock headshots (`assets/speakers/stock-headshot-01…06.jpg`, Oct 22, 2026); the earlier 2026 headshots of real people were removed |
| Speakers page | Intro, "More speakers to be announced soon!" | Last line follows the AI Summit page; the rest is new |
| Home and Speakers page | "portraits are temporary" → "portraits are stock images" (speakers note and Speakers-page intro) | Stock headshots replaced the temporary 2026 portraits |
| Concept A hero and banner | Alt text "Vector Institute 10th anniversary mark: 10 Years \| Ans" (`hero.anniversary_mark`) | Describes the agency's mark; no anniversary wording added to the page copy |
| FAQ page | All questions and answers | Facts reused from BRIEF.md §2 and the legal copy (invitation-only, public livestream, Hilton address, recorded, English only, privacy paragraph). Process details (confirmation-email link, viewing details by email), the Osgoode station directions and the accessibility answer are placeholders to confirm |


## Concept E — In motion (October 22, 2026)

All public-facing event copy, speaker profiles, session details, page titles, navigation labels and footer copy are unchanged from Concept D. The private `_note` metadata now correctly says that portraits are the supplied stock headshots. Added `ui` strings for accessible navigation, a skip link and placeholder tooltips. No marketing copy was added. The new visual composition retains Home → intro → stats → days → speakers → recap → nine-photo gallery → funders → footer, plus the separate Agenda, Speakers and FAQ pages.

## Refined design — October 22, 2026

No event copy or JSON data changed. The revision simplifies the visual hierarchy, navigation, hero, content grids, agenda, portraits, gallery and footer. Added UI-only preview/status labels and offline content support.

## Bold Vector — October 22, 2026

Event JSON is unchanged. The new direction uses a full-width cobalt hero, oversized official arrow, magenta day panels, larger portraits and featured-session cards. Added only UI labels Featured sessions and Full program; featured cards reuse existing session copy and link to its details.

## Split-screen refinement — October 22, 2026

Event JSON and all event wording are unchanged. This design-only revision aligns opening arrow tips to the section top, introduces a diagonal photo/arrow hero split, reduces the speaker announcement to a small text line, references the recap brochure’s muted magenta–violet gradient and adds sparse official pixel accents. Mobile hero actions move below the split without changing their labels or invitation text.

## Karbon and pixels refinement — October 22, 2026

Per the requester, removed visible internal-preview, fictitious-speaker, sample-program and video-source notes. The speaker page intro retains its first sentence. The video accessible label is now “Remarkable 2026 recap video”; destination tooltips are removed and portrait alt text uses speaker names. Only `speakers_note`, `speakers_page.intro`, `agenda_page.note` and `ui.video_placeholder` change in JSON. All event descriptions, session content, speaker profiles and logistics remain unchanged. Content status is retained in the handoff.

## Rounded panels — October 23, 2026

Design-only revision. Event JSON and all event wording are unchanged. Added UI-only labels: “Topics” above the FAQ topic list. The date and venue now appear as pills inside the opening panels rather than in a strip below the hero.

## Arrow seam — October 23, 2026

Design-only revision. Event JSON and all event wording are unchanged. Inner-page banner photos are decorative and carry empty alternative text.
