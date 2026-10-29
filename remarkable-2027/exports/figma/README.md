# Remarkable 2027: Figma import files

Eight single-page vector PDFs, one per page and view, at the real layout size:

- Desktop: 1440 px wide (home, agenda, speakers, faq)
- Mobile: 390 px wide (home, agenda, speakers, faq)

## Importing into Figma

1. Install the Karbon fonts (Regular, Medium, Semibold, Bold) on your computer first, so Figma can match the
   text layers. In the Figma desktop app they're picked up automatically; in the browser, install Figma's
   font installer.
2. In a Figma Design file, drag all eight PDFs onto the canvas, or use **File → Place image/video** / the
   import option for PDFs. Each PDF becomes a frame.
3. Text arrives as editable text layers; logos, plus symbols and dividers as vectors; photos, the glass
   panels and blended artwork as image fills.

## What does not carry over

These are static frames: no auto layout, components, variables or interactions (menus, accordions,
dialogs, agenda tabs). The interactive preview remains the reference for behaviour. A PDF import also
groups layers by drawing order rather than by section, so expect to rename and regroup layers if the
frames will be edited heavily.

## Regenerating

From the project, with the local server running (`python3 -m http.server 8765 --directory Source/dist`),
the PDFs are printed by Chromium (Playwright `page.pdf`, screen media, backgrounds on, one page per frame
sized to the full page height).
