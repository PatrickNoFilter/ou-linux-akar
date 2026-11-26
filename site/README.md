# OU Linux website

Static site for OU Linux (Orang Utan Distro), Akar Alpha series. Designed for
Cloudflare Pages; it also opens directly from disk.

## Files

- `index.html` — page structure
- `styles.css` — all styling
- `app.js` — populates release details and download links
- `site.config.js` — **the only file you edit for a new release**
- `assets/` — optimized WebP versions of the logo, mascot, desktop screenshot and artwork

## Publish a new ISO

1. Upload the ISO to a host that allows multi-gigabyte files (Cloudflare R2,
   Altare U3, SourceForge, Archive.org). GitHub cannot host this file: 100 MB
   limit in Git, 2 GB limit per release asset.
2. Edit `site.config.js`:
   - `version`, `release`, `file`, `sizeBytes`, `sha256` for the new image
   - add each public download URL to `mirrors`, e.g.
     ```js
     mirrors: [
       { name: "Primary", url: "https://host/OU-OS-Akar-Alpha-v36.iso", note: "Direct download" }
     ]
     ```
3. Verify locally, then commit. With no mirror configured the page deliberately
   shows "ISO link not published yet" instead of a broken button.

Compute the checksum with: `sha256sum OU-OS-Akar-Alpha-v36.iso`

## Deploy to Cloudflare Pages

Option A — connected to GitHub (recommended):

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git** → select `PatrickNoFilter/ou-linux-akar`.
2. Build settings:
   - Framework preset: **None**
   - Build command: *(leave empty)*
   - Build output directory: `site`
   - Root directory: *(leave as default / repository root)*
3. Deploy. Every push to `main` then republishes the site automatically.
4. Add a custom domain under the project's **Custom domains** tab if you own one;
   otherwise use the free `*.pages.dev` URL.

Option B — direct upload (no Git connection):

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Upload assets** → drag in the contents of the `site/` folder (not the folder itself).
2. Set the project name, e.g. `ou-linux`.

## Verify after deploy

- Site loads over HTTPS and all images appear.
- The download button points at the real ISO URL; confirm with
  `curl -I -L <url>` (expect `200` or `206` and a `Content-Length` near 3 GB).
- `sha256sum` of the downloaded image matches the checksum shown on the page.
