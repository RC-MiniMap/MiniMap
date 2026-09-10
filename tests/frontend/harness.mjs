import { readFileSync } from "node:fs";
import { existsSync } from "node:fs";
import { resolve, dirname, isAbsolute } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const FRONTEND_DIR = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(FRONTEND_DIR, "../..");
const SCRIPT_PATHS = Object.freeze({
  directions: resolve(PROJECT_ROOT, "app/static/js/directions.js"),
  map: resolve(PROJECT_ROOT, "app/static/js/map.js"),
});

function createEventTarget() {
  const listeners = new Map();

  return {
    addEventListener(type, listener) {
      const callbacks = listeners.get(type) ?? [];
      callbacks.push(listener);
      listeners.set(type, callbacks);
    },

    removeEventListener(type, listener) {
      const callbacks = listeners.get(type) ?? [];
      listeners.set(
        type,
        callbacks.filter((callback) => callback !== listener),
      );
    },

    dispatchEvent(eventOrType) {
      const event =
        typeof eventOrType === "string"
          ? { type: eventOrType }
          : { ...eventOrType };
      if (!event.type) {
        throw new TypeError("Events must have a type");
      }

      const callbacks = [...(listeners.get(event.type) ?? [])];
      for (const callback of callbacks) {
        callback(event);
      }
      return true;
    },

    listenerCount(type) {
      return (listeners.get(type) ?? []).length;
    },
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

class FakeElement {
  constructor(ownerDocument, tagName) {
    this.ownerDocument = ownerDocument;
    this.tagName = tagName.toUpperCase();
    this.children = [];
    this.parentNode = null;
    this.style = {};
    this.className = "";
    this.eventListeners = new Map();
    this._id = "";
    this._innerHTML = "";
    this._textContent = "";
  }

  get id() {
    return this._id;
  }

  set id(value) {
    this.ownerDocument.unregisterId(this);
    this._id = String(value);
    this.ownerDocument.registerId(this);
  }

  get innerHTML() {
    return this._innerHTML;
  }

  get outerHTML() {
    const attributes = [
      this.id && ` id="${this.id}"`,
      this.className && ` class="${this.className}"`,
    ]
      .filter(Boolean)
      .join("");
    const content = this._innerHTML || escapeHtml(this._textContent);
    return `<${this.tagName.toLowerCase()}${attributes}>${content}</${this.tagName.toLowerCase()}>`;
  }

  set innerHTML(value) {
    this.clearChildren();
    this._innerHTML = String(value);
    this._textContent = "";

    // This deliberately small parser gives every opening tag a fake node and
    // preserves ids/classes needed by tests without pretending to be a browser.
    const openingTags = /<([a-z][\w-]*)\b([^>]*)>/gi;
    for (const match of this._innerHTML.matchAll(openingTags)) {
      const tagName = match[1];
      const child = this.ownerDocument.createElement(tagName);
      const id = match[2].match(/\bid=["']([^"']+)["']/i)?.[1];
      const className = match[2].match(/\bclass=["']([^"']+)["']/i)?.[1];
      const text = new RegExp(
        `<${tagName}\\b[^>]*>([^<]*)</${tagName}>`,
        "i",
      ).exec(this._innerHTML.slice(match.index))?.[1];
      if (id) child.id = id;
      if (className) child.className = className;
      if (text?.trim()) child.textContent = text.trim();
      this.appendChild(child);
    }
  }

  get textContent() {
    if (this._textContent) return this._textContent;
    return this._innerHTML.replace(/<[^>]*>/g, "").trim();
  }

  set textContent(value) {
    this.clearChildren();
    this._innerHTML = "";
    this._textContent = String(value);
  }

  appendChild(child) {
    if (child.parentNode) {
      child.parentNode.removeChild(child);
    }
    child.parentNode = this;
    this.children.push(child);
    this.ownerDocument.registerTree(child);
    this._innerHTML = this.children
      .map((element) => element.outerHTML)
      .join("");
    return child;
  }

  removeChild(child) {
    const index = this.children.indexOf(child);
    if (index === -1) return child;
    this.children.splice(index, 1);
    this.ownerDocument.unregisterTree(child);
    child.parentNode = null;
    this._innerHTML = this.children
      .map((element) => element.outerHTML)
      .join("");
    return child;
  }

  clearChildren() {
    for (const child of [...this.children]) {
      this.removeChild(child);
    }
  }

  replaceChildren(...children) {
    this.clearChildren();
    for (const child of children) this.appendChild(child);
  }

  addEventListener(type, listener) {
    const callbacks = this.eventListeners.get(type) ?? [];
    callbacks.push(listener);
    this.eventListeners.set(type, callbacks);
  }

  removeEventListener(type, listener) {
    const callbacks = this.eventListeners.get(type) ?? [];
    this.eventListeners.set(
      type,
      callbacks.filter((callback) => callback !== listener),
    );
  }

  dispatchEvent(eventOrType) {
    const event =
      typeof eventOrType === "string"
        ? { type: eventOrType }
        : { ...eventOrType };
    if (!event.type) {
      throw new TypeError("Events must have a type");
    }
    event.target ??= this;
    event.currentTarget = this;

    for (const callback of [...(this.eventListeners.get(event.type) ?? [])]) {
      callback(event);
    }
    return true;
  }

  click() {
    return this.dispatchEvent({ type: "click" });
  }

  querySelector(selector) {
    if (selector.startsWith("#")) {
      return this.ownerDocument.getElementById(selector.slice(1));
    }
    if (selector.startsWith(".")) {
      return this.find((element) =>
        element.className.split(/\s+/).includes(selector.slice(1)),
      );
    }
    return this.find(
      (element) => element.tagName.toLowerCase() === selector.toLowerCase(),
    );
  }

  find(predicate) {
    for (const child of this.children) {
      if (predicate(child)) return child;
      const match = child.find(predicate);
      if (match) return match;
    }
    return null;
  }
}

class FakeDocument {
  constructor() {
    this.createdElements = [];
    this.elements = [];
    this.elementsById = new Map();
    this.events = createEventTarget();
    this.defaultView = null;
  }

  createElement(tagName) {
    const element = new FakeElement(this, tagName);
    this.createdElements.push(element);
    this.elements.push(element);
    return element;
  }

  installElement(id, tagName = "div") {
    const element = new FakeElement(this, tagName);
    element.id = id;
    this.elements.push(element);
    return element;
  }

  getElementById(id) {
    return this.elementsById.get(id) ?? null;
  }

  addEventListener(...args) {
    return this.events.addEventListener(...args);
  }

  removeEventListener(...args) {
    return this.events.removeEventListener(...args);
  }

  dispatchEvent(...args) {
    return this.events.dispatchEvent(...args);
  }

  listenerCount(type) {
    return this.events.listenerCount(type);
  }

  registerId(element) {
    if (element.id) this.elementsById.set(element.id, element);
  }

  unregisterId(element) {
    if (element.id && this.elementsById.get(element.id) === element) {
      this.elementsById.delete(element.id);
    }
  }

  registerTree(element) {
    this.registerId(element);
    for (const child of element.children) this.registerTree(child);
  }

  unregisterTree(element) {
    this.unregisterId(element);
    for (const child of element.children) this.unregisterTree(child);
  }
}

function toHostValue(value) {
  if (Array.isArray(value)) return Array.from(value, toHostValue);
  if (value && typeof value === "object") {
    if (Object.getPrototypeOf(value) === Object.prototype) return value;
    return Object.fromEntries(
      Object.entries(value).map(([key, entry]) => [key, toHostValue(entry)]),
    );
  }
  return value;
}

function boundsForPoints(points) {
  const pointList = Array.isArray(points?.[0]) ? points : [points];
  const latitudes = pointList.map(([latitude]) => latitude);
  const longitudes = pointList.map(([, longitude]) => longitude);
  const south = Math.min(...latitudes);
  const west = Math.min(...longitudes);
  const north = Math.max(...latitudes);
  const east = Math.max(...longitudes);

  return {
    south,
    west,
    north,
    east,
    getSouthWest: () => [south, west],
    getNorthEast: () => [north, east],
    toArray: () => [
      [south, west],
      [north, east],
    ],
  };
}

function createLeafletRecorder() {
  const maps = [];
  const layers = [];

  function createLayer(type, points, options = {}) {
    const hostPoints = toHostValue(points);
    const layer = {
      type,
      points: hostPoints,
      latlngs: hostPoints,
      options: toHostValue(options),
      map: null,
      addTo(map) {
        this.map = map;
        map.layers.push(this);
        return this;
      },
    };

    if (type === "polyline") {
      layer.getBounds = () => boundsForPoints(hostPoints);
    }

    layers.push(layer);
    return layer;
  }

  const leaflet = {
    CRS: { Simple: Object.freeze({ name: "Simple" }) },

    map(container, options = {}) {
      const map = {
        container,
        options: toHostValue(options),
        layers: [],
        fitBoundsCalls: [],
        invalidateSizeCalls: 0,
        fitBounds(bounds, fitOptions) {
          this.fitBoundsCalls.push({
            bounds: Array.isArray(bounds) ? toHostValue(bounds) : bounds,
            options: toHostValue(fitOptions),
          });
          return this;
        },
        invalidateSize() {
          this.invalidateSizeCalls += 1;
          return this;
        },
      };
      maps.push(map);
      return map;
    },

    polyline(points, options) {
      return createLayer("polyline", points, options);
    },

    circleMarker(point, options) {
      return createLayer("circleMarker", point, options);
    },
  };

  return { leaflet, maps, layers };
}

function createConsoleRecorder() {
  const messages = { debug: [], info: [], log: [], warn: [], error: [] };
  const console = {};

  for (const method of Object.keys(messages)) {
    console[method] = (...args) => messages[method].push(args);
  }

  return { console, messages };
}

/**
 * Create an isolated browser-like runtime for the two classic frontend scripts.
 * The returned object exposes the fake DOM, window, Leaflet recorder, timers,
 * and event dispatch helpers used by frontend tests.
 */
export function createBrowserHarness({
  directionSteps,
  routeMap,
  windowProperties = {},
  globals = {},
} = {}) {
  const document = new FakeDocument();
  const directionsContainer = document.installElement(
    "directions-card-container",
  );
  const mapContainer = document.installElement("map");
  const window = createEventTarget();
  const { leaflet, maps, layers } = createLeafletRecorder();
  const { console, messages } = createConsoleRecorder();
  const timers = new Map();
  let nextTimerId = 1;

  Object.assign(window, {
    window,
    self: window,
    document,
    L: leaflet,
    ...windowProperties,
    ...globals,
  });
  if (directionSteps !== undefined) {
    window.directionSteps = directionSteps;
  }
  if (routeMap !== undefined) {
    window.routeMap = routeMap;
  }
  document.defaultView = window;

  function setTimeoutFake(callback, delay = 0, ...args) {
    const id = nextTimerId++;
    timers.set(id, { callback, delay, args });
    return id;
  }

  function clearTimeoutFake(id) {
    timers.delete(id);
  }

  function runTimers() {
    while (timers.size) {
      const [id, timer] = timers.entries().next().value;
      timers.delete(id);
      timer.callback(...timer.args);
    }
  }

  const context = vm.createContext({
    window,
    document,
    L: leaflet,
    console,
    setTimeout: setTimeoutFake,
    clearTimeout: clearTimeoutFake,
    ...windowProperties,
    ...globals,
  });
  if (directionSteps !== undefined) {
    context.directionSteps = directionSteps;
  }
  if (routeMap !== undefined) {
    context.routeMap = routeMap;
  }

  const harness = {
    isBrowserHarness: true,
    context,
    window,
    document,
    L: leaflet,
    leaflet,
    console,
    consoleMessages: messages,
    directionsContainer,
    mapContainer,
    maps,
    layers,
    timers,
    dispatchDOMContentLoaded() {
      document.dispatchEvent({ type: "DOMContentLoaded" });
      return harness;
    },
    dispatchWindowEvent(eventOrType) {
      window.dispatchEvent(eventOrType);
      return harness;
    },
    runTimers,
    flushTimers: runTimers,
    getElementById(id) {
      return document.getElementById(id);
    },
    getCreatedElements() {
      return [...document.createdElements];
    },
    getCreatedLayers() {
      return [...layers];
    },
  };

  return harness;
}

function isBrowserHarness(value) {
  return value?.isBrowserHarness === true;
}

function resolveScriptPath(scriptPath) {
  if (scriptPath instanceof URL) return fileURLToPath(scriptPath);

  const value = String(scriptPath);
  if (
    value === "directions" ||
    value === "directions.js" ||
    value.endsWith("/directions.js")
  ) {
    return SCRIPT_PATHS.directions;
  }
  if (value === "map" || value === "map.js" || value.endsWith("/map.js")) {
    return SCRIPT_PATHS.map;
  }

  const candidates = isAbsolute(value)
    ? [value]
    : [resolve(PROJECT_ROOT, value), resolve(FRONTEND_DIR, value)];
  const path = candidates.find((candidate) => existsSync(candidate));
  if (!path) {
    throw new Error(`Frontend script not found: ${scriptPath}`);
  }
  return path;
}

function prepareLoad(scriptOptions) {
  if (isBrowserHarness(scriptOptions)) {
    return { harness: scriptOptions, options: {} };
  }

  const options = scriptOptions ?? {};
  const harness =
    options.harness ??
    createBrowserHarness({
      directionSteps: options.directionSteps,
      routeMap: options.routeMap,
      windowProperties: options.windowProperties,
      globals: options.globals,
    });
  return { harness, options };
}

function applyGlobals(harness, options) {
  if (options.directionSteps !== undefined) {
    harness.window.directionSteps = options.directionSteps;
    harness.context.directionSteps = options.directionSteps;
  }
  if (options.routeMap !== undefined) {
    harness.window.routeMap = options.routeMap;
    harness.context.routeMap = options.routeMap;
  }
  for (const [name, value] of Object.entries(options.globals ?? {})) {
    harness.window[name] = value;
    harness.context[name] = value;
  }
}

/**
 * Evaluate a classic browser script in a fresh or supplied harness.
 * By default the DOMContentLoaded event and queued fake timers are drained.
 */
export function loadScript(scriptPath, scriptOptions = {}) {
  const { harness, options } = prepareLoad(scriptOptions);
  applyGlobals(harness, options);

  const resolvedPath = resolveScriptPath(scriptPath);
  const source = readFileSync(resolvedPath, "utf8");
  vm.runInContext(source, harness.context, { filename: resolvedPath });

  if (options.dispatchDOMContentLoaded !== false) {
    harness.dispatchDOMContentLoaded();
  }
  if (options.flushTimers !== false) {
    harness.runTimers();
  }
  return harness;
}

export function loadDirectionsScript(scriptOptions = {}) {
  return loadScript(SCRIPT_PATHS.directions, scriptOptions);
}

export function loadMapScript(scriptOptions = {}) {
  return loadScript(SCRIPT_PATHS.map, scriptOptions);
}

export function getCreatedElements(harness) {
  if (!isBrowserHarness(harness)) {
    throw new TypeError("getCreatedElements expects a browser harness");
  }
  return [...harness.document.createdElements];
}

export function getCreatedLayers(harness) {
  if (!isBrowserHarness(harness)) {
    throw new TypeError("getCreatedLayers expects a browser harness");
  }
  return [...harness.layers];
}

export function getMaps(harness) {
  if (!isBrowserHarness(harness)) {
    throw new TypeError("getMaps expects a browser harness");
  }
  return [...harness.maps];
}
