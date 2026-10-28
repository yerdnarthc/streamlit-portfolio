const ENGINE_KEY = "__arthPortfolioMotionEngine";
const ENGINE_VERSION = "1.2.0";
const ROOT_SELECTOR = '[data-testid="stAppViewContainer"]';
const MAIN_SCROLL_SELECTOR = '[data-testid="stMain"]';
const PORTFOLIO_TABS_SELECTOR =
  '[class*="st-key-pf_project_tabs_"] [data-testid="stTabs"]';
const PAGE_ROOTS = [
  ["about", ".st-key-about_page"],
  ["autobiography", ".st-key-autobiography_page"],
  ["skills", ".st-key-skills_page"],
  ["portfolio", ".st-key-portfolio_page"],
  ["feedback", ".st-key-feedback_page"],
];
const MOTION_TOKENS = Object.freeze({
  tiltX: 1.35,
  tiltY: 1.7,
  parallaxX: 3.5,
  parallaxY: 3,
});

const REVEAL_GROUPS = [
  {
    selector: ".st-key-sidebar_identity",
    motion: "shell",
    initialOnly: true,
  },
  {
    selector: ".st-key-primary_navigation label",
    motion: "nav-item",
    initialOnly: true,
    delay: 90,
    stagger: 50,
  },
  {
    selector: ".st-key-about_identity h2",
    motion: "hero-title",
  },
  {
    selector: '[class*="st-key-about_fact_"]',
    motion: "line-item",
    delay: 120,
    stagger: 78,
  },
  {
    selector: ".st-key-about_photo_frame",
    motion: "image-mask",
    delay: 160,
    eager: true,
  },
  {
    selector: ".st-key-about_biography",
    motion: "editorial",
  },
  {
    selector: ".st-key-autobiography_page h2",
    motion: "page-title",
  },
  {
    selector: ".st-key-autobiography_preface",
    motion: "editorial",
    delay: 80,
  },
  {
    selector: '[class*="st-key-autobio_chapter_"]',
    motion: "chapter",
    stagger: 62,
    alternate: true,
  },
  {
    selector: ".st-key-autobiography_code_panel, .st-key-autobiography_download",
    motion: "panel",
    stagger: 72,
  },
  {
    selector: ".st-key-skills_page h2",
    motion: "page-title",
  },
  {
    selector: ".st-key-skills_controls",
    motion: "control-group",
    delay: 65,
  },
  {
    selector: '[class*="st-key-skills_spotlight_"]',
    motion: "skills-spotlight",
    replay: true,
    eager: true,
  },
  {
    selector: ".st-key-skills_metrics [data-testid=\"stMetric\"]",
    motion: "metric",
    stagger: 82,
  },
  {
    selector: '[class*="st-key-skills_metrics_stage_"]',
    motion: "skills-metrics-stage",
    replay: true,
    eager: true,
  },
  {
    selector: ".st-key-skills_chart, .st-key-skills_table",
    motion: "panel",
    stagger: 88,
  },
  {
    selector: '[class*="st-key-skills_chart_stage_"]',
    motion: "skills-chart-stage",
    replay: true,
    eager: true,
  },
  {
    selector: '[class*="st-key-skills_table_stage_"]',
    motion: "skills-table-stage",
    replay: true,
    eager: true,
  },
  {
    selector: ".st-key-skills_empty_state [data-testid=\"stAlert\"]",
    motion: "feedback-error",
    replay: true,
  },
  {
    selector: ".st-key-portfolio_page h2",
    motion: "page-title",
  },
  {
    selector: '[class*="st-key-pf_group_header_"]',
    motion: "line-item",
  },
  {
    selector: ".st-key-pf_index_bar, .st-key-pf_browse_toolbar",
    motion: "control-group",
    stagger: 72,
  },
  {
    selector: '[class*="st-key-pf_project_stage_"]',
    motion: "project-stage",
    replay: true,
    eager: true,
  },
  {
    selector: ".st-key-feedback_intro",
    motion: "page-title",
  },
  {
    selector: ".st-key-feedback_form_shell",
    motion: "panel",
    delay: 80,
  },
  {
    selector: ".st-key-feedback_error [data-testid=\"stAlert\"]",
    motion: "feedback-error",
    replay: true,
  },
  {
    selector: ".st-key-feedback_success",
    motion: "feedback-success",
    replay: true,
  },
  {
    selector: ".st-key-autobiography_page [data-testid=\"stCode\"]",
    motion: "feedback",
    replay: true,
  },
  {
    selector: ".st-key-skills_page [data-testid=\"stAlert\"], .st-key-portfolio_page [data-testid=\"stAlert\"]",
    motion: "feedback",
    replay: true,
  },
];

const TILT_SELECTOR = [
  ".st-key-about_photo_frame",
  '[class*="st-key-pf_preview_frame"]',
  '[class*="st-key-skills_spotlight_"]',
].join(",");

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function createMotionEngine() {
  const abortController = new AbortController();
  const { signal } = abortController;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia(
    "(hover: hover) and (pointer: fine) and (min-width: 900px)",
  );
  const revealTargets = new Set();
  const tiltTargets = new Set();
  const liveAnimations = new Set();
  const seenRevealIdentities = new Set();
  const initialGroupsBound = new Set();
  const portfolioTabStates = new WeakMap();
  const portfolioTabAnimations = new WeakMap();
  let destroyed = false;
  let discoveryFrame = 0;
  let pageScrollFrame = 0;
  let scrollFrame = 0;
  let autobiographyTimeline = null;
  let activePage = "";

  const reveal = (element) => {
    if (!element || element.dataset.motionState === "revealed") return;
    element.dataset.motionState = "revealed";
    if (element.dataset.motionIdentity) {
      seenRevealIdentities.add(element.dataset.motionIdentity);
    }
    intersectionObserver?.unobserve(element);
  };

  const intersectionObserver = "IntersectionObserver" in window
    ? new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) reveal(entry.target);
          });
        },
        {
          root: null,
          rootMargin: "0px 0px -10% 0px",
          threshold: 0.08,
        },
      )
    : null;

  const bindReveal = (element, group, index) => {
    if (!element || element.dataset.motionBound === ENGINE_VERSION) return;

    element.dataset.motionBound = ENGINE_VERSION;
    element.dataset.motion = group.motion;
    const identity = group.replay
      ? ""
      : `${activePage}:${group.motion}:${group.selector}:${index}`;
    if (identity) element.dataset.motionIdentity = identity;
    element.style.setProperty(
      "--motion-delay",
      `${(group.delay ?? 0) + (group.stagger ?? 0) * index}ms`,
    );

    if (group.alternate) {
      element.style.setProperty(
        "--motion-x",
        index % 2 === 0 ? "-16px" : "16px",
      );
    }

    revealTargets.add(element);

    if (identity && seenRevealIdentities.has(identity)) {
      reveal(element);
      return;
    }

    if (reducedMotion.matches) {
      if (document.documentElement.classList.contains("portfolio-motion-ready")) {
        element.dataset.motionState = "pending";
        requestAnimationFrame(() => reveal(element));
      } else {
        reveal(element);
      }
      return;
    }

    if (!intersectionObserver) {
      reveal(element);
      return;
    }

    element.dataset.motionState = "pending";
    if (group.eager) {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => reveal(element));
      });
      return;
    }

    intersectionObserver.observe(element);
  };

  const resetTilt = (element) => {
    element.style.setProperty("--motion-tilt-x", "0deg");
    element.style.setProperty("--motion-tilt-y", "0deg");
    element.style.setProperty("--motion-shift-x", "0px");
    element.style.setProperty("--motion-shift-y", "0px");
    element.classList.remove("motion-interacting");
  };

  const bindTilt = (element) => {
    if (!element || element.dataset.motionTiltBound === ENGINE_VERSION) return;

    element.dataset.motionTiltBound = ENGINE_VERSION;
    element.classList.add("motion-tilt-target");
    tiltTargets.add(element);
    let pointerFrame = 0;
    let nextX = 0;
    let nextY = 0;
    let bounds = null;

    const writePointerPosition = () => {
      pointerFrame = 0;
      if (!element.isConnected || reducedMotion.matches || !finePointer.matches) {
        resetTilt(element);
        return;
      }

      element.style.setProperty(
        "--motion-tilt-x",
        `${nextY * -MOTION_TOKENS.tiltX}deg`,
      );
      element.style.setProperty(
        "--motion-tilt-y",
        `${nextX * MOTION_TOKENS.tiltY}deg`,
      );
      element.style.setProperty(
        "--motion-shift-x",
        `${nextX * MOTION_TOKENS.parallaxX}px`,
      );
      element.style.setProperty(
        "--motion-shift-y",
        `${nextY * MOTION_TOKENS.parallaxY}px`,
      );
    };

    element.addEventListener(
      "pointerenter",
      () => {
        if (!reducedMotion.matches && finePointer.matches) {
          bounds = element.getBoundingClientRect();
          element.classList.add("motion-interacting");
        }
      },
      { signal },
    );

    element.addEventListener(
      "pointermove",
      (event) => {
        if (reducedMotion.matches || !finePointer.matches) return;
        bounds ??= element.getBoundingClientRect();
        nextX = clamp(((event.clientX - bounds.left) / bounds.width) * 2 - 1, -1, 1);
        nextY = clamp(((event.clientY - bounds.top) / bounds.height) * 2 - 1, -1, 1);
        if (!pointerFrame) pointerFrame = requestAnimationFrame(writePointerPosition);
      },
      { signal, passive: true },
    );

    element.addEventListener(
      "pointerleave",
      () => {
        if (pointerFrame) cancelAnimationFrame(pointerFrame);
        pointerFrame = 0;
        bounds = null;
        resetTilt(element);
      },
      { signal },
    );
  };

  const trackAnimation = (animation) => {
    if (!animation) return null;
    liveAnimations.add(animation);
    animation.addEventListener(
      "finish",
      () => {
        liveAnimations.delete(animation);
        animation.cancel();
      },
      { once: true },
    );
    animation.addEventListener(
      "cancel",
      () => liveAnimations.delete(animation),
      { once: true },
    );
    return animation;
  };

  const animateActivePortfolioTab = (tabGroup, previousIndex, selectedIndex) => {
    const panel = tabGroup.querySelector('[data-testid="stTabPanel"]');
    if (!panel?.animate) return;

    portfolioTabAnimations.get(tabGroup)?.cancel();
    const direction = selectedIndex > previousIndex ? 1 : -1;
    const keyframes = reducedMotion.matches
      ? [{ opacity: 0.72 }, { opacity: 1 }]
      : [
          {
            clipPath:
              direction > 0 ? "inset(0 8% 0 0)" : "inset(0 0 0 8%)",
            opacity: 0.24,
            transform: `translate3d(${direction * 10}px, 0, 0)`,
          },
          {
            clipPath: "inset(0 0 0 0)",
            opacity: 1,
            transform: "translate3d(0, 0, 0)",
          },
        ];
    const animation = panel.animate(keyframes, {
      duration: reducedMotion.matches ? 140 : 360,
      easing: "cubic-bezier(0.16, 1, 0.3, 1)",
      fill: "both",
    });
    portfolioTabAnimations.set(tabGroup, animation);
    trackAnimation(animation);
  };

  const discoverPortfolioTabs = () => {
    document.querySelectorAll(PORTFOLIO_TABS_SELECTOR).forEach((tabGroup) => {
      const tabs = [...tabGroup.querySelectorAll('[role="tab"]')];
      const selectedIndex = tabs.findIndex(
        (tab) => tab.getAttribute("aria-selected") === "true",
      );
      if (selectedIndex < 0) return;

      const previousIndex = portfolioTabStates.get(tabGroup);
      portfolioTabStates.set(tabGroup, selectedIndex);
      if (previousIndex === undefined || previousIndex === selectedIndex) return;
      animateActivePortfolioTab(tabGroup, previousIndex, selectedIndex);
    });
  };

  const updateScrollProgress = () => {
    scrollFrame = 0;
    if (!autobiographyTimeline?.isConnected) return;

    if (reducedMotion.matches) {
      autobiographyTimeline.style.setProperty("--motion-scroll-progress", "1");
      return;
    }

    const bounds = autobiographyTimeline.getBoundingClientRect();
    const viewportHeight = window.innerHeight || 1;
    const travel = bounds.height + viewportHeight * 0.45;
    const progress = clamp(
      (viewportHeight * 0.72 - bounds.top) / Math.max(travel, 1),
      0,
      1,
    );
    autobiographyTimeline.style.setProperty(
      "--motion-scroll-progress",
      progress.toFixed(4),
    );
  };

  const scheduleScrollProgress = () => {
    if (!autobiographyTimeline?.isConnected || reducedMotion.matches) return;
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScrollProgress);
  };

  const setPageScrollTop = () => {
    const scrollContainer = document.querySelector(MAIN_SCROLL_SELECTOR);
    scrollContainer?.scrollTo({ top: 0, left: 0, behavior: "auto" });

    if (document.scrollingElement !== scrollContainer) {
      document.scrollingElement?.scrollTo({
        top: 0,
        left: 0,
        behavior: "auto",
      });
    }
  };

  const resetPageScroll = () => {
    if (pageScrollFrame) cancelAnimationFrame(pageScrollFrame);
    setPageScrollTop();
    pageScrollFrame = requestAnimationFrame(() => {
      pageScrollFrame = 0;
      setPageScrollTop();
    });
  };

  const pruneDetachedTargets = () => {
    revealTargets.forEach((element) => {
      if (!element.isConnected) {
        intersectionObserver?.unobserve(element);
        revealTargets.delete(element);
      }
    });
    tiltTargets.forEach((element) => {
      if (!element.isConnected) tiltTargets.delete(element);
    });
  };

  const discover = () => {
    discoveryFrame = 0;
    pruneDetachedTargets();

    const nextPage = PAGE_ROOTS.find(([, selector]) =>
      document.querySelector(selector),
    )?.[0];
    if (activePage && nextPage && nextPage !== activePage) {
      resetPageScroll();
    }
    if (nextPage && nextPage !== activePage) {
      activePage = nextPage;
      seenRevealIdentities.clear();
    }

    REVEAL_GROUPS.forEach((group) => {
      if (group.initialOnly && initialGroupsBound.has(group.selector)) return;
      const elements = document.querySelectorAll(group.selector);
      elements.forEach((element, index) => {
        bindReveal(element, group, index);
      });
      if (group.initialOnly && elements.length) {
        initialGroupsBound.add(group.selector);
      }
    });

    document.querySelectorAll(TILT_SELECTOR).forEach(bindTilt);
    discoverPortfolioTabs();
    autobiographyTimeline = document.querySelector(
      ".st-key-autobiography_timeline",
    );
    if (reducedMotion.matches) {
      autobiographyTimeline?.style.setProperty("--motion-scroll-progress", "1");
    } else {
      scheduleScrollProgress();
    }
    requestAnimationFrame(() => {
      document.documentElement.classList.add("portfolio-motion-ready");
    });
  };

  const scheduleDiscovery = () => {
    if (!discoveryFrame) discoveryFrame = requestAnimationFrame(discover);
  };

  const mutationRoot = document.querySelector(ROOT_SELECTOR) ?? document.body;
  const mutationObserver = new MutationObserver(scheduleDiscovery);

  const handleMotionPreference = () => {
    if (reducedMotion.matches) {
      revealTargets.forEach(reveal);
      tiltTargets.forEach(resetTilt);
      autobiographyTimeline?.style.setProperty("--motion-scroll-progress", "1");
    } else {
      scheduleScrollProgress();
    }
  };

  const handleFocus = (event) => {
    const pendingTarget = event.target?.closest?.(
      '[data-motion-state="pending"]',
    );
    if (pendingTarget) reveal(pendingTarget);
  };

  const mount = () => {
    mutationObserver.observe(mutationRoot, {
      attributes: true,
      attributeFilter: ["aria-selected"],
      childList: true,
      subtree: true,
    });
    window.addEventListener("scroll", scheduleScrollProgress, {
      signal,
      passive: true,
    });
    document
      .querySelector(MAIN_SCROLL_SELECTOR)
      ?.addEventListener("scroll", scheduleScrollProgress, {
        signal,
        passive: true,
      });
    window.addEventListener("resize", scheduleScrollProgress, {
      signal,
      passive: true,
    });
    document.addEventListener("focusin", handleFocus, { signal });
    reducedMotion.addEventListener("change", handleMotionPreference, { signal });
    finePointer.addEventListener(
      "change",
      () => {
        if (!finePointer.matches) tiltTargets.forEach(resetTilt);
      },
      { signal },
    );
    discover();
  };

  const refresh = () => scheduleDiscovery();

  const destroy = () => {
    if (destroyed) return;
    destroyed = true;
    abortController.abort();
    mutationObserver.disconnect();
    intersectionObserver?.disconnect();
    if (discoveryFrame) cancelAnimationFrame(discoveryFrame);
    if (pageScrollFrame) cancelAnimationFrame(pageScrollFrame);
    if (scrollFrame) cancelAnimationFrame(scrollFrame);
    liveAnimations.forEach((animation) => animation.cancel());
    liveAnimations.clear();

    revealTargets.forEach((element) => {
      element.removeAttribute("data-motion");
      element.removeAttribute("data-motion-state");
      element.removeAttribute("data-motion-bound");
      element.removeAttribute("data-motion-identity");
      element.style.removeProperty("--motion-delay");
      element.style.removeProperty("--motion-x");
    });
    tiltTargets.forEach((element) => {
      resetTilt(element);
      element.classList.remove("motion-tilt-target");
      element.removeAttribute("data-motion-tilt-bound");
    });
    autobiographyTimeline?.style.removeProperty("--motion-scroll-progress");
    document.documentElement.classList.remove("portfolio-motion-ready");
  };

  return {
    version: ENGINE_VERSION,
    get destroyed() {
      return destroyed;
    },
    mount,
    refresh,
    destroy,
  };
}

export default function portfolioMotionRuntime() {
  let engine = window[ENGINE_KEY];

  if (!engine || engine.destroyed || engine.version !== ENGINE_VERSION) {
    engine?.destroy?.();
    engine = createMotionEngine();
    window[ENGINE_KEY] = engine;
    engine.mount();
  } else {
    engine.refresh();
  }

  return () => {
    if (window[ENGINE_KEY] === engine) {
      engine.destroy();
      delete window[ENGINE_KEY];
    }
  };
}
