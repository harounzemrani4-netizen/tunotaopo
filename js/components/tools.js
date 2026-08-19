(function (root) {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function isClassroom() {
    try {
      return new URLSearchParams(location.search).get("mode") === "classroom";
    } catch (ignore) {
      return false;
    }
  }

  function setClassroom(on) {
    var url = new URL(location.href);
    if (on) url.searchParams.set("mode", "classroom");
    else url.searchParams.delete("mode");
    history.replaceState({}, "", url.pathname + url.search + url.hash);
    document.documentElement.classList.toggle("is-classroom", on);
    updateClassroomButtons(on);
  }

  function updateClassroomButtons(on) {
    var enter = $("classroom-enter");
    var exit = $("classroom-exit");
    if (enter) enter.hidden = on;
    if (exit) exit.hidden = !on;
  }

  function bindClassroom() {
    var on = isClassroom();
    document.documentElement.classList.toggle("is-classroom", on);
    updateClassroomButtons(on);
    var enter = $("classroom-enter");
    var exit = $("classroom-exit");
    if (enter) {
      enter.addEventListener("click", function () {
        setClassroom(true);
      });
    }
    if (exit) {
      exit.addEventListener("click", function () {
        setClassroom(false);
      });
    }
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(function () {
        return copyFallback(text);
      });
    }
    return copyFallback(text);
  }

  function copyFallback(text) {
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      var ok = false;
      try {
        ok = document.execCommand("copy");
      } catch (ignore) {}
      document.body.removeChild(area);
      if (ok) resolve();
      else reject(new Error("No se pudo copiar"));
    });
  }

  function flash(button, label) {
    if (!button) return;
    var original = button.textContent;
    button.textContent = label;
    window.setTimeout(function () {
      button.textContent = original;
    }, 2000);
  }

  function pageUrl() {
    return location.origin + location.pathname + location.search;
  }

  function bindShare() {
    var nativeBtn = $("share-native");
    var qrBtn = $("show-qr");
    var qrBox = $("qr-box");
    if (nativeBtn) {
      nativeBtn.addEventListener("click", function () {
        var url = pageUrl();
        var title = document.title;
        if (navigator.share) {
          navigator.share({ title: title, url: url }).catch(function () {
            copyText(url).then(function () {
              flash(nativeBtn, "Enlace copiado");
            });
          });
          return;
        }
        copyText(url).then(function () {
          flash(nativeBtn, "Enlace copiado");
        });
      });
    }
    var printBtn = $("print-result");
    if (printBtn) {
      printBtn.addEventListener("click", function () {
        window.print();
      });
    }
    if (qrBtn && qrBox) {
      qrBtn.addEventListener("click", function () {
        if (!qrBox.hidden && qrBox.innerHTML) {
          qrBox.hidden = true;
          qrBox.innerHTML = "";
          qrBtn.textContent = "Mostrar QR";
          return;
        }
        var url = location.origin + location.pathname;
        try {
          if (!root.NotaOpoQR) throw new Error("QR no disponible");
          qrBox.innerHTML =
            '<p class="qr-kicker">Escanea para abrir esta calculadora</p>' +
            root.NotaOpoQR.toSvg(url) +
            '<p class="qr-url">' +
            url.replace(/&/g, "&amp;") +
            "</p>";
          qrBox.hidden = false;
          qrBtn.textContent = "Ocultar QR";
        } catch (err) {
          qrBox.innerHTML = '<p>No se pudo generar el QR. Copia el enlace de esta página.</p>';
          qrBox.hidden = false;
        }
      });
    }
  }

  root.NotaOpoTools = {
    bindClassroom: bindClassroom,
    bindShare: bindShare,
    copyText: copyText,
    flash: flash,
    isClassroom: isClassroom
  };
})(window);
