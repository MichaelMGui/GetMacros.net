/* GetMacros Unified v7 interactions.
 * Navigation and motion are progressive enhancement: no content, result, or
 * control depends on this file becoming available.
 */
(function () {
  "use strict";

  var mobile = window.matchMedia && window.matchMedia("(max-width: 900px)");

  function headerState() {
    var header=document.querySelector('.site-header');
    if(!header||!window.IntersectionObserver)return;
    var marker=document.createElement('span');
    marker.setAttribute('aria-hidden','true');
    marker.style.cssText='position:absolute;top:18px;left:0;width:1px;height:1px;pointer-events:none';
    document.body.prepend(marker);
    new IntersectionObserver(function(entries){
      var scrolled=entries[0].boundingClientRect.bottom<0;
      if(header.classList.contains('has-scroll')!==scrolled)header.classList.toggle('has-scroll',scrolled);
    }).observe(marker);
  }

  function readingProgress() {
    var content=document.querySelector('.article-container,.focused-guide-body');
    var header=document.querySelector('.full-nav');
    if(!content||!header||content.textContent.trim().split(/\s+/).length<700)return;
    var track=document.createElement('div'),fill=document.createElement('span');
    track.className='reading-progress';track.setAttribute('aria-hidden','true');
    track.append(fill);header.append(track);
    var start=0,end=1,queued=false,last=-1;
    function paint(){
      queued=false;
      if(document.hidden)return;
      var amount=Math.round(Math.max(0,Math.min(1,(scrollY-start)/(end-start)))*200)/200;
      if(amount!==last){fill.style.setProperty('--read-progress',String(amount));last=amount;}
    }
    function measure(){
      var rect=content.getBoundingClientRect();
      start=scrollY+rect.top-innerHeight*.28;
      end=Math.max(start+1,start+rect.height-innerHeight*.52);
      paint();
    }
    // Geometry changes only on resize/content expansion, never during scrolling.
    if(window.ResizeObserver)new ResizeObserver(measure).observe(content);
    addEventListener('resize',measure,{passive:true});
    addEventListener('scroll',function(){if(!queued){queued=true;requestAnimationFrame(paint);}},{passive:true});
    measure();
  }

  function theme() {
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    if (!buttons.length) return;
    var stored = "";
    try { stored = localStorage.getItem("gm-theme") || ""; } catch (error) {}
    var initial = document.documentElement.getAttribute("data-theme") || stored || "light";
    function apply(mode, remember) {
      document.documentElement.setAttribute("data-theme", mode);
      if (remember) {
        try { localStorage.setItem("gm-theme", mode); } catch (error) {}
      }
      var dark = mode === "dark";
      buttons.forEach(function (button) {
        button.setAttribute("aria-pressed", String(dark));
        button.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
        // The moon and sun are both in the markup; CSS reveals the one that
        // matches the current theme, so nothing here touches .theme-icon.
        var label = button.querySelector(".theme-label");
        if (label) label.textContent = dark ? "Light" : "Dark";
      });
      var meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.setAttribute("content", dark ? "#132d24" : "#f7faf3");
    }
    apply(initial === "dark" ? "dark" : "light", false);
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        apply(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark", true);
      });
    });
  }

  function navigation() {
    var nav = document.querySelector(".full-nav");
    if (!nav) return;
    var toggle = nav.querySelector(".nav-toggle");
    var links = nav.querySelector(".full-nav-links");
    var groups = Array.prototype.slice.call(nav.querySelectorAll(".nav-group"));
    if (!links) return;

    function revealPanel(panel) {
      if (!panel || !panel.animate || matchMedia('(prefers-reduced-motion: reduce)').matches || document.documentElement.classList.contains('tide-motion-off')) return;
      if (panel._entrance) panel._entrance.cancel();
      panel._entrance = panel.animate([
        {opacity:.55,scale:'.97',translate:'0 -5px'},
        {opacity:1,scale:'1',translate:'0 0'}
      ],{duration:240,easing:'cubic-bezier(.22,1,.36,1)'});
    }
    function openGroup(group, open) {
      closeGroups(group);
      group.classList.toggle('is-open',open);
      group.querySelector('.nav-group-trigger').setAttribute('aria-expanded',String(open));
      var panel=group.querySelector('.nav-popover');
      if(open) revealPanel(panel);
      else if(panel._entrance) panel._entrance.cancel();
    }
    function focusChoice(choice) {
      choice.focus({preventScroll:true});
      // Move only the mobile sheet, never the page behind it.
      if(mobile.matches){
        var item=choice.getBoundingClientRect(),sheet=links.getBoundingClientRect();
        if(item.bottom>sheet.bottom-12)links.scrollTop+=item.bottom-sheet.bottom+12;
        else if(item.top<sheet.top+12)links.scrollTop+=item.top-sheet.top-12;
      }
    }

    function closeGroups(except) {
      groups.forEach(function (group) {
        if (group === except) return;
        var panel=group.querySelector('.nav-popover');
        if(panel && panel._entrance) panel._entrance.cancel();
        group.classList.remove("is-open");
        var trigger = group.querySelector(".nav-group-trigger");
        if (trigger) trigger.setAttribute("aria-expanded", "false");
      });
    }
    // The menu deliberately does not lock body scroll.
    //
    // `.nav-open{overflow:hidden}` reset the page to the top, because a body
    // that is still scrolled stops being scrollable -- the "I have to scroll
    // back up" problem. Pinning the body with position:fixed fixed that but
    // moved the drawer out of the viewport, since it is anchored inside a
    // sticky header.
    //
    // Leaving scroll alone is simpler and correct: the header is sticky, so
    // the drawer opens under it wherever you are, and closing the menu cannot
    // lose your place because nothing ever moved.
    function setNav(open) {
      var entering = open && !document.body.classList.contains('nav-open');
      document.body.classList.toggle("nav-open", open);
      if (entering) revealPanel(links);
      if (!open && links._entrance) links._entrance.cancel();
      if (toggle) {
        toggle.setAttribute("aria-expanded", String(open));
        var label = toggle.querySelector(".sr-only");
        if (label) label.textContent = open ? "Close site menu" : "Open site menu";
      }
      if (!open) closeGroups();
    }
    if (toggle) {
      toggle.addEventListener("click", function () {
        setNav(!document.body.classList.contains("nav-open"));
      });
    }
    groups.forEach(function (group, index) {
      var trigger = group.querySelector(".nav-group-trigger");
      if (!trigger) return;
      var panel=group.querySelector('.nav-popover');
      panel.id='navigation-panel-'+index;
      trigger.setAttribute('aria-controls',panel.id);
      trigger.addEventListener("click", function () {
        openGroup(group,!group.classList.contains('is-open'));
      });
      trigger.addEventListener('keydown',function(event){
        if(event.key!=='ArrowDown' && event.key!=='ArrowUp')return;
        event.preventDefault();openGroup(group,true);
        var choices=panel.querySelectorAll('a');
        focusChoice(choices[event.key==='ArrowUp'?choices.length-1:0]);
      });
      panel.addEventListener('keydown',function(event){
        var choices=Array.from(panel.querySelectorAll('a')),at=choices.indexOf(document.activeElement),next;
        if(event.key==='ArrowDown')next=(at+1)%choices.length;
        else if(event.key==='ArrowUp')next=(at-1+choices.length)%choices.length;
        else if(event.key==='Home')next=0;
        else if(event.key==='End')next=choices.length-1;
        else return;
        event.preventDefault();focusChoice(choices[next]);
      });
    });
    document.addEventListener("click", function (event) {
      if (!nav.contains(event.target)) setNav(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      var openGroup = nav.querySelector('.nav-group.is-open');
      var groupTrigger = openGroup && openGroup.querySelector('.nav-group-trigger');
      var wasOpen = document.body.classList.contains("nav-open");
      setNav(false);
      if (!wasOpen && groupTrigger) groupTrigger.focus({preventScroll:true});
      if (wasOpen && toggle) {
        try { toggle.focus({ preventScroll: true }); }
        catch (error) { toggle.focus(); }
      }
    });
    nav.addEventListener('focusout',function(event){
      if(event.relatedTarget && !nav.contains(event.relatedTarget))setNav(false);
    });
    addEventListener('pageshow',function(event){if(event.persisted)setNav(false);});
    links.addEventListener("click", function (event) {
      if (mobile.matches && event.target.closest("a")) setNav(false);
    });
    if (mobile.addEventListener) mobile.addEventListener("change", function () { setNav(false); });

    var current = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    links.querySelectorAll("a[href]").forEach(function (link) {
      var target = (link.getAttribute("href") || "").split("#")[0].split("?")[0].split("/").pop().toLowerCase();
      var active = target === current;
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
      if (active) {
        var parent = link.closest(".nav-group");
        if (parent) parent.classList.add("is-current");
      }
    });
  }

  function accessibility() {
    document.querySelectorAll(".table-wrap,.table-scroll").forEach(function (wrap) {
      if (!wrap.hasAttribute("tabindex")) wrap.tabIndex = 0;
      if (!wrap.hasAttribute("role")) wrap.setAttribute("role", "region");
      if (!wrap.hasAttribute("aria-label")) wrap.setAttribute("aria-label", "Scrollable nutrition table");
    });
    document.querySelectorAll("main img:not([width])").forEach(function (image) {
      image.setAttribute("decoding", "async");
    });
  }

  function compactRankings() {
    document.querySelectorAll(".ranking-card .ranking-list").forEach(function (list) {
      // The parent disclosure already controls density; avoid a second reveal.
      if (list.closest("details")) return;
      var rows = Array.prototype.slice.call(list.children);
      if (rows.length <= 5 || list.dataset.compactReady) return;
      list.dataset.compactReady = "true";
      rows.slice(5, 8).forEach(function (row) { row.classList.add("ranking-extra"); });
      rows.slice(8).forEach(function (row) { row.classList.add("ranking-overflow"); });
      var button = document.createElement("button");
      button.type = "button";
      button.className = "ranking-more";
      button.setAttribute("aria-expanded", "false");
      button.textContent = "See 3 more";
      button.addEventListener("click", function () {
        var open = list.classList.toggle("show-all");
        button.setAttribute("aria-expanded", String(open));
        button.textContent = open ? "Show top 5" : "See " + Math.min(3, rows.length - 5) + " more";
      });
      list.insertAdjacentElement("afterend", button);
    });
  }

  function start() {
    try { theme(); } catch (error) {}
    try { headerState(); } catch (error) {}
    try { readingProgress(); } catch (error) {}
    try { navigation(); } catch (error) {}
    try { accessibility(); } catch (error) {}
    try { compactRankings(); } catch (error) {}
    // Legacy reveal hooks stay visible without observers or entrance motion.
    document.querySelectorAll('.studio-reveal').forEach(item => item.classList.add('is-visible'));
    // Avoid repainting large gradients on every pointer movement.
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
}());
