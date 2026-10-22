# Remarkable 2027 — design concept

A responsive landing-page design for Vector Institute, intended as a visual and front-end reference for a Swoogo build. It is a standalone static concept, not a connected registration site.

## Design system

- Official bilingual Vector mark and arrow geometry extracted from the supplied 2026 guidelines.
- Karbon Semibold headings and Open Sans body copy; official Karbon font files supplied in the user's prior materials.
- Magenta `#EB088A`, black, white, grey `#E9E8E8`, and cobalt `#313CFF`. All gradients run horizontally from magenta to cobalt.
- Rounded placed photographs, modest corner radii, clear type hierarchy, accessible native dialogs and disclosures, keyboard-operable day tabs and gallery, responsive navigation, reduced-motion support.
- Authentic 2026 conference photography extracted from the supplied recap. All historic statistics and photographs are explicitly labelled as 2026.

## Content status

February 18–19, 2027, Hilton Toronto, invitation-only in-person attendance, and the two-day outline are retained from the supplied draft mockups. These are draft details, not independently confirmed event information. The program is illustrative and labelled accordingly. No fictitious speakers from the old mockup are presented as confirmed; the 2027 lineup is marked to be announced. Funders are carried over from the supplied materials and should be confirmed for the 2027 launch.

Registration buttons open a clearly marked design-preview dialog. Replace those handlers with the actual Swoogo registration destinations for publication. The photo gallery uses still photographs, with no implied video playback. Contact links use the email from the supplied mockups.

## Front-end handoff

`dist/index.html` contains the semantic section markup, `dist/styles.css` the responsive styles, `dist/app.js` the lightweight interactions, and `dist/assets/` the reference-derived assets and fonts. No build step or external runtime library is required.

The page is organized into a header, masthead/hero, event details, introduction, 2026 statistics, program, speaker announcement, 2026 gallery, FAQ, final call to action, and funder/footer sections. Those sections can be adapted individually to the selected Swoogo theme. Asset URLs, theme selectors, font hosting, navigation links, language versions, final funders and privacy copy need to be configured for the production Swoogo event. This concept does not modify the existing Swoogo page.

## Sources

- Vector_BrandGuidelines_6.29.26(20261022-151239).pdf
- Vector Remarkable 2026 - Event Recap - Graphic Design Reference for 2027.pdf
- concept-a-home-desktop.png, concept-a-agenda-desktop.png, concept-a-speakers-desktop.png, concept-a-faq-desktop.png
