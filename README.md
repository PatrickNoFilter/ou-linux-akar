# OU Linux — Akar (Alpha)

**OU Linux** (Orang Utan Linux) is a Debian 13 (`trixie`) based GNU/Linux
distribution for the desktop. This repository documents the **Akar (Alpha)**
series.

> Status: **Alpha** — intended for testing and development, not production.

The project branding uses the orangutan ("Orang Utan") mascot of the OU Linux
distro. The default desktop is Xfce with the customized **OU Menu** launcher.

## Latest ISO

| Item | Value |
|------|-------|
| File | `OU-OS-Akar-Alpha-v36.iso` |
| Size | 3,037,724,672 bytes (~2.83 GiB) |
| SHA-256 | `a3d34fec32ca70133a5c45a4b643609118365a268f9a932464554066650cc779` |

The ISO is **not** stored in this Git repository. GitHub rejects files larger
than 100 MB in Git, and release assets are limited to 2 GB per file. Distribute
the ISO through an external file host, or split it into parts for releases.

Verify a downloaded image with:

```bash
sha256sum OU-OS-Akar-Alpha-v36.iso
```

## System identity

```
PRETTY_NAME="OU OS Akar (Alpha)"
NAME="OU OS"
VERSION="Akar (Alpha)"
VERSION_CODENAME=akar
ID_LIKE=debian
```

## Components

- [Debian](https://www.debian.org/) 13 (`trixie`) — base distribution
- [Xfce](https://xfce.org/) — desktop environment
- [OU Menu](https://github.com/PatrickNoFilter/xfce4-ou-menu-plugin) — customized panel launcher

## Credits

- The Debian Project
- The Xfce Development Team
- Matteo Bonanomi — Meow Menu (upstream of OU Menu)
- Graeme Gott — original Xfce Whisker Menu

## License

This repository's documentation is provided as-is. The ISO image contains
third-party packages, each under its own license; refer to the packages inside
the image for their license terms.
