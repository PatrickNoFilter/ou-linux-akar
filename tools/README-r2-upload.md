# Hosting the OU Linux ISO on Cloudflare R2

The ISO is 2.83 GiB — too large for Git, GitHub Releases (2 GB asset cap), and
Cloudflare Workers request bodies (100 MB). **Do not build a Worker upload API**;
it cannot accept this file. The right API is R2's S3-compatible object API.

R2's free tier includes 10 GB-month of storage and no egress fees, so one ISO
fits and downloads cost nothing.

## What I need you to create (in your browser, ~3 minutes)

I can't do this part: the Cloudflare dashboard blocks automation from this
machine, and credentials must never be pasted into chat.

1. **Create the bucket** — Cloudflare dashboard → **R2** → **Create bucket** →
   name it `ou-linux-iso`.
2. **Make it publicly readable** — bucket **Settings** → **Public access** →
   enable the `r2.dev` subdomain, or attach a custom domain (better for a real
   download endpoint; set it up under the bucket's **Custom domains**).
3. **Create an API key** — R2 → **Manage R2 API tokens** → **Create API token**
   → permission **Object Read & Write**, scope it to `ou-linux-iso`. Copy the
   **Access Key ID** and **Secret Access Key**. Copy the **Account ID** from the
   R2 overview page.
4. **Store them locally** on this machine, e.g.:

   ```
   ~/.config/ou-r2.env
   R2_ACCOUNT_ID=...
   R2_ACCESS_KEY_ID=...
   R2_SECRET_ACCESS_KEY=...
   R2_BUCKET=ou-linux-iso
   # optional, if you attached a custom domain:
   R2_PUBLIC_BASE=https://iso.yourdomain.com
   ```

   `chmod 600 ~/.config/ou-r2.env`. Keep it out of Git and out of chat.

## Then I take over

Tell me the env-file path and I'll run `tools/upload-iso-r2.sh`, which:

- verifies the local ISO's SHA-256 before uploading,
- PUTs the object via `curl --aws-sigv4` (no extra packages needed),
- verifies the upload with a signed range request,
- prints the public URL and the exact `mirrors` entry to add to
  `site/site.config.js`.

Then I add the mirror, push to `main`, and verify the live download button and
the URL's HTTP status. Final check: `curl -I -L <url>` (expect 200/206 and a
content length near 3,037,724,672 bytes), then `sha256sum` the downloaded file.

## No-API alternative

If you'd rather not create a token: in the R2 bucket, use **Upload** and drag in
`OU-OS-Akar-Alpha-v36.iso`, enable public access, and send me the resulting URL.
I'll wire it into the site and verify it the same way.

## Card-free alternative: Internet Archive (recommended when R2 needs a card)

R2 asks for a payment method. Internet Archive does not, and 2.83 GiB is well
within its limits (items up to ~100 GB, single files up to ~500 GB).

1. Create a free account: https://archive.org/account/register.php
2. Get your IA-S3 keys: https://archive.org/account/s3.php
3. Write a local env file (chmod 600, never in chat or Git):
   ```
   ~/.config/ou-archive.env
   IA_ACCESS_KEY_ID=...
   IA_SECRET_ACCESS_KEY=...
   IA_IDENTIFIER=ou-linux-akar-akar-alpha-v36
   ```
   The identifier must be globally unique on archive.org.
4. Tell me the path. `tools/upload-iso-archive.sh` verifies the local SHA-256,
   installs its own CLI into `~/.local/share/ou-linux-ia-libs`, uploads with
   `--verify`, and prints the permanent URL:
   `https://archive.org/download/<identifier>/OU-OS-Akar-Alpha-v36.iso`
5. I add that URL to `mirrors` in `site/site.config.js`, push to `main`, and
   verify the live download button and HTTP range response.
