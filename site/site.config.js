/* OU Linux website — single file to edit when publishing a new release.
   Add each public download URL to `mirrors`. Until then the page honestly
   shows a "link not published yet" state instead of a broken download. */
window.OU_CONFIG = {
  project: "OU Linux",
  fullName: "Orang Utan Linux",
  release: "Akar Alpha v36",
  version: "v36",
  codename: "Akar",
  status: "Alpha",
  file: "OU-OS-Akar-Alpha-v36.iso",
  sizeBytes: 3037724672,
  sha256: "a3d34fec32ca70133a5c45a4b643609118365a268f9a932464554066650cc779",
  base: "Debian 13 (trixie)",
  desktop: "Xfce",
  sourceUrl: "https://github.com/PatrickNoFilter/ou-linux-akar",
  repoMenu: "https://github.com/PatrickNoFilter/xfce4-ou-menu-plugin",
  repoQuickSettings: "https://github.com/PatrickNoFilter/ou-quick-settings",
  // Example once you have a public URL:
  // { name: "Primary", url: "https://your-host/OU-OS-Akar-Alpha-v36.iso", note: "Direct download" }
  mirrors: []
};
