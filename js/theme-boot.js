(function () {
  try {
    var theme = localStorage.getItem("tunotaopo:theme");
    if (theme === "dark" || theme === "light") {
      document.documentElement.setAttribute("data-theme", theme);
    }
  } catch (ignore) {}
})();
