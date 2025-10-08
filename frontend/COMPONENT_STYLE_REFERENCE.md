# Component Style Reference Guide

Quick reference for styling components in the Textile Management System.

## 🎨 Color Palette Quick Reference

### Primary Colors
```
Primary: #0F62FE (Blue)
Primary Hover: #0353E9
Primary Light: #E0E8FF (for focus rings)
```

### Text Colors
```
Text Primary: #161616 (dark) / #F4F4F4 (light mode dark theme)
Text Secondary: #525252 (dark) / #C6C6C6 (light mode dark theme)
Text Muted: #8D8D8D
```

### Background Colors
```
Background: #F4F4F4 (light) / #161616 (dark)
Surface: #FFFFFF (light) / #262626 (dark)
Surface Hover: #F8F8F8 (light) / #393939 (dark)
Border: #E0E0E0 (light) / #393939 (dark)
```

### Semantic Colors
```
Success: #24A148 (light) / #42BE65 (dark)
Warning: #F1C21B
Error: #DA1E28 (light) / #FA4D56 (dark)
```

## 📏 Spacing Scale

```
4px   = 0.25rem  = gap-1
8px   = 0.5rem   = gap-2, py-2
10px  = 0.625rem = button padding
14px  = 0.875rem = standard padding
16px  = 1rem     = gap-4, p-4
20px  = 1.25rem  = form-group margin
24px  = 1.5rem   = card padding
32px  = 2rem     = container padding
```

## 🔤 Typography Scale

```
11px = 0.6875rem = tiny text
12px = 0.75rem   = table headers
13px = 0.8125rem = labels, form labels
14px = 0.875rem  = body text, inputs
16px = 1rem      = standard text
18px = 1.125rem  = card titles, header
20px = 1.25rem   = page titles
```

## 📦 Component Sizing

### Buttons
```
Standard: padding: 0.625rem 1rem (10px 16px)
Small:    padding: 0.5rem 0.875rem (8px 14px)
Large:    padding: 0.875rem 1.5rem (14px 24px)

Border Radius: 0.5rem (8px)
Font Size: 0.875rem (14px)
```

### Form Inputs
```
Padding: 0.625rem 0.875rem (10px 14px)
Border: 1px solid var(--color-border)
Border Radius: 0.5rem (8px)
Font Size: 0.875rem (14px)
Height: ~36px
```

### Tables
```
Header Padding: 0.875rem 1rem (14px 16px)
Cell Padding: 0.875rem 1rem (14px 16px)
Header Font: 0.75rem (12px) uppercase
Cell Font: 0.875rem (14px)
```

### Cards
```
Padding: 1.5rem (24px)
Border Radius: 0.5rem (8px)
Border: 1px solid var(--color-border)
Shadow: var(--shadow-sm)
```

## 🎯 Common Patterns

### Page Layout
```tsx
<div>
  {/* Sticky Header */}
  <div className="page-header">
    <div className="container">
      <h1 className="page-title">Title</h1>
      <p className="page-subtitle">Subtitle</p>
    </div>
  </div>
  
  {/* Content */}
  <div className="container">
    <div className="table-section">
      {/* Content here */}
    </div>
  </div>
</div>
```

### Form Layout
```tsx
<div className="card">
  <div className="card-header">
    <h2 className="card-title">Form Title</h2>
    <p className="card-description">Description</p>
  </div>
  
  <form>
    <div className="form-group">
      <label className="form-label">Label</label>
      <input className="form-input" type="text" />
    </div>
    
    <div className="flex gap-3">
      <button className="btn btn-primary">Save</button>
      <button className="btn btn-secondary">Cancel</button>
    </div>
  </form>
</div>
```

### Table Layout
```tsx
<div className="table-section">
  <div className="search-bar">
    <div className="flex items-center gap-6">
      <div className="flex-1 search-input-container">
        <Search className="search-icon" size={20} />
        <input
          type="text"
          className="form-input search-input"
          placeholder="Search..."
        />
      </div>
      <div className="search-results-badge">
        10 results
      </div>
    </div>
  </div>
  
  <div className="overflow-x-auto">
    <table>
      <thead>
        <tr>
          <th>Column 1</th>
          <th>Column 2</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Data 1</td>
          <td>Data 2</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

### Modal/Overlay
```tsx
<div className="form-overlay">
  <div 
    className="form-overlay-backdrop" 
    onClick={handleClose}
  ></div>
  <div className="form-overlay-content">
    <div className="card">
      {/* Modal content */}
    </div>
  </div>
</div>
```

## 🎨 Utility Classes

### Layout
```
.container         - Max-width container with padding
.flex              - Flexbox display
.flex-col          - Flex column direction
.items-center      - Align items center
.justify-between   - Justify content space-between
.gap-3             - Gap of 0.75rem
```

### Spacing
```
.mb-4             - Margin bottom 1rem
.mt-4             - Margin top 1rem
.p-4              - Padding all sides 1rem
.px-4             - Padding horizontal 1rem
.py-2             - Padding vertical 0.5rem
```

### Text
```
.text-sm          - Font size 0.875rem
.text-lg          - Font size 1.125rem
.font-semibold    - Font weight 600
.text-primary     - Primary text color
.text-secondary   - Secondary text color
```

## 🎯 Component Classes

### Buttons
```
.btn              - Base button
.btn-primary      - Primary button (blue)
.btn-secondary    - Secondary button (bordered)
.btn-success      - Success button (green)
.btn-danger       - Danger button (red)
.btn-sm           - Small button
.btn-lg           - Large button
```

### Forms
```
.form-group       - Form field container
.form-label       - Form field label
.form-input       - Text input
.form-select      - Select dropdown
.form-textarea    - Textarea
.form-checkbox    - Checkbox input
.checkbox-label   - Checkbox with label
```

### Status
```
.status-badge         - Base badge
.status-active        - Active status (green)
.status-inactive      - Inactive status (red)
.search-results-badge - Search results count
```

### Tables
```
.table-section    - Table container
.overflow-x-auto  - Scrollable table wrapper
```

### Cards
```
.card             - Base card
.card-header      - Card header section
.card-title       - Card title
.card-description - Card description
```

### Search
```
.search-bar           - Search container
.search-input         - Search input field
.search-input-container - Input with icon wrapper
.search-icon          - Search icon positioning
```

## 🔍 Interactive States

### Hover States
```css
/* Buttons */
.btn:hover { opacity: 0.9; }

/* Inputs */
.form-input:hover { border-color: var(--color-text-secondary); }

/* Sidebar Items */
.sidebar-item:hover { background-color: var(--color-surface-hover); }

/* Table Rows */
tr:hover { background-color: var(--color-surface-hover); }
```

### Focus States
```css
/* Inputs */
.form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

/* Buttons */
.btn:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### Active States
```css
/* Buttons */
.btn:active { opacity: 0.8; }

/* Sidebar Items */
.sidebar-item-active {
  background-color: var(--color-primary);
  color: white;
}
```

## 📱 Responsive Utilities

### Breakpoints
```css
/* Mobile: < 768px */
@media (max-width: 768px) {
  /* Reduced spacing */
}

/* Desktop: > 768px */
@media (min-width: 769px) {
  /* Full layout */
}
```

### Mobile Adjustments
- Reduce padding by 25-30%
- Stack horizontal layouts
- Simplify complex grids
- Increase touch targets

## ⚡ Animation/Transition

### Standard Transitions
```css
transition: var(--transition-fast);  /* 0.15s */
transition: var(--transition);       /* 0.2s */
```

### Easing
```css
cubic-bezier(0.4, 0, 0.2, 1)  /* Standard easing */
```

### Properties to Transition
```css
/* Fast rendering */
opacity
transform

/* Slower rendering (use sparingly) */
background-color
border-color
```

## 🎨 Dark Mode Classes

All colors automatically adapt when using CSS variables:

```tsx
// Theme toggle
const { theme, toggleTheme } = useTheme();

// Colors adapt automatically
<div style={{ 
  backgroundColor: 'var(--color-surface)',
  color: 'var(--color-text-primary)'
}}>
  Content
</div>
```

## 📋 Checklist for New Components

- [ ] Use CSS variables for colors
- [ ] Follow spacing scale
- [ ] Use typography scale
- [ ] Test in light mode
- [ ] Test in dark mode
- [ ] Test responsive behavior
- [ ] Add hover states
- [ ] Add focus states
- [ ] Check contrast ratios
- [ ] Verify keyboard navigation

## 🚀 Quick Tips

1. **Always use CSS variables** for colors
2. **Stick to the spacing scale** (0.25rem, 0.5rem, etc.)
3. **Use rem units** instead of px
4. **Keep transitions fast** (< 0.2s)
5. **Test in both themes**
6. **Maintain consistency** with existing components
7. **Use utility classes** when possible
8. **Follow the typography scale**
9. **Keep it simple** - less is more
10. **Check accessibility** (contrast, focus states)

## 📚 Additional Resources

- See `IMPLEMENTATION_GUIDE.md` for detailed usage
- See `DESIGN_COMPARISON.md` for before/after comparisons
- See `DESIGN_IMPROVEMENTS_SUMMARY.md` for complete breakdown
- Check `globals.css` for all available classes

---

## Quick Copy-Paste Examples

### Button Group
```tsx
<div className="flex gap-3">
  <button className="btn btn-primary">Save</button>
  <button className="btn btn-secondary">Cancel</button>
</div>
```

### Form Field
```tsx
<div className="form-group">
  <label className="form-label">Field Name</label>
  <input 
    type="text" 
    className="form-input" 
    placeholder="Enter value"
  />
</div>
```

### Status Badge
```tsx
<span className="status-badge status-active">
  Active
</span>
```

### Card with Header
```tsx
<div className="card">
  <div className="card-header">
    <h2 className="card-title">Card Title</h2>
    <p className="card-description">Description text</p>
  </div>
  {/* Content */}
</div>
```

---

**Last Updated**: October 8, 2025
**Version**: 1.0.0

