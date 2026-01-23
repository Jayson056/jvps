# JVPS Desktop Remote - Design Reference Guide

## Brand Identity

### Name
- **Full Name**: JVPS Desktop Remote
- **Tagline**: "Remote Desktop Control & Screen Sharing"
- **Type**: Enterprise-Grade Desktop Control Solution

### Color Palette
```
Primary Blue:       #3498db (Actions, Primary UI)
Success Green:      #2ecc71 (Positive, Approvals)
Warning Orange:     #f39c12 (Alerts, Info)
Danger Red:         #e74c3c (Destructive, Errors)
Dark Background:    #0f0f0f (Main)
Dark Secondary:     #1a1a1a (Panels)
Container BG:       rgba(20, 20, 20, 0.95)
Text Primary:       #f1f1f1 (Main text)
Text Secondary:     #888 (Secondary text)
Border Light:       rgba(255, 255, 255, 0.05) (Subtle borders)
```

---

## Icon System (Font Awesome 6.4.0)

### Navigation & General
| Icon | Class | Usage |
|------|-------|-------|
| 🏠 | `fas fa-home` | Home/Dashboard |
| ← | `fas fa-arrow-left` | Back |
| ❌ | `fas fa-times` | Close/Cancel |
| ℹ️ | `fas fa-info-circle` | Information |
| ⚠️ | `fas fa-exclamation-circle` | Warning/Error |
| ✓ | `fas fa-check` | Confirm/Success |
| ✓ | `fas fa-check-circle` | Status - Connected |

### Devices & Connection
| Icon | Class | Usage |
|------|-------|-------|
| 🖥️ | `fas fa-desktop` | Desktop/Device |
| 🔗 | `fas fa-network-wired` | Network/Session |
| 🔌 | `fas fa-microchip` | Device ID |
| 📋 | `fas fa-id-card` | Session ID |
| 📡 | `fas fa-broadcast-tower` | Broadcasting |
| 👁️ | `fas fa-eye` | View/Watch |

### Control & Input
| Icon | Class | Usage |
|------|-------|-------|
| 🖱️ | `fas fa-mouse` | Mouse Control |
| ⌨️ | `fas fa-keyboard` | Keyboard Input |
| 👥 | `fas fa-users` | Connected Users |
| 🎮 | `fas fa-gamepad` | Control Mode |
| 🖱️ | `fas fa-click` | Click Action |

### Actions & Features
| Icon | Class | Usage |
|------|-------|-------|
| 📺 | `fas fa-share-screen` | Share/Broadcast |
| 🔐 | `fas fa-lock` | Security/Password |
| 🔑 | `fas fa-key` | Access Code |
| ✨ | `fas fa-magic` | Direct Link |
| 📋 | `fas fa-copy` | Copy |
| ⏱️ | `fas fa-tachometer-alt` | Latency/Speed |
| ⏳ | `fas fa-hourglass-start` | Waiting |
| ⏹️ | `fas fa-stop-circle` | Stop |

### Animated
| Icon | Class | Usage |
|------|-------|-------|
| ⌛ | `fas fa-spinner fa-spin` | Loading Spinner |
| 🔄 | `fas fa-redo` | Rotate/Refresh |
| 📤 | `fas fa-sign-out-alt` | Exit/Logout |
| 📥 | `fas fa-sign-in-alt` | Connect/Login |

---

## Button Styles

### Primary Button
```css
background: linear-gradient(135deg, #3498db, #2980b9);
color: #fff;
box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
```
**Usage**: Main actions (Connect, Create Session, Share)

### Secondary Button
```css
background: linear-gradient(135deg, #7f8c8d, #606c70);
color: #fff;
box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
```
**Usage**: Navigation, alternative actions (Back, Dashboard)

### Danger Button
```css
background: linear-gradient(135deg, #e74c3c, #c0392b);
color: #fff;
box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
```
**Usage**: Destructive actions (Stop, Exit, Cancel)

### All Buttons Include:
- Flexbox layout with icon support
- Icon + text with 8px gap
- Hover animation: `translateY(-3px)`
- Enhanced shadow on hover
- Smooth transitions (300ms)

---

## Typography

### Headings (h1, h2)
- **Gradient**: Blue (#3498db) → Green (#2ecc71)
- **Font-Weight**: 700
- **Font-Size**: Auto-responsive
- **Text-Align**: Center (on most pages)
- **Icon**: Right-aligned with 10px margin

### Body Text
- **Font**: System stack (-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto)
- **Color**: #f1f1f1 (primary), #888 (secondary)
- **Line-Height**: 1.6

---

## Page Structure

### Standard Container
```
Max-Width: 900px
Margin: 40px auto
Padding: 20px
Background: rgba(20, 20, 20, 0.95)
Border-Radius: 15px
Box-Shadow: 0 8px 32px rgba(0, 0, 0, 0.4)
Border: 1px solid rgba(255, 255, 255, 0.05)
```

### Cards/Lists
```
Background: Gradient or transparent
Border: 1px solid rgba(52, 152, 219, 0.2)
Padding: 15px
Border-Radius: 12px
Transition: All 300ms
Hover: Transform translateX(5px), enhanced shadow
```

---

## Status Indicators

### Connected Status
- **Dot Color**: #27ae60 (Green)
- **Text**: "Connected to device"
- **Animation**: Pulse (0-1 opacity)

### Connecting Status
- **Dot Color**: #f39c12 (Orange)
- **Text**: "Connecting..." / "Connecting to device..."
- **Animation**: Pulse or spinner

### Disconnected Status
- **Dot Color**: #e74c3c (Red)
- **Text**: "Connection Lost" / "Disconnected"
- **Animation**: Static

---

## Form Elements

### Input Fields
```css
Padding: 12px
Border: 2px solid #34495e
Background: rgba(52, 73, 94, 0.3)
Color: #f1f1f1
Border-Radius: 8px
Transition: All 300ms

Focus State:
  Border-Color: #3498db
  Background: rgba(52, 73, 94, 0.5)
  Box-Shadow: 0 0 10px rgba(52, 152, 219, 0.3)
```

### Labels
```css
Color: #3498db
Font-Weight: 600
Font-Size: 0.95rem
Margin-Bottom: 8px
Icon: Included with 5-8px gap
```

---

## Responsive Design

### Desktop (min-width: 768px)
- Full container width used
- Multi-column layouts enabled
- Full control panel displayed

### Tablet & Mobile (max-width: 767px)
- Adjusted padding and margins
- Single column layouts
- Smaller buttons
- Optimized for touch
- Video player adjustments

---

## Animation Library

### Transitions
- **Default**: All 300ms cubic-bezier(0.4, 0, 0.2, 1)
- **Button Hover**: translateY(-3px)
- **List Item Hover**: translateX(5px)
- **Background Fade**: 0.3s ease

### Keyframe Animations
- **pulse**: 0% opacity 1, 50% opacity 0.5, 100% opacity 1 (2s infinite)
- **spin**: 0deg → 360deg (continuous)
- **slideDown**: translateY(-10px) + opacity fade

---

## Accessibility Considerations

1. **Icon + Text Pairing**: Every icon includes descriptive text
2. **Color Contrast**: All text meets WCAG AA standards
3. **Focus States**: Clear focus indicators on all interactive elements
4. **Semantic HTML**: Proper use of heading hierarchy
5. **ARIA Labels**: Added where necessary for screen readers
6. **Keyboard Navigation**: All interactive elements accessible via keyboard

---

## Professional Language Guide

### Replace These | With These
```
🎬 OmniStream Pro          →  JVPS Desktop Remote
Broadcasting              →  Sharing / Sharing Active
Viewer                    →  Connected User / Viewer
Session                   →  Session / Device / Connection
Room                      →  Device
Broadcasting              →  Streaming / Sharing
Broadcast                 →  Connection / Session
Auto-Connect              →  Direct Access
Manual View               →  Secure Access
Password                  →  Access Code
Watch Live                →  Connect to Device
Start Broadcasting        →  Start Sharing
Waiting for viewers       →  Waiting for connections
Active Viewers            →  Connected Users
Connection Information    →  Connection Details
How Viewers Connect       →  Connection Instructions
Broadcaster               →  Remote Device
```

---

## Font Awesome CDN URL
```
https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
```

Include in `<head>` of all templates:
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

---

## Quick Implementation Examples

### Button with Icon
```html
<button class="btn btn-primary">
    <i class="fas fa-check"></i> Create Session
</button>
```

### Status Display
```html
<div class="status-indicator">
    <div class="status-dot connected"></div>
    <span id="statusText"><i class="fas fa-spinner fa-spin"></i> Connecting...</span>
</div>
```

### Info Box
```html
<div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #3498db;">
    <h3><i class="fas fa-info-circle"></i> Information</h3>
    <p>Your informative text here</p>
</div>
```

---

## Design System Version
- **Version**: 2.0 (Professional Edition)
- **Brand**: JVPS Desktop Remote
- **Updated**: January 24, 2026
- **Status**: Complete & Ready for Production

