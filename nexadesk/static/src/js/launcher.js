/** @odoo-module **/

/**
 * NexaDesk — Home Launcher for Odoo
 *
 * Modules:
 *   Constellation   canvas particle background
 *   HotKeys         keyboard navigation
 *   HomeLauncher    OWL component
 *   LauncherShell   action wrapper
 *   homeLauncherService  registered service
 *   WebClient / NavBar patches
 */

import { registry }                   from "@web/core/registry";
import { useService }                  from "@web/core/utils/hooks";
import { patch }                       from "@web/core/utils/patch";
import { NavBar }                      from "@web/webclient/navbar/navbar";
import { WebClient }                   from "@web/webclient/webclient";
import { computeAppsAndMenuItems }     from "@web/webclient/menus/menu_helpers";
import { Mutex }                       from "@web/core/utils/concurrency";
import { ControllerNotFoundError,
         standardActionServiceProps }  from "@web/webclient/actions/action_service";
import { Component, useState, useRef,
         onMounted, onWillUnmount,
         onWillUpdateProps, xml }      from "@odoo/owl";


// ─────────────────────────────────────────────────────────────────
//  CONSTELLATION  — animated canvas background
// ─────────────────────────────────────────────────────────────────
class Constellation {
    constructor(el) {
        this._el    = el;
        this._ctx   = el.getContext("2d");
        this._nodes = [];
        this._timer = null;
        this._fit();
        this._populate();
    }

    _fit() {
        this._el.width  = window.innerWidth;
        this._el.height = window.innerHeight;
    }

    _populate() {
        const qty = Math.round((this._el.width * this._el.height) / 10000);
        this._nodes = Array.from({ length: qty }, () => ({
            x:  Math.random() * this._el.width,
            y:  Math.random() * this._el.height,
            dx: (Math.random() - .5) * .25,
            dy: (Math.random() - .5) * .25,
            radius: Math.random() * 1.6 + .3,
            alpha:  Math.random() * .55 + .1,
        }));
    }

    _frame() {
        const W = this._el.width, H = this._el.height;
        this._ctx.clearRect(0, 0, W, H);

        for (const n of this._nodes) {
            this._ctx.beginPath();
            this._ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
            this._ctx.fillStyle = `rgba(255,255,255,${n.alpha})`;
            this._ctx.fill();
            n.x = (n.x + n.dx + W) % W;
            n.y = (n.y + n.dy + H) % H;
        }

        for (let a = 0; a < this._nodes.length; a++) {
            for (let b = a + 1; b < this._nodes.length; b++) {
                const nx = this._nodes[a].x - this._nodes[b].x;
                const ny = this._nodes[a].y - this._nodes[b].y;
                const sq = nx * nx + ny * ny;
                if (sq > 8000) continue;
                this._ctx.beginPath();
                this._ctx.moveTo(this._nodes[a].x, this._nodes[a].y);
                this._ctx.lineTo(this._nodes[b].x, this._nodes[b].y);
                this._ctx.strokeStyle = `rgba(255,255,255,${.06 * (1 - sq / 8000)})`;
                this._ctx.lineWidth = .4;
                this._ctx.stroke();
            }
        }

        this._timer = requestAnimationFrame(() => this._frame());
    }

    refit()  { this._fit(); }
    start()  { this._timer = requestAnimationFrame(() => this._frame()); }
    stop()   { cancelAnimationFrame(this._timer); }
}



// ─────────────────────────────────────────────────────────────────
//  HOTKEYS  — keyboard navigation handler
// ─────────────────────────────────────────────────────────────────
class HotKeys {
    constructor() {
        this._routes  = new Map();
        this._handler = (evt) => {
            const chord  = (evt.shiftKey && evt.key !== "Shift" ? "Shift+" : "") + evt.key;
            const action = this._routes.get(chord) ?? this._routes.get(evt.key);
            if (action) { evt.preventDefault(); action(evt); }
        };
    }

    register(chord, fn) { this._routes.set(chord, fn); return this; }
    activate(el)        { el.addEventListener("keydown", this._handler); }
    deactivate(el)      { el.removeEventListener("keydown", this._handler); }
}


// ─────────────────────────────────────────────────────────────────
//  HOME LAUNCHER  — main OWL component
// ─────────────────────────────────────────────────────────────────
export class HomeLauncher extends Component {
    static template = "nexadesk.HomeLauncher";
    static props    = {
        apps:    { type: Array, default: () => [] },
        onClose: Function,
    };

    setup() {
        this._menu      = useService("menu");
        this._cmd       = useService("command");
        this._ui        = useService("ui");

        this._sky         = null;
        this._keys        = new HotKeys();
        this._composing   = false;
        this._resizeGuard = null;

        // relying on the undocumented this.render(true) internal API.
        this._state = useState({ cursor: -1});

        this._wrapRef  = useRef("wrap");
        this._skyRef   = useRef("sky");
        this._queryRef = useRef("query");
        this._gridRef  = useRef("grid");

        // Bind every method used as a callback or event handler.
        // In OWL 2 / strict-mode modules, methods passed to setTimeout
        // or called via template event expressions lose their receiver —
        // binding in setup() guarantees 'this' is always the component.
        this.openApp  = this.openApp.bind(this);
        this._doOpen  = this._doOpen.bind(this);

        onWillUpdateProps(() => { this._state.cursor = -1; });

        onMounted(() => {
            this._sky = new Constellation(this._skyRef.el);
            this._sky.start();

            this._resizeGuard = () => this._sky?.refit();
            window.addEventListener("resize", this._resizeGuard);

            this._registerHotkeys();
            this._keys.activate(this._wrapRef.el);
            this._queryRef.el?.focus({ preventScroll: true });
        });

        onWillUnmount(() => {
            this._sky?.stop();
            this._keys.deactivate(this._wrapRef.el);
            window.removeEventListener("resize", this._resizeGuard);
        });
    }

    // ── Keyboard ────────────────────────────────────────────────
    _registerHotkeys() {
        const move = (delta) => () => this._shiftCursor(delta);
        const cols = () => {
            const w = window.innerWidth;
            if (w < 576)  return 3;
            if (w < 900)  return 4;
            if (w < 1200) return 5;
            return 6;
        };

        this._keys
            .register("Escape",     () => this.props.onClose())
            .register("Enter",      () => { const a = this.apps[this._state.cursor]; if (a) this._doOpen(a); })
            .register("ArrowRight", move(+1))
            .register("ArrowLeft",  move(-1))
            .register("ArrowDown",  () => this._shiftCursor(+cols()))
            .register("ArrowUp",    () => this._shiftCursor(-cols()))
            .register("Tab",        move(+1))
            .register("Shift+Tab",  move(-1));
    }

    _shiftCursor(delta) {
        const total = this.apps.length;
        if (!total) return;
        const cur  = this._state.cursor;
        const next = cur < 0
            ? (delta > 0 ? 0 : total - 1)
            : ((cur + delta + total * 99) % total);
        this._state.cursor = next;
        setTimeout(() => {
            this._gridRef.el
                ?.querySelectorAll(".fsl_tile")[next]
                ?.scrollIntoView({ block: "nearest", behavior: "smooth" });
        }, 10);
    }

    // ── Getters ─────────────────────────────────────────────────
    get apps()    { return this.props.apps || []; }
    get cursor()  { return this._state.cursor; }

    // ── Handlers ────────────────────────────────────────────────
    async _doOpen(app) {
        console.log(app)
        // this.props.onClose();
        await this._menu.selectMenu(app);
    }

    dismiss() { this.props.onClose(); }

    onQueryInput() {
        const raw  = this._queryRef.el?.value?.trim() ?? "";
        const term = this._composing ? "/" : `/${raw}`;
        this._composing = false;
        this._cmd.openMainPalette({ searchValue: term }, () => {
            this._queryRef.el?.focus();
            if (this._queryRef.el) this._queryRef.el.value = "";
        });
    }

    onQueryBlur() {
        setTimeout(() => {
            if (document.activeElement === document.body &&
                this._ui.activeElement === document) {
                this._queryRef.el?.focus();
            }
        }, 0);
    }

    onCompositionBegin() { this._composing = true; }

    // Bound in setup() — safe to use in template and setTimeout
    openApp(evt, app) {
        console.log("**********************************")
        const tile = evt.currentTarget;
        const glow = tile.querySelector(".fsl_tile_glow");
        if (glow) {
            const box = tile.getBoundingClientRect();
            glow.style.cssText =
                `left:${evt.clientX - box.left}px;` +
                `top:${evt.clientY - box.top}px;` +
                `opacity:1;transform:scale(4)`;
            setTimeout(() => {
                glow.style.opacity   = "0";
                glow.style.transform = "scale(0)";
            }, 400);
        }
        setTimeout(() => this._doOpen(app), 160);
    }

 
}


// ─────────────────────────────────────────────────────────────────
//  SERVICE
// ─────────────────────────────────────────────────────────────────
export const homeLauncherService = {
    dependencies: ["action", "menu"],

    start(env) {
        const lock    = new Mutex();
        let   showing = false;

        // ── Shell component — gives HomeLauncher access to the full
        //    OWL template environment where QWeb templates are registered.
        class LauncherShell extends Component {
            static components = { HomeLauncher };
            static target     = "current";
            static props      = { ...standardActionServiceProps };
            static template   = xml`
                <HomeLauncher
                    apps="state.apps"
                    onClose="() => this.handleClose()"
                />`;

            setup() {
                const menuSvc = useService("menu");
                const tree    = menuSvc.getMenuAsTree("root");
                const apps    = (tree ? computeAppsAndMenuItems(tree).apps : null) || [];
                this.state    = useState({ apps });

                onMounted(() => {
                    showing = true;
                    document.body.classList.add("fsl_open");
                    env.bus.trigger("HOME_LAUNCHER:OPEN");
                });
                onWillUnmount(() => {
                    showing = false;
                    document.body.classList.remove("fsl_open");
                    env.bus.trigger("HOME_LAUNCHER:CLOSE");
                });
            }

            handleClose() { close(); }
        }

        registry.category("actions").add("nexadesk_home", LauncherShell, { force: true });

        async function open() {
            return lock.exec(async () => {
                if (showing) return;
                // clearBreadcrumbs: true — prevents Odoo from restoring the
                // previous controller (e.g. CRM) when the launcher re-opens
                // after the user navigated away. Without this, clicking a
                // second app always opens the first one instead.
                await env.services.action.doAction("nexadesk_home", {
                    clearBreadcrumbs: true,
                });
            });
        }

        async function close() {
            return lock.exec(async () => {
                if (!showing) return;
                try {
                    await env.services.action.restore();
                } catch (e) {
                    if (!(e instanceof ControllerNotFoundError)) throw e;
                }
            });
        }

        return {
            open,
            close,
            toggle:  () => (showing ? close() : open()),
            get isOpen() { return showing; },
        };
    },
};

registry.category("services").add("homeLauncher", homeLauncherService);


// ─────────────────────────────────────────────────────────────────
//  WEBCLIENT PATCH  — open launcher on boot
// ─────────────────────────────────────────────────────────────────
patch(WebClient.prototype, {
    setup() {
        super.setup();
        this._launcher = useService("homeLauncher");
    },
    _loadDefaultApp() {
        return this._launcher.open();
    },
});


// ─────────────────────────────────────────────────────────────────
//  NAVBAR PATCH  — grid button in the top bar
// ─────────────────────────────────────────────────────────────────
patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.homeLauncher = useService("homeLauncher");
    },
    toggleHomeLauncher() {
        this.homeLauncher.toggle();
    },
});
