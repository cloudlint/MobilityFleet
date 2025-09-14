# Dashboard Design Guidelines

## Design Approach
**Selected Approach**: Design System (Material Design/Fluent Design hybrid)
**Justification**: This is a utility-focused enterprise dashboard prioritizing efficiency, data density, and learnability over visual flair.

## Core Design Elements

### Color Palette
- **Primary**: 213 94% 68% (Professional blue)
- **Surface (Light)**: 210 20% 98% (Card backgrounds)
- **Surface (Dark)**: 213 18% 12% (Dark mode cards)
- **Border**: 214 20% 87% (Light) / 213 15% 25% (Dark)
- **Text Primary**: 213 25% 15% (Light) / 210 15% 95% (Dark)
- **Accent**: 142 71% 45% (Success green for positive metrics)

### Typography
- **Primary Font**: Inter via Google Fonts CDN
- **Headers**: 600 weight, 16-18px
- **Body**: 400 weight, 14px
- **Metrics**: 500 weight, 20-24px for key numbers

### Layout System
**Spacing Units**: Tailwind 2, 4, 6, 8 units consistently
- Card padding: p-6
- Icon spacing: mr-2, ml-2
- Button margins: m-2
- Grid gaps: gap-6

### Component Library

#### Dashboard Cards
- **Container**: Rounded corners (rounded-lg), subtle shadow (shadow-sm)
- **Header Section**: Flex layout with title left, controls right
- **Minimize/Maximize Controls**: 
  - Icon-only buttons using Heroicons (ChevronUpIcon/ChevronDownIcon)
  - Size: 20px icons in 32px clickable area
  - Hover state: Subtle background (hover:bg-gray-100)
  - Position: Top-right corner of card header

#### Card States
- **Expanded**: Full content visible, ChevronUpIcon
- **Minimized**: Header + 1-line summary visible, ChevronDownIcon
- **Transition**: 200ms ease-in-out for smooth collapse/expand

#### Grid Layout
- **Desktop**: 3-column grid using CSS Grid
- **Tablet**: 2-column adaptive
- **Mobile**: Single column stack
- **Card Heights**: Auto-fit content, maintain alignment

### Card Header Design
- **Structure**: Title (left) + Metric Preview (center) + Controls (right)
- **Minimized Preview**: Show 1 key metric (e.g., "23 Active Rentals")
- **Visual Hierarchy**: Card title (font-medium), preview (text-gray-600)

### Interaction Patterns
- **Click Target**: Entire button area (not just icon)
- **Keyboard**: Tab navigation, Enter/Space activation
- **State Persistence**: Remember collapsed/expanded states per user session
- **Batch Controls**: Optional "Collapse All"/"Expand All" buttons in dashboard header

### Icons
Use Heroicons via CDN:
- Minimize: ChevronUpIcon
- Maximize: ChevronDownIcon
- Consistent 20px sizing across all controls

### Accessibility
- **ARIA Labels**: "Minimize card" / "Maximize card"
- **Focus States**: Clear focus rings on controls
- **Screen Readers**: Announce state changes
- **Dark Mode**: Consistent implementation across all card elements

This design prioritizes usability and efficiency while maintaining professional aesthetics suitable for a business dashboard environment.