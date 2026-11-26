/* Populates the page from site.config.js. No dependencies. */
(function () {
  "use strict";

  var cfg = window.OU_CONFIG;
  if (!cfg) {
    document.getElementById("download-primary").innerHTML =
      '<div class="download-pending"><strong>Configuration missing</strong>' +
      '<span>Restore site.config.js to show release details.</span></div>';
    return;
  }

  function bytes(value) {
    var gib = value / (1024 * 1024 * 1024);
    return gib.toFixed(2) + " GiB (" + new Intl.NumberFormat("en-US").format(value) + " bytes)";
  }

  var values = {
    project: cfg.project,
    fullName: cfg.fullName,
    release: cfg.release,
    version: cfg.version,
    codename: cfg.codename,
    status: cfg.status,
    file: cfg.file,
    size: bytes(cfg.sizeBytes),
    base: cfg.base,
    desktop: cfg.desktop
  };

  document.querySelectorAll("[data-config]").forEach(function (el) {
    var key = el.getAttribute("data-config");
    if (Object.prototype.hasOwnProperty.call(values, key)) {
      el.textContent = values[key];
    }
  });

  document.querySelectorAll("[data-link]").forEach(function (el) {
    var key = el.getAttribute("data-link");
    if (cfg[key]) { el.href = cfg[key]; }
  });

  document.title = cfg.project + " — " + cfg.release + " · Orang Utan Distro";

  /* Primary download + mirror list */
  var primary = document.getElementById("download-primary");
  var mirrorsBox = document.getElementById("mirrors");
  primary.textContent = "";
  mirrorsBox.textContent = "";

  if (Array.isArray(cfg.mirrors) && cfg.mirrors.length > 0) {
    var valid = cfg.mirrors.filter(function (m) { return m && m.url; });
    if (valid.length > 0) {
      var main = document.createElement("a");
      main.className = "btn btn-download";
      main.href = valid[0].url;
      main.setAttribute("download", cfg.file);
      main.textContent = "Download " + cfg.file + " ↓";
      primary.appendChild(main);

      valid.forEach(function (m) {
        var link = document.createElement("a");
        link.className = "mirror";
        link.href = m.url;
        link.setAttribute("download", cfg.file);

        var left = document.createElement("span");
        var name = document.createElement("span");
        name.className = "mirror-name";
        name.textContent = m.name || "Mirror";
        var note = document.createElement("span");
        note.className = "mirror-note";
        note.textContent = m.note || "Direct ISO download";
        left.appendChild(name);
        left.appendChild(note);

        var arrow = document.createElement("span");
        arrow.className = "mirror-arrow";
        arrow.setAttribute("aria-hidden", "true");
        arrow.textContent = "↗";

        link.appendChild(left);
        link.appendChild(arrow);
        mirrorsBox.appendChild(link);
      });
    } else {
      renderPending();
    }
  } else {
    renderPending();
  }

  function renderPending() {
    var box = document.createElement("div");
    box.className = "download-pending";
    var title = document.createElement("strong");
    title.textContent = "ISO link not published yet";
    var note = document.createElement("span");
    note.textContent = "This " + cfg.version + " image is documented, but no public mirror is configured. Add a URL to mirrors in site.config.js to enable downloads.";
    box.appendChild(title);
    box.appendChild(note);
    primary.appendChild(box);

    var p = document.createElement("p");
    p.className = "pending";
    p.textContent = "No mirrors available. Do not trust ISOs from unofficial sources.";
    mirrorsBox.appendChild(p);
  }

  /* Checksum display + copy */
  document.getElementById("sha-value").textContent = cfg.sha256;
  document.getElementById("verify-cmd").textContent = "sha256sum " + cfg.file;

  var copyBtn = document.getElementById("copy-sha");
  var status = document.getElementById("copy-status");
  copyBtn.addEventListener("click", function () {
    var text = cfg.sha256;
    function done(ok) {
      status.textContent = ok ? "Checksum copied to clipboard." : "Copy failed — select the checksum manually.";
      window.setTimeout(function () { status.textContent = ""; }, 3000);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
    } else {
      var area = document.createElement("textarea");
      area.value = text;
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(area);
      done(ok);
    }
  });
})();
