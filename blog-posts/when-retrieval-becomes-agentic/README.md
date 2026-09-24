# When retrieval becomes agentic: WordPress post

This folder has the WordPress block markup for the post. It follows the layout of the earlier "Enhancing RAG with Knowledge Graphs" post: an H1, a large-type standfirst, the byline, a Contents list with jump links, H2 sections with a rule under each, centred small italic captions, and a numbered reference list with anchors.

| File | Use it when |
|---|---|
| `wordpress-interactive.html` | You can host the figure files (`.html` / `.svg`) somewhere public. Figures 1, 2, 3 and 6 are interactive iframes, and Figures 4 and 5 are animated SVGs. |
| `wordpress-static.html` | You can only use the Media Library. All six figures are PNG images. |

Both files passed Gutenberg's own block validator (`@wordpress/block-library` 11.1) with 0 invalid blocks. When you paste either one, no block should show "This block contains unexpected or invalid content".

## Publishing steps

1. **Host the figure assets.** In the author's bundle, upload the `assets/` folder so each figure keeps its path, for example `…/assets/fig-01/fig-01-two-circle-model.html`. The earlier post served its iframe and SVG files from `vectorinstitute.github.io/kg-rag/…`, so the same GitHub Pages setup (or the CloudFront bucket) works here. WordPress won't accept `.html` uploads, and it only accepts `.svg` with an SVG plugin.
2. **Point the markup at them.** Both files use the placeholder `https://ASSET-HOST.example/when-retrieval-becomes-agentic/assets`. Find and replace it with the real base URL. It appears once per figure.
   - Static version with the Media Library: upload the six `fig-0N-*.png` files. Then replace each image URL with its Media Library URL, or delete each image block and re-insert the image from the library so WordPress adds responsive `srcset` sizes.
3. **Create the post.** Open the editor, choose ⋮ → *Code editor*, paste the whole file and switch back to the visual editor.
4. **Featured image:** `assets/header/hero@1600x686.png`. It's 21:9, the crop the theme uses, and the headline is already in the image.
   - If the theme also prints the post title, the title shows up twice, because the first block is an H1 (as in the older post). Either delete that H1 block, or use `assets/header/poster.png` as the featured image. That version has no headline and survives the 21:9 crop.
   - The animated banner (`header/header.html`) can't be a featured image. It could go in as an iframe at the top of the content, but I haven't included it.
5. **Category:** AI Engineering.
6. **Preview on a phone as well as a desktop** before publishing (see the figure notes below).

## How the interactive figures size themselves

Each interactive figure reports its own height to the page. The Custom HTML block just above Figure 1 contains a short `<script>` that receives those reports and resizes each iframe to fit. **Keep that block.** Without it the figures stay at a fixed height. On a phone, Figure 3 needs about 1,200px and would be cut off.

- I checked the sizing in a headless browser at 1280px and 390px wide. The measured heights were Figure 1: 647 / 291px, Figure 2: 603 / 399px, Figure 3: 487 / 1221px and Figure 6: 677 / 296px.
- Figure 6 measures itself in a way that can only make the frame taller, never shorter. So its frame starts at a 16:10 ratio, just below its real height, and grows to fit.
- WordPress keeps `<script>` and `<iframe>` in Custom HTML blocks only for users with the `unfiltered_html` capability, which administrators and editors on a single site have. The older post already used iframes, so this should work. If the script gets stripped when you save, the figures still show, but with fixed heights.

## Editorial choices to confirm

- **Standfirst:** the manuscript has no subtitle. I used its first paragraph, unchanged, as the large-type standfirst.
- **"Introduction" heading:** added so the Contents list has a first entry, as in the older post. It covers paragraphs 2–3 of the manuscript.
- **Byline:** "By Ali Kore, Mahshid Alinoori, and Shayaan Mehdi, Vector Institute", in the older post's style. I dropped the manuscript's "Draft · … · AI Engineering" line because the status and the category belong in WordPress.
- **Citations** `[1]`–`[5]` are superscript links to the reference list, in the older post's style. The references use the older post's format: authors, *italic title*, year, arXiv ID and link.
- The bold lead-ins in sections 1 and 5 and the monospace `triggers` / `related_to` match the manuscript.

## Discrepancies in the bundle (for the author)

1. **Figure 4 caption:** the manuscript says "…whatever edges the extractor **draws**". The preview says "**drew**". I used the manuscript's wording.
2. **The manuscript is a `.docx`, not a markdown file.** Its figure placeholders are "All formats for Figure N" links to Google Drive folders, not paths into `assets/`.
3. **Figures 4 and 5 are PNGs in the preview**, even in Interactive mode. The bundle also has animated SVGs for them, and the interactive version here uses the SVGs. They are CSS-only and respect reduced-motion settings. If the author meant the stills, swap `.svg` for `.png` in those two image blocks.
4. **Figure 3 doesn't use the prose's terms.** The figure's rows and columns are flat / cross-referenced / entity-dense and single-fact / multi-hop / corpus-wide synthesis. The prose uses loose → dense and local / multi-hop / global / path queries, so path queries appear in the text but not in the figure. One cell also cites a "LinkedIn ticket KG" that isn't in the references.
5. **Text in Figures 4 and 5 is very small on phones,** because they are drawn at 1200px wide. This is the same with the PNGs.
