# MD-Book Styling Analysis & Recommendations

**Analysis Date:** 2025-11-13
**Source:** https://github.com/terraphim/md-book
**For:** Terraphim AI Website (terraphim.ai)

---

## Executive Summary

The **md-book** repository is a Rust-based documentation generator (mdBook alternative) with excellent CSS architecture and UX patterns. After analyzing the codebase, **several valuable concepts can be leveraged** to enhance the terraphim.ai website.

**Key Findings:**
- ✅ Superior CSS custom properties system for theming
- ✅ Innovative multi-column content layout for readability
- ✅ Right-hand table of contents for navigation
- ✅ Better code block handling with column-span
- ✅ Systematic responsive breakpoints
- ✅ Typography system with proper hierarchy

**Recommendation:** Adopt 5-7 specific patterns from md-book (detailed below)

---

## Current State Comparison

### Terraphim.ai (Current)

**Strengths:**
- ✅ Modern dark mode with CSS custom properties (recently implemented)
- ✅ Bulma CSS framework for rapid development
- ✅ Good accessibility features (skip links, ARIA labels)
- ✅ Performance optimizations (preconnect, caching)

**Opportunities:**
- ⚠️ Limited CSS custom properties (only in custom.scss)
- ⚠️ Single-column content layout
- ⚠️ No table of contents for long articles
- ⚠️ Basic code block styling
- ⚠️ Could improve content readability on wide screens

### MD-Book

**Strengths:**
- ✅ Comprehensive CSS custom properties system
- ✅ Three-column grid layout (sidebar, content, TOC)
- ✅ Multi-column article content for readability
- ✅ Sticky navigation elements
- ✅ Advanced code block handling
- ✅ Progressive responsive design

**Limitations:**
- ❌ No CSS framework (custom from scratch)
- ❌ Documentation-focused (not general purpose)
- ❌ Limited interactive features

---

## Valuable Concepts from MD-Book

### 1. ⭐ **Comprehensive CSS Custom Properties System**

**What MD-Book Does:**

```css
:root {
  /* Color palette */
  --sl-color-primary-50: #f0f0f0;
  --sl-color-primary-100: #e0e0e0;
  /* ... through 900 */

  /* Semantic colors */
  --theme-text: var(--neutral-900);
  --theme-bg: var(--neutral-0);
  --theme-bg-offset: var(--neutral-50);
  --theme-border: var(--neutral-200);

  /* Typography */
  --sl-font-weight-bold: 600;
  --sl-line-height: 1.6;

  /* Layout */
  --header-height: 4rem;
  --sidebar-width: 300px;
  --toc-width: 240px;
}
```

**Benefits:**
- Systematic color palette with semantic naming
- Easy theme customization
- Consistent spacing and sizing
- Better maintainability

**Recommendation for Terraphim.ai:**

**Priority:** 🟢 **HIGH** - Expand CSS variables

**Implementation:**

```scss
// Enhance sass/custom.scss with comprehensive variables

:root {
  // Color palette - full scale
  --neutral-0: #ffffff;
  --neutral-50: #f9fafb;
  --neutral-100: #f3f4f6;
  --neutral-200: #e5e7eb;
  --neutral-300: #d1d5db;
  --neutral-400: #9ca3af;
  --neutral-500: #6b7280;
  --neutral-600: #4b5563;
  --neutral-700: #374151;
  --neutral-800: #1f2937;
  --neutral-900: #111827;

  // Semantic colors (light theme)
  --color-text: var(--neutral-900);
  --color-text-secondary: var(--neutral-600);
  --color-bg: var(--neutral-0);
  --color-bg-secondary: var(--neutral-50);
  --color-border: var(--neutral-200);
  --color-accent: #00d1b2; // Terraphim brand color

  // Typography scale
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;

  // Spacing scale
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;

  // Layout dimensions
  --header-height: 4rem;
  --content-max-width: 1200px;
  --sidebar-width: 280px;
  --toc-width: 240px;
}

[theme="dark"] {
  --color-text: var(--neutral-50);
  --color-text-secondary: var(--neutral-300);
  --color-bg: var(--neutral-900);
  --color-bg-secondary: var(--neutral-800);
  --color-border: var(--neutral-700);
}
```

**Effort:** Medium (2-3 hours)
**Impact:** High (improved consistency and maintainability)

---

### 2. ⭐ **Multi-Column Article Layout**

**What MD-Book Does:**

```css
.main-article {
  column-width: 40ch; /* Optimal reading width */
  column-gap: 2rem;
  column-rule: 1px solid var(--theme-border);
}

/* Prevent elements from breaking across columns */
h1, h2, h3, h4, h5, h6 {
  column-span: all; /* Span across all columns */
  break-after: avoid;
}

pre, code, img {
  column-span: all; /* Prevent code blocks from wrapping */
}
```

**Benefits:**
- Better readability on wide screens (40-45 characters per line is optimal)
- Professional magazine-like layout
- Automatic content distribution
- Better use of horizontal space

**Recommendation for Terraphim.ai:**

**Priority:** 🟡 **MEDIUM** - Consider for blog posts/documentation

**Implementation:**

```scss
// Add to sass/custom.scss

// Multi-column layout for long-form content
.content-multicolumn {
  @media screen and (min-width: 1200px) {
    column-width: 40ch;
    column-gap: var(--space-2xl);
    column-rule: 1px solid var(--color-border);

    // Prevent awkward breaks
    h1, h2, h3, h4, h5, h6 {
      column-span: all;
      break-after: avoid;
    }

    // Keep code blocks together
    pre, .highlight {
      column-span: all;
      break-inside: avoid;
    }

    // Keep images together
    figure, img {
      break-inside: avoid;
    }

    // Lists should not break
    ul, ol {
      break-inside: avoid-column;
    }
  }
}
```

**Usage in templates:**
```html
<div class="content content-multicolumn">
  {{ page.content | safe }}
</div>
```

**Effort:** Low (1-2 hours)
**Impact:** Medium (improved readability for long articles)

---

### 3. ⭐⭐⭐ **Right-Hand Table of Contents**

**What MD-Book Does:**

```css
.grid-container {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar main toc"
    "footer footer footer";
  grid-template-columns: 300px minmax(0, 1fr) 240px;
  grid-template-rows: auto 1fr auto;
}

.toc {
  grid-area: toc;
  position: sticky;
  top: 0;
  max-height: 100vh;
  overflow-y: auto;
}

.toc ul {
  list-style: none;
  padding: 0;
}

.toc li.level-2 { padding-left: 1rem; }
.toc li.level-3 { padding-left: 2rem; }
```

**Benefits:**
- Easy navigation for long articles
- Sticky positioning keeps TOC visible while scrolling
- Better UX for documentation and blog posts
- Visual page structure overview

**Recommendation for Terraphim.ai:**

**Priority:** 🔴 **HIGHEST** - Excellent UX improvement

**Implementation:**

Create a new component for table of contents:

```scss
// Add to sass/custom.scss

.page-toc {
  position: sticky;
  top: calc(var(--header-height) + 1rem);
  max-height: calc(100vh - var(--header-height) - 2rem);
  overflow-y: auto;
  padding: var(--space-lg);
  background: var(--color-bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--color-border);

  h4 {
    font-size: var(--font-size-sm);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-text-secondary);
    margin-bottom: var(--space-md);
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li {
    margin-bottom: var(--space-sm);
  }

  a {
    color: var(--color-text-secondary);
    text-decoration: none;
    display: block;
    padding: var(--space-xs) var(--space-sm);
    border-radius: 4px;
    font-size: var(--font-size-sm);
    transition: all 0.2s ease;

    &:hover {
      background: var(--color-bg);
      color: var(--color-accent);
    }

    &.active {
      background: var(--color-accent);
      color: white;
      font-weight: 600;
    }
  }

  // Nested levels
  .toc-level-2 { padding-left: 0; }
  .toc-level-3 { padding-left: 1rem; }
  .toc-level-4 { padding-left: 2rem; }

  // Hide on smaller screens
  @media screen and (max-width: 1200px) {
    display: none;
  }
}

// Layout grid with TOC
.page-with-toc {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 240px;
  gap: var(--space-2xl);

  @media screen and (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}
```

**JavaScript for active state:**

```javascript
// Add to static/js/site.js or create new file

function initTableOfContents() {
  const tocLinks = document.querySelectorAll('.page-toc a');
  const headings = document.querySelectorAll('h2[id], h3[id], h4[id]');

  if (!tocLinks.length || !headings.length) return;

  // Intersection Observer for active state
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        tocLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }, {
    rootMargin: '-100px 0px -80% 0px'
  });

  headings.forEach(heading => observer.observe(heading));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initTableOfContents);
```

**Template structure:**

```html
<div class="page-with-toc">
  <article class="content">
    {{ page.content | safe }}
  </article>

  {% if page.toc %}
  <aside class="page-toc">
    <h4>On This Page</h4>
    <ul>
      {% for heading in page.toc %}
      <li class="toc-level-{{ heading.level }}">
        <a href="#{{ heading.id }}">{{ heading.title }}</a>
      </li>
      {% endfor %}
    </ul>
  </aside>
  {% endif %}
</div>
```

**Effort:** Medium (4-5 hours including JavaScript)
**Impact:** Very High (major UX improvement for documentation)

---

### 4. ⭐ **Better Code Block Styling**

**What MD-Book Does:**

```css
pre {
  column-span: all; /* Prevent wrapping in multi-column layout */
  overflow-x: auto;
  background: var(--theme-bg-offset);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--theme-border);
}

code {
  white-space: pre !important;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

/* Inline code */
p code {
  white-space: nowrap;
  padding: 0.2em 0.4em;
  background: var(--theme-bg-offset);
  border-radius: 3px;
  border: 1px solid var(--theme-border);
}
```

**Benefits:**
- Better horizontal scrolling for long code
- Prevents awkward column breaks
- Clear visual distinction between inline and block code
- Proper whitespace preservation

**Recommendation for Terraphim.ai:**

**Priority:** 🟢 **HIGH** - Improves developer content

**Implementation:**

```scss
// Enhance code blocks in sass/custom.scss

pre {
  background: var(--code-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: var(--space-lg);
  overflow-x: auto;
  margin: var(--space-lg) 0;
  box-shadow: 0 2px 4px var(--shadow);

  // Prevent column breaks if multi-column is used
  column-span: all;
  break-inside: avoid;

  code {
    background: transparent;
    border: none;
    padding: 0;
    font-size: 0.9em;
    line-height: 1.5;
    white-space: pre !important;
    display: block;
  }
}

// Inline code
:not(pre) > code {
  background: var(--code-bg);
  border: 1px solid var(--border-color);
  border-radius: 3px;
  padding: 0.2em 0.4em;
  font-size: 0.9em;
  white-space: nowrap;
  font-family: var(--font-family-mono);
}

// Copy button for code blocks
.code-block-wrapper {
  position: relative;

  .copy-button {
    position: absolute;
    top: var(--space-sm);
    right: var(--space-sm);
    padding: var(--space-xs) var(--space-sm);
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: var(--font-size-xs);
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease;

    &:hover {
      background: var(--color-accent);
      color: white;
      border-color: var(--color-accent);
    }
  }

  &:hover .copy-button {
    opacity: 1;
  }
}
```

**Effort:** Low (1-2 hours)
**Impact:** Medium (better developer experience)

---

### 5. ⭐ **Responsive Breakpoint Strategy**

**What MD-Book Does:**

```css
/* Progressive enhancement approach */

/* Large screens (default) */
.grid-container {
  grid-template-columns: 300px minmax(0, 1fr) 240px;
}

/* Medium screens - remove TOC */
@media screen and (max-width: 1200px) {
  .grid-container {
    grid-template-columns: 300px minmax(0, 1fr);
  }
  .toc { display: none; }
  .main-article { column-count: 1; }
}

/* Small screens - remove sidebar */
@media screen and (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
  }
  .sidebar { display: none; }
}

/* Mobile */
@media screen and (max-width: 640px) {
  /* Stack navigation, reduce padding */
}
```

**Benefits:**
- Clear breakpoint hierarchy
- Progressive enhancement
- Maintains functionality at all sizes
- Logical feature removal on smaller screens

**Recommendation for Terraphim.ai:**

**Priority:** 🟢 **HIGH** - Standardize breakpoints

**Implementation:**

```scss
// Add to sass/custom.scss - standardize breakpoints

// Breakpoint variables
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1200px;
  --breakpoint-2xl: 1400px;
}

// Breakpoint mixins (if using Sass)
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'mobile' {
    @media screen and (max-width: 640px) { @content; }
  }
  @else if $breakpoint == 'tablet' {
    @media screen and (max-width: 768px) { @content; }
  }
  @else if $breakpoint == 'desktop' {
    @media screen and (max-width: 1024px) { @content; }
  }
  @else if $breakpoint == 'wide' {
    @media screen and (max-width: 1200px) { @content; }
  }
}

// Usage example
.container {
  max-width: var(--content-max-width);
  padding: 0 var(--space-xl);

  @include respond-to('tablet') {
    padding: 0 var(--space-md);
  }

  @include respond-to('mobile') {
    padding: 0 var(--space-sm);
  }
}
```

**Effort:** Low (1 hour)
**Impact:** Medium (improved consistency)

---

### 6. ⭐ **Typography Hierarchy System**

**What MD-Book Does:**

```css
h1 { font-size: 2.5rem; line-height: 1.2; }
h2 { font-size: 2rem; line-height: 1.3; }
h3 { font-size: 1.75rem; line-height: 1.4; }
h4 { font-size: 1.5rem; line-height: 1.4; }
h5 { font-size: 1.25rem; line-height: 1.5; }
h6 { font-size: 1rem; line-height: 1.5; }

/* Consistent spacing */
h1, h2, h3, h4, h5, h6 {
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  font-weight: var(--sl-font-weight-bold);
}

h1:first-child,
h2:first-child,
h3:first-child { margin-top: 0; }
```

**Benefits:**
- Clear visual hierarchy
- Consistent spacing
- Better readability
- Systematic scaling

**Recommendation for Terraphim.ai:**

**Priority:** 🟡 **MEDIUM** - Already decent with Bulma, but can enhance

**Implementation:**

```scss
// Enhance typography in sass/custom.scss

.content {
  // Typography scale
  h1 {
    font-size: var(--font-size-4xl);
    line-height: 1.2;
    margin-top: var(--space-2xl);
    margin-bottom: var(--space-lg);
  }

  h2 {
    font-size: var(--font-size-3xl);
    line-height: 1.3;
    margin-top: var(--space-xl);
    margin-bottom: var(--space-md);
  }

  h3 {
    font-size: var(--font-size-2xl);
    line-height: 1.4;
    margin-top: var(--space-lg);
    margin-bottom: var(--space-md);
  }

  // First heading has no top margin
  h1:first-child,
  h2:first-child,
  h3:first-child {
    margin-top: 0;
  }

  // Paragraphs
  p {
    line-height: 1.7;
    margin-bottom: var(--space-md);
    max-width: 70ch; // Optimal reading width
  }

  // Lists
  ul, ol {
    line-height: 1.7;
    margin-bottom: var(--space-md);
    padding-left: var(--space-xl);
  }

  li {
    margin-bottom: var(--space-sm);
  }
}
```

**Effort:** Low (1 hour)
**Impact:** Medium (improved readability)

---

### 7. **Three-Column Grid Layout**

**What MD-Book Does:**

```css
.grid-container {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar main toc"
    "footer footer footer";
  grid-template-columns: 300px minmax(0, 1fr) 240px;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}

.sidebar {
  grid-area: sidebar;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.main-content {
  grid-area: main;
  padding: 2rem;
}

.toc {
  grid-area: toc;
  position: sticky;
  top: 0;
  height: 100vh;
}
```

**Benefits:**
- Sidebar navigation always accessible
- Main content gets priority
- TOC for quick navigation
- Sticky elements stay visible

**Recommendation for Terraphim.ai:**

**Priority:** 🟡 **MEDIUM-LOW** - Only if adding sidebar navigation

**Current State:** Terraphim.ai uses top navigation (navbar), which is already good for a blog/marketing site. Three-column layout is more suited for documentation sites.

**When to Consider:**
- If adding a documentation section
- If content becomes more hierarchical
- If users need persistent navigation

**Effort:** High (8-10 hours including restructuring)
**Impact:** Medium (depends on content type)

---

## Implementation Priorities

### Phase 1: Quick Wins (1 week)

**High Priority, Low Effort:**

1. ✅ **Expand CSS Custom Properties** (2-3 hours)
   - Full color palette (50-900 scale)
   - Typography scale
   - Spacing scale
   - Semantic color tokens

2. ✅ **Better Code Block Styling** (1-2 hours)
   - Enhanced pre/code styling
   - Column-span for multi-column compatibility
   - Copy button (optional)

3. ✅ **Standardize Responsive Breakpoints** (1 hour)
   - Define breakpoint variables
   - Create mixins/utilities
   - Document usage

**Total Time:** ~5 hours
**Impact:** High (better maintainability and developer experience)

### Phase 2: UX Enhancements (2-3 weeks)

**High Priority, Medium Effort:**

4. ✅ **Right-Hand Table of Contents** (4-5 hours)
   - Component styling
   - JavaScript for active state
   - Template integration
   - Responsive behavior

5. ✅ **Enhanced Typography System** (1 hour)
   - Systematic heading scales
   - Optimal line lengths
   - Consistent spacing

**Total Time:** ~6 hours
**Impact:** Very High (major UX improvement)

### Phase 3: Advanced Features (Optional)

**Medium Priority, Medium Effort:**

6. ⚠️ **Multi-Column Article Layout** (1-2 hours)
   - Add as optional class
   - Test with existing content
   - Add to documentation pages

**Total Time:** ~2 hours
**Impact:** Medium (improved readability for long content)

### Phase 4: Structural Changes (Future)

**Low Priority, High Effort:**

7. ⚠️ **Three-Column Grid Layout** (8-10 hours)
   - Only if adding documentation section
   - Requires template restructuring
   - Consider carefully

---

## Detailed Recommendations Summary

| Feature | Priority | Effort | Impact | Recommend? |
|---------|----------|--------|--------|------------|
| **CSS Custom Properties** | 🔴 HIGH | Low | High | ✅ YES - Immediate |
| **Code Block Styling** | 🔴 HIGH | Low | High | ✅ YES - Immediate |
| **Responsive Breakpoints** | 🟢 HIGH | Low | Medium | ✅ YES - Immediate |
| **Table of Contents** | 🔴 HIGH | Medium | Very High | ✅ YES - Next sprint |
| **Typography System** | 🟡 MEDIUM | Low | Medium | ✅ YES - Next sprint |
| **Multi-Column Layout** | 🟡 MEDIUM | Low | Medium | ⚠️ OPTIONAL - Test first |
| **3-Column Grid** | 🟡 LOW | High | Medium | ❌ NO - Not needed yet |

---

## Code Examples: Quick Implementation

### 1. Expanded CSS Variables (Add to `sass/custom.scss`)

```scss
// ============================================================================
// Enhanced CSS Custom Properties System (inspired by md-book)
// ============================================================================

:root {
  // ===== Color Palette =====
  // Neutral scale (50-900)
  --neutral-0: #ffffff;
  --neutral-50: #f9fafb;
  --neutral-100: #f3f4f6;
  --neutral-200: #e5e7eb;
  --neutral-300: #d1d5db;
  --neutral-400: #9ca3af;
  --neutral-500: #6b7280;
  --neutral-600: #4b5563;
  --neutral-700: #374151;
  --neutral-800: #1f2937;
  --neutral-900: #111827;

  // Brand colors
  --brand-primary: #00d1b2;
  --brand-secondary: #3273dc;
  --brand-success: #48c774;
  --brand-warning: #ffdd57;
  --brand-danger: #f14668;
  --brand-info: #3298dc;

  // ===== Semantic Colors (Light Theme) =====
  --color-text: var(--neutral-900);
  --color-text-secondary: var(--neutral-600);
  --color-text-muted: var(--neutral-500);

  --color-bg: var(--neutral-0);
  --color-bg-secondary: var(--neutral-50);
  --color-bg-tertiary: var(--neutral-100);

  --color-border: var(--neutral-200);
  --color-border-hover: var(--neutral-300);

  --color-link: var(--brand-secondary);
  --color-link-hover: var(--brand-primary);

  --color-accent: var(--brand-primary);

  // Code colors
  --color-code-bg: var(--neutral-100);
  --color-code-text: var(--neutral-800);

  // ===== Typography Scale =====
  --font-size-xs: 0.75rem;      /* 12px */
  --font-size-sm: 0.875rem;     /* 14px */
  --font-size-base: 1rem;       /* 16px */
  --font-size-lg: 1.125rem;     /* 18px */
  --font-size-xl: 1.25rem;      /* 20px */
  --font-size-2xl: 1.5rem;      /* 24px */
  --font-size-3xl: 1.875rem;    /* 30px */
  --font-size-4xl: 2.25rem;     /* 36px */
  --font-size-5xl: 3rem;        /* 48px */

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.7;
  --line-height-loose: 2;

  // ===== Spacing Scale =====
  --space-xs: 0.25rem;     /* 4px */
  --space-sm: 0.5rem;      /* 8px */
  --space-md: 1rem;        /* 16px */
  --space-lg: 1.5rem;      /* 24px */
  --space-xl: 2rem;        /* 32px */
  --space-2xl: 3rem;       /* 48px */
  --space-3xl: 4rem;       /* 64px */
  --space-4xl: 6rem;       /* 96px */

  // ===== Layout Dimensions =====
  --header-height: 4rem;
  --footer-height: auto;
  --sidebar-width: 280px;
  --toc-width: 240px;
  --content-max-width: 1200px;
  --content-narrow-width: 70ch;

  // ===== Border Radius =====
  --radius-sm: 3px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-full: 9999px;

  // ===== Shadows =====
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

  // ===== Transitions =====
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 350ms ease;

  // ===== Z-Index Scale =====
  --z-dropdown: 1000;
  --z-sticky: 1100;
  --z-fixed: 1200;
  --z-modal-backdrop: 1300;
  --z-modal: 1400;
  --z-popover: 1500;
  --z-tooltip: 1600;
}

// ===== Dark Theme Overrides =====
[theme="dark"] {
  --color-text: var(--neutral-50);
  --color-text-secondary: var(--neutral-300);
  --color-text-muted: var(--neutral-400);

  --color-bg: var(--neutral-900);
  --color-bg-secondary: var(--neutral-800);
  --color-bg-tertiary: var(--neutral-700);

  --color-border: var(--neutral-700);
  --color-border-hover: var(--neutral-600);

  --color-link: #67b5ff;
  --color-link-hover: #a0cfff;

  --color-code-bg: var(--neutral-800);
  --color-code-text: var(--neutral-100);

  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
}
```

### 2. Right-Hand TOC Component (Add to `sass/custom.scss`)

```scss
// ============================================================================
// Table of Contents Component (inspired by md-book)
// ============================================================================

.page-toc {
  position: sticky;
  top: calc(var(--header-height) + var(--space-md));
  max-height: calc(100vh - var(--header-height) - var(--space-xl));
  overflow-y: auto;
  padding: var(--space-lg);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);

  // Scrollbar styling
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: var(--radius-full);

    &:hover {
      background: var(--color-border-hover);
    }
  }

  h4 {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-text-secondary);
    margin-bottom: var(--space-md);
    margin-top: 0;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li {
    margin-bottom: var(--space-xs);
  }

  a {
    color: var(--color-text-secondary);
    text-decoration: none;
    display: block;
    padding: var(--space-xs) var(--space-sm);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-sm);
    line-height: var(--line-height-normal);
    transition: all var(--transition-fast);
    border-left: 2px solid transparent;

    &:hover {
      background: var(--color-bg-tertiary);
      color: var(--color-text);
      border-left-color: var(--color-accent);
    }

    &.active {
      background: var(--color-accent);
      color: white;
      font-weight: var(--font-weight-medium);
      border-left-color: var(--color-accent);
    }
  }

  // Nested heading levels
  .toc-level-2 {
    padding-left: 0;
  }

  .toc-level-3 {
    padding-left: var(--space-md);
    font-size: var(--font-size-xs);
  }

  .toc-level-4 {
    padding-left: var(--space-lg);
    font-size: var(--font-size-xs);
  }

  // Hide on smaller screens
  @media screen and (max-width: 1200px) {
    display: none;
  }
}

// Layout grid with TOC
.page-with-toc {
  display: grid;
  grid-template-columns: minmax(0, 1fr) var(--toc-width);
  gap: var(--space-2xl);

  @media screen and (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}
```

---

## Testing Plan

After implementing md-book inspired features:

### 1. Visual Regression Testing
- [ ] Compare before/after screenshots
- [ ] Test on multiple screen sizes (320px, 768px, 1024px, 1440px, 1920px)
- [ ] Test in multiple browsers (Chrome, Firefox, Safari, Edge)

### 2. Accessibility Testing
- [ ] Run WAVE accessibility checker
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility
- [ ] Verify color contrast ratios

### 3. Performance Testing
- [ ] Run Lighthouse audit
- [ ] Check CSS file size increase
- [ ] Measure page load times
- [ ] Test on slow 3G connection

### 4. Functionality Testing
- [ ] Table of contents navigation
- [ ] Active state highlighting
- [ ] Multi-column layout on wide screens
- [ ] Code block rendering
- [ ] Dark mode compatibility

---

## Conclusion

**Summary of Recommendations:**

**✅ Implement Immediately (Phase 1):**
1. Expanded CSS custom properties system
2. Better code block styling
3. Standardized responsive breakpoints

**✅ Implement Next Sprint (Phase 2):**
4. Right-hand table of contents (highest UX impact)
5. Enhanced typography system

**⚠️ Optional/Test First:**
6. Multi-column article layout (test with long-form content)

**❌ Not Recommended Now:**
7. Three-column grid layout (not needed for current content structure)

**Estimated Total Effort:**
- Phase 1: ~5 hours (immediate wins)
- Phase 2: ~6 hours (UX enhancements)
- Total: ~11 hours for major improvements

**Expected Benefits:**
- ✅ Better maintainability (CSS variables)
- ✅ Improved developer experience (code blocks)
- ✅ Enhanced navigation (table of contents)
- ✅ Better readability (typography, multi-column)
- ✅ More consistent responsive design

**Next Steps:**
1. Review this analysis
2. Prioritize features based on your content strategy
3. Start with Phase 1 (quick wins)
4. Test and iterate
5. Move to Phase 2 based on results

---

**Document Version:** 1.0
**Last Updated:** 2025-11-13
**Compatibility:** Terraphim AI (Zola 0.14.1, Bulma 1.0.2)
