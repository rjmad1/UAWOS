

## 1. Purpose

This document defines the canonical design language, UX principles, component architecture, layout system, interaction patterns, accessibility requirements, responsive behavior, and implementation standards for all UAWOS user experiences.

This specification serves as the single source of truth for:

- UI Design

- UX Design

- Front-End Engineering

- AI Generated Components

- Product Design

- Design Reviews

- Accessibility Reviews

- Future Design System Evolution

---

# 2. Design Philosophy

## Core Principles

### Clarity First

Users should never wonder:

- Where they are

- What they can do

- What happens next

### Information Density Without Clutter

Optimize for:

- Enterprise users

- Power users

- Operations teams

- Administrators

- Analysts

Avoid:

- Excessive whitespace

- Marketing-style layouts

- Decorative UI

### Progressive Disclosure

Show:

- Important information immediately

- Advanced information when needed

### Action-Oriented

Every screen must answer:

- What is happening?

- What requires attention?

- What actions are available?

### Consistency Over Creativity

Prefer:

- Familiar patterns

- Predictable interactions

Avoid:

- Novel controls

- Hidden interactions

---

# 3. Design Foundation

## Design System

Framework:

- shadcn/ui

- Radix UI

- Tailwind CSS

Style:

- New York

Theme:

- Default

Color Palette:

- Default shadcn theme tokens

Typography:

- Default shadcn typography scale

Radius:

- Default radius scale

Icons:

- Lucide Icons

Animations:

- shadcn defaults

- subtle only

No custom visual language unless approved through architecture review. ([Shadcn UI](https://ui.shadcn.com/docs/theming?utm_source=chatgpt.com "Theming - shadcn/ui"))

---

# 4. Color System

## Use Default shadcn Tokens

Never hardcode colors.

Use semantic tokens only.

### Core Tokens

```css
background
foreground

card
card-foreground

popover
popover-foreground

primary
primary-foreground

secondary
secondary-foreground

muted
muted-foreground

accent
accent-foreground

destructive
destructive-foreground

border
input
ring
```

### Sidebar Tokens

```css
sidebar-background
sidebar-foreground
sidebar-primary
sidebar-border
sidebar-ring
```

Use CSS variables exclusively. ([Shadcn UI](https://ui.shadcn.com/docs/theming?utm_source=chatgpt.com "Theming - shadcn/ui"))

---

# 5. Typography

## Font

Default shadcn font stack

### Scale

| Type      | Usage              |
| --------- | ------------------ |
| Text XS   | metadata           |
| Text SM   | helper text        |
| Text Base | body               |
| Text LG   | emphasized         |
| H4        | section titles     |
| H3        | cards              |
| H2        | page titles        |
| H1        | application titles |

### Rules

Maximum 3 font sizes per screen hierarchy.

Avoid:

- Decorative fonts

- Excessive weights

---

# 6. Spacing System

Use Tailwind scale only.

### Preferred

```text
1
2
4
6
8
12
16
24
32
```

### Layout Rhythm

```text
Component Gap:
16px

Section Gap:
24px

Page Gap:
32px

Dashboard Gap:
24px
```

---

# 7. Grid System

## Desktop

```text
12 Columns
```

## Tablet

```text
8 Columns
```

## Mobile

```text
4 Columns
```

## Maximum Width

```text
1600px
```

Content centered.

---

# 8. Application Layout Architecture

## Primary Shell

```text
┌───────────────────────────┐
│ Top Navigation            │
├───────┬───────────────────┤
│       │                   │
│ Left  │ Main Content      │
│ Nav   │                   │
│       │                   │
├───────┴───────────────────┤
│ Status / Notifications    │
└───────────────────────────┘
```

---

# 9. Navigation Standards

## Primary Navigation

Use:

- Sidebar

Components:

- Sidebar

- Collapsible Sidebar

- Navigation Menu

### Sidebar Behavior

Expanded:

```text
280px
```

Collapsed:

```text
72px
```

### Navigation Rules

Maximum:

- 3 levels

Avoid:

- Deep nesting

---

# 10. Page Structure Standard

Every page contains:

```text
Page Header

Context Actions

Filters

Content Area

Status Area

Supporting Panels
```

---

# 11. Component Standards

## Allowed shadcn Components

### Inputs

- Input

- Textarea

- Select

- Combobox

- Checkbox

- Radio Group

- Switch

- Slider

### Data

- Table

- Data Table

- Chart

- Badge

### Navigation

- Breadcrumb

- Tabs

- Navigation Menu

- Pagination

### Feedback

- Alert

- Alert Dialog

- Toast

- Progress

- Skeleton

### Overlay

- Dialog

- Drawer

- Popover

- Sheet

### Layout

- Accordion

- Card

- Separator

- Resizable

### Advanced

- Command

- Calendar

- Date Picker

- Sidebar

Use native shadcn implementations whenever available. ([Shadcn UI](https://ui.shadcn.com/?utm_source=chatgpt.com "The Foundation for your Design System - shadcn/ui"))

---

# 12. Dashboard Standards

Every dashboard must include:

## Header

- Title

- Context

- Global actions

## KPI Layer

Cards:

- Revenue

- Utilization

- Throughput

- Alerts

- Health

## Trend Layer

Charts

## Operational Layer

Tables

## Action Layer

Tasks

---

# 13. Table Standards

Enterprise applications are table-first.

### Requirements

Support:

- Sorting

- Filtering

- Pagination

- Export

- Column resize

- Column visibility

- Sticky headers

- Bulk actions

### Row Actions

Use:

- Dropdown menu

Never:

- Inline clutter

---

# 14. Forms

## Layout

Single Column:

Simple forms

Two Column:

Complex forms

### Validation

Real-time validation

Display:

- Error

- Warning

- Success

### Submit Behavior

Must include:

- Loading state

- Success state

- Failure state

---

# 15. Search Experience

## Global Search

Use:

- Command Component

Capabilities:

- Search entities

- Search actions

- Search screens

Shortcut:

```text
CTRL + K
```

---

# 16. Empty States

Every empty state must include:

### Required

- Explanation

- Action

- Visual cue

### Example

```text
No Work Orders Found

Create your first work order
or adjust your filters.
```

---

# 17. Loading States

Use:

- Skeleton

Avoid:

- Spinners

except:

- Short actions

---

# 18. Notifications

Use:

- Toast

Categories:

```text
Success
Warning
Error
Info
```

---

# 19. Accessibility Standards

Minimum:

WCAG AA

Requirements:

- Keyboard Navigation

- Screen Reader Support

- Focus Visibility

- ARIA Labels

- Semantic HTML

All controls must be keyboard accessible. shadcn/ui components are built on accessible primitives and should retain those characteristics. ([Shadcn UI](https://ui.shadcn.com/?utm_source=chatgpt.com "The Foundation for your Design System - shadcn/ui"))

---

# 20. Responsive Design

## Breakpoints

```text
sm
md
lg
xl
2xl
```

### Mobile First

Always:

```text
Mobile
Tablet
Desktop
```

Design sequence.

---

# 21. Dark Mode

Mandatory.

Support:

- Light

- Dark

- System

Use theme tokens only.

Never:

```css
#FFFFFF
#000000
```

directly.

---

# 22. Motion Standards

### Allowed

- Fade

- Slide

- Expand

- Collapse

### Avoid

- Bounce

- Excessive parallax

- Decorative motion

Duration:

```text
150–250ms
```

---

# 23. Error Handling

Every failure must include:

### User Message

Human readable

### Technical Context

Logged

### Recovery Action

Visible

---

# 24. AI-Native UX Standards

All AI experiences must support:

### Prompt Input

Rich Input

### Streaming Output

Incremental rendering

### Citations

Visible references

### Actions

Copy

Retry

Regenerate

Share

Export

### History

Conversation memory

---

# 25. Performance Requirements

### Lighthouse

Target:

```text
90+
```

### Core Web Vitals

Pass all metrics.

### Interaction

Target:

```text
<100ms perceived response
```

---

# 26. Security UX

Sensitive actions require:

- Confirmation Dialog

- Audit Logging

- Role Validation

Destructive actions:

Use:

```text
Alert Dialog
```

---

# 27. Design Review Checklist

Before approval verify:

### Consistency

- Uses shadcn components

### Accessibility

- WCAG AA

### Responsiveness

- Mobile

- Tablet

- Desktop

### States

- Empty

- Loading

- Error

- Success

### Dark Mode

Verified

### Performance

Verified

### Security

Verified

---

# 28. Non-Negotiable Rules

1. No custom component before evaluating shadcn equivalent.

2. No hardcoded colors.

3. No hardcoded spacing.

4. No inaccessible interactions.

5. No hidden critical actions.

6. No decorative complexity.

7. No visual design divergence from shadcn defaults.

8. All pages must support dark mode.

9. All forms require validation.

10. All tables require filtering and sorting.

11. All AI experiences require streaming support.

12. All new UI must be composable and reusable.

---

# 29. Reference Component Inventory

Adopt the complete shadcn/ui catalog as the approved component inventory:

- Accordion

- Alert

- Alert Dialog

- Aspect Ratio

- Avatar

- Badge

- Breadcrumb

- Button

- Calendar

- Card

- Carousel

- Chart

- Checkbox

- Collapsible

- Combobox

- Command

- Context Menu

- Data Table

- Date Picker

- Dialog

- Drawer

- Dropdown Menu

- Form

- Hover Card

- Input

- Input OTP

- Label

- Menubar

- Navigation Menu

- Pagination

- Popover

- Progress

- Radio Group

- Resizable

- Scroll Area

- Select

- Separator

- Sheet

- Sidebar

- Skeleton

- Slider

- Sonner

- Switch

- Table

- Tabs

- Textarea

- Toast

- Toggle

- Toggle Group

- Tooltip

- Tree

- Command Palette

- Charts

- AI Input Patterns

- Authentication Patterns

- Dashboard Patterns

Use official shadcn patterns as the default implementation baseline. ([Shadcn UI](https://ui.shadcn.com/docs?utm_source=chatgpt.com "Introduction - Shadcn UI"))

This document is sufficiently comprehensive to act as the foundational design specification for a large-scale enterprise SaaS platform, AI-native application, operations platform, or internal developer portal built on shadcn/ui.
