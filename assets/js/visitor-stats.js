(function () {
  "use strict";

  // GitHub Pages is static, so the two site-wide counters live in CountAPI.
  // Counts begin with this integration; the previous Busuanzi totals are unavailable.
  var api = "https://countapi.mileshilliard.com/api/v1";
  var pageViewsKey = "yongxie_icmm_github_io_site_page_views_20261028";
  var visitorsKey = "yongxie_icmm_github_io_unique_browsers_20261028";
  var visitorFlag = "yongxie_icmm_counted_visitor_v1";
  var pageViews = document.getElementById("site-page-views");
  var visitors = document.getElementById("site-unique-visitors");

  function stored(key) {
    try { return window.localStorage.getItem(key); } catch (_) { return null; }
  }

  function save(key, value) {
    try { window.localStorage.setItem(key, String(value)); } catch (_) { /* Storage may be disabled. */ }
  }

  function show(element, value, cached) {
    if (!element) return;
    var count = Number(value);
    element.textContent = value === null || !Number.isSafeInteger(count) || count < 0
      ? "Unavailable" : count.toLocaleString("en-US");
    element.title = cached ? "Last recorded count; the counter is temporarily unavailable" : "";
  }

  async function counter(operation, key) {
    var controller = new AbortController();
    var timeout = window.setTimeout(function () { controller.abort(); }, 8000);
    try {
      var response = await fetch(api + "/" + operation + "/" + key, {
        cache: "no-store",
        signal: controller.signal
      });
      if (!response.ok) throw new Error("Counter returned " + response.status);
      var data = await response.json();
      var value = Number(data.value);
      if (!Number.isSafeInteger(value) || value < 0) throw new Error("Invalid counter value");
      return value;
    } finally {
      window.clearTimeout(timeout);
    }
  }

  async function updatePageViews() {
    try {
      var value = await counter("hit", pageViewsKey);
      save("yongxie_icmm_last_page_views", value);
      show(pageViews, value, false);
    } catch (_) {
      var last = stored("yongxie_icmm_last_page_views");
      show(pageViews, last === null ? null : Number(last), last !== null);
    }
  }

  async function updateVisitors() {
    var alreadyCounted = stored(visitorFlag) === "1";
    if (alreadyCounted && !visitors) return;
    try {
      var value = await counter(alreadyCounted ? "get" : "hit", visitorsKey);
      if (!alreadyCounted) save(visitorFlag, "1");
      save("yongxie_icmm_last_visitors", value);
      show(visitors, value, false);
    } catch (_) {
      var last = stored("yongxie_icmm_last_visitors");
      show(visitors, last === null ? null : Number(last), last !== null);
    }
  }

  var lastPageViews = stored("yongxie_icmm_last_page_views");
  var lastVisitors = stored("yongxie_icmm_last_visitors");
  if (pageViews && lastPageViews !== null) show(pageViews, lastPageViews, true);
  if (visitors && lastVisitors !== null) show(visitors, lastVisitors, true);
  updatePageViews();
  updateVisitors();
}());
