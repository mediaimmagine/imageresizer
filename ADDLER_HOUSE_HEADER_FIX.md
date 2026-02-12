# Addler House – Header menu fix (blog / non-home pages)

**Site:** https://www.sandbox-ah.mediaimmagine.it/  
**Theme:** Homey (child: Homey Child)  
**Issue:** On the blog and other non-home pages, the header menu ribbon was transparent and the menu text was white, so it was unreadable. On the homepage the header had a white background and dark text.

---

## Cause

- The **Homey** theme adds the class **`transparent-header`** to the header wrapper (`.nav-area`) on **non-home pages** (e.g. blog, archive, single).
- On those pages the header (and its parent) get:
  - **Transparent background** → menu bar invisible over content.
  - **White nav link color** → intended for a dark/overlay background.
- On the **homepage** the theme does *not* add `transparent-header`, so the header keeps a **white background** and **dark grey** nav text (`#4f5962`), which is readable.

---

## Fix (Custom CSS)

Add the following in **Appearance → Customize → Additional CSS** (or in the child theme).

### 1. Solid white header on blog and non-home pages

```css
/* Solid white header on blog and other non-home pages (Homey transparent-header fix) */
body.blog .transparent-header .header-nav,
body.archive .transparent-header .header-nav,
body.single .transparent-header .header-nav,
.transparent-header .nav-area {
	background-color: #ffffff !important;
}
.transparent-header .header-nav {
	background-color: #ffffff !important;
}
```

### 2. Menu text visible (same as homepage)

```css
/* Menu text visible on white ribbon (same as homepage) */
.transparent-header .header-nav .navi a,
.transparent-header .header-nav nav a {
	color: #4f5962 !important;
}
.transparent-header .header-nav .navi a:hover,
.transparent-header .header-nav nav a:hover {
	color: #3a2620 !important;
}
.transparent-header .header-nav a img {
	opacity: 1;
	filter: none;
}
```

- **`#4f5962`** = nav link color (matches homepage).
- **`#3a2620`** = hover color (aligned with site’s dark brown, e.g. Polylang select).

---

## Technical details

| Page type | Body class   | Header wrapper        | Header background | Nav link color |
|----------|--------------|------------------------|-------------------|----------------|
| Home     | `home`       | `.nav-area` (no transparent) | White             | `#4f5962`      |
| Blog     | `blog`       | `.nav-area.transparent-header` | Was transparent   | Was white      |

After the fix, blog and other non-home pages use the same white header ribbon and dark menu text as the homepage.

---

## Where to add the CSS

- **WordPress:** Appearance → Customize → Additional CSS  
- **Child theme:** in `style.css` or a custom CSS file enqueued in the child theme.

Clear any caching (theme/plugin/CDN) after saving.

---

*Documented: February 2025*

---

# Ciaobooking widget – Number of guests / Children empty (footer)

**Page:** https://www.sandbox-ah.mediaimmagine.it/our-accommodations/  
**Widgets:** Two Ciaobooking widgets in the footer (Veneto, Sicilia). Arrival/Departure date fields work; "Number of guests" and "Children" spinbuttons show the box and arrows but the value is invisible.

---

## Cause

Theme (Homey) or global footer CSS forces **white text** and **white background** on inputs inside the footer. The Ciaobooking spinbutton inputs (`input[name="guests"]`, `input[name="children"]`) sit inside `.cb-input-wrapper` and inherit that styling, so the numbers are **white on white** and appear as an empty box.

---

## Fix (Custom CSS)

Add in **Appearance → Customize → Additional CSS** (together with the header fix):

Footer rules must be **scoped to the Ciaobooking widget only** so Contact Us and Newsletter keep the theme’s (light) text. Use the class **`.widget_native_ciaobooking_widget`**:

```css
/* Footer: only Ciaobooking widgets (Veneto / Sicilia) – Contact Us & Newsletter unchanged */
footer .widget_native_ciaobooking_widget,
[role="contentinfo"] .widget_native_ciaobooking_widget {
	color: #3a2620 !important;
}
footer .widget_native_ciaobooking_widget .cb-input-wrapper input[type="number"],
[role="contentinfo"] .widget_native_ciaobooking_widget .cb-input-wrapper input[type="number"] {
	color: #3a2620 !important;
	background-color: #ffffff !important;
}
```

- **`.widget_native_ciaobooking_widget`** = Ciaobooking widget container (Veneto, Sicilia). Other footer widgets (Contact Us, Newsletter) are not matched, so their text stays as per theme.
- **`#3a2620`** = dark brown; **`#ffffff`** = input background.

Full coherent CSS is in **`ADDLER_HOUSE_CUSTOM_CSS.css`** in this repo.

---

*Ciaobooking widget fix documented: February 2025*
