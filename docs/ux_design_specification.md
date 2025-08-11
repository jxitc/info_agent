# Info Agent - UX Design Specification

## Overview

This document defines the user experience design for Info Agent's web interface, translating the existing CLI functionality into an intuitive, responsive web application that works seamlessly across desktop and mobile platforms.

## Design Goals

### Primary Objectives
- **Accessibility**: Make Info Agent's powerful features accessible to non-technical users
- **Feature Parity**: Support all existing CLI commands through intuitive UI interactions
- **Cross-Platform**: Responsive design that works on desktop, tablet, and mobile devices
- **Performance**: Fast, efficient interface that scales with large memory collections
- **Consistency**: Maintain the same core workflows and mental models as the CLI

### User Experience Principles
- **Minimalist Design**: Clean, uncluttered interface focused on content
- **Progressive Disclosure**: Surface advanced features without overwhelming basic users
- **Keyboard-Friendly**: Maintain power-user efficiency with keyboard shortcuts
- **Responsive**: Seamless experience across all device sizes

## Information Architecture

### Core User Flows
1. **View Memories** → Browse and discover existing memories
2. **Search Memories** → Find specific information quickly
3. **Add Memory** → Create new memories with AI processing
4. **Memory Details** → View full memory content and metadata

## Layout Structure

### Desktop Layout (≥1024px)
```
┌─ Header ──────────────────────────────────────────────┐
│ [Logo] Info Agent                           [Profile] │
├─ Navigation ─┬─ Main Content ──────────────────────────┤
│ ■ Show all   │ ┌─ Search Bar ─────────────────────────┐ │
│   memory     │ │ [Search for memory...]        [🔍]  │ │
│ ■ Add new    │ └──────────────────────────────────────┘ │
│   memory     │ ┌─ Content Area ───────────────────────┐ │
│ ■ Search     │ │ [Memory Cards Grid]                  │ │
│ ■ Settings   │ │                                      │ │
│ ■ Help       │ │                                      │ │
└──────────────┴─└──────────────────────────────────────┘ │
```

### Mobile Layout (≤768px)
```
┌─ Header ──────────────────────────────┐
│ [☰] Info Agent              [Profile] │
├─ Search ─────────────────────────────┤
│ [Search for memory...]        [🔍]   │
├─ Content ────────────────────────────┤
│ [Memory Cards - Single Column]       │
│                                      │
│                                      │
└─ Bottom Navigation ──────────────────┤
│ [Home] [Add] [Search] [Profile]      │
```

## Component Specifications

### 1. Navigation System

#### Desktop Sidebar Navigation
- **Position**: Fixed left sidebar (240px width)
- **Background**: Light gray (#F8F9FA)
- **Items**:
  - Show all memory (⭐ icon, keyboard: Ctrl+1)
  - Add new memory (+ icon, keyboard: Ctrl+N)
  - Search (🔍 icon, keyboard: Ctrl+F)
  - Vector operations (⚡ icon, keyboard: Ctrl+V)
  - LLM testing (🧠 icon, keyboard: Ctrl+L)
  - System status (📊 icon, keyboard: Ctrl+S)
  - Settings (⚙️ icon, keyboard: Ctrl+,)
  - Help (❓ icon, keyboard: F1)

#### Mobile Bottom Navigation
- **Items**: Home, Add, Search, More
- **Fixed position** at bottom of screen
- **Active state** highlighting

### 2. Search System

#### Global Search Bar
- **Placement**: Prominent in header/top section
- **Placeholder**: "Search for memory..." 
- **Features**:
  - Auto-complete suggestions
  - Recent searches
  - Search filters (categories, people, dates)
  - Advanced search toggle
- **Keyboard Shortcuts**: 
  - Focus: `/` or `Ctrl+K`
  - Clear: `Esc`

#### Advanced Search Panel
- **Expandable panel** below main search bar
- **Filters**:
  - Categories (dropdown/tags)
  - People mentioned
  - Date range picker
  - Content type (notes, meetings, tasks, etc.)
  - AI processing status
- **Search modes**:
  - Semantic search (default)
  - Exact text match
  - Hybrid search

### 3. Memory Display Components

#### Memory Card (List View)
```
┌─ Memory Card ────────────────────────────────┐
│ ┌─[i]─┐ Title                    [•••] Menu  │
│ │     │ Body preview text...                │
│ │     │ ┌─ Metadata ─────────────────────┐  │
│ └─────┘ │ 📅 2 days ago  📂 Work  👤 John │  │
│         └─────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

#### Memory Card (Grid View)
```
┌─ Memory Card ──────────────┐
│ Title              [Menu]  │
│ ─────────────────────────  │
│ Body preview text...       │
│ ...truncated...            │
│ ─────────────────────────  │
│ 📅 2 days  📂 Work  👤 John │
└────────────────────────────┘
```

#### Memory Card Components
- **Icon/Avatar**: AI-generated or category-based visual indicator
- **Title**: AI-extracted title (truncated at 60 chars)
- **Preview**: First 120 characters of content
- **Metadata Pills**: 
  - Creation date (relative: "2 days ago")
  - Category tag
  - People mentioned
  - AI processing status
- **Actions Menu**: Edit, delete, share, duplicate
- **Interactive States**: Hover, selected, loading

### 4. Memory Detail View

#### Full-Screen Modal (Desktop)
- **Header**: Title, edit button, close button
- **Content**: Full memory text with formatting
- **Sidebar**: 
  - Metadata panel
  - Dynamic fields
  - Related memories
  - Actions (edit, delete, export)

#### Full-Page View (Mobile)
- **Navigation**: Back button, title, actions menu
- **Content**: Scrollable memory content
- **Bottom actions**: Edit, Delete, Share

### 5. Add Memory Interface

#### Quick Add (Always Visible)
- **Floating Action Button** (mobile)
- **"Add new memory" sidebar item** (desktop)
- **Keyboard shortcut**: `Ctrl+N`

#### Add Memory Form
- **Text Area**: Large, auto-expanding input field
- **AI Processing Toggle**: Enable/disable AI extraction
- **Title Override**: Optional manual title input
- **Category Selection**: Dropdown or tag input
- **Save Options**: 
  - Save (Ctrl+S)
  - Save & Add Another (Ctrl+Shift+S)
  - Cancel (Esc)

#### AI Processing Indicators
- **Processing Status**: "Analyzing text..." with spinner
- **Extraction Preview**: Show AI-extracted fields before saving
- **Error Handling**: Clear error messages with retry options

## Responsive Design Breakpoints

### Desktop Large (≥1440px)
- Sidebar: 280px
- Content: 3-column memory grid
- Search: Full-width with advanced filters visible

### Desktop Medium (1024px - 1439px)
- Sidebar: 240px
- Content: 2-column memory grid
- Search: Full-width with collapsible filters

### Tablet (768px - 1023px)
- Sidebar: Collapsible overlay
- Content: 2-column memory grid
- Search: Full-width with modal filters

### Mobile Large (480px - 767px)
- Navigation: Bottom tab bar
- Content: Single column with cards
- Search: Full-width with bottom sheet filters

### Mobile Small (≤479px)
- Navigation: Bottom tab bar
- Content: Condensed single column
- Search: Full-width with simplified interface

## Basic Interaction Patterns (MVP)

### Memory Management (Basic)
- **Single memory selection**: Click to select and view details
- **Simple actions**: Basic edit and delete buttons
- **Basic navigation**: Simple page navigation

### Search Interactions (Basic)
- **Basic search**: Simple text input with search button
- **Basic results**: List of matching memories

### Navigation Patterns (Basic)
- **Simple navigation**: Basic page routing
- **Browser back**: Standard browser back button support

## Accessibility Features

### Keyboard Navigation
- **Tab Order**: Logical flow through all interactive elements
- **Keyboard Shortcuts**: Configurable shortcuts for power users
- **Focus Indicators**: Clear visual focus states
- **Screen Reader**: Proper ARIA labels and semantic markup

### Visual Accessibility (Future Enhancement)
- **High Contrast**: Support for high contrast color themes
- **Text Scaling**: Respect system font size preferences
- **Color Blind**: Avoid color-only information conveyance
- **Dark Mode**: System-based or manual theme switching

## Performance Considerations

### Memory List Optimization
- **Virtual Scrolling**: Handle thousands of memories efficiently
- **Lazy Loading**: Load memory content on demand
- **Search Debouncing**: Prevent excessive API calls during typing
- **Infinite Scroll**: Progressive loading with pagination fallback

### Caching Strategy
- **Memory Cache**: Recently viewed memories cached locally
- **Search Cache**: Cache search results for quick revisits
- **Offline Support**: Basic functionality when offline
- **Service Worker**: Cache static assets and API responses

## Technical Implementation Notes

### State Management
- **Memory List State**: Loading, error, data states
- **Search State**: Query, filters, results, history
- **UI State**: Selected memories, modal states, navigation
- **Sync State**: Changes pending sync with backend

### API Integration
- **RESTful APIs**: Create API endpoints that map to existing CLI commands (HIGH PRIORITY)
- **Error Handling**: Basic error handling and user feedback
- **JSON Responses**: Standard JSON API responses

### Future API Features
- **Real-time Updates**: WebSocket for collaborative features
- **Rate Limiting**: Handle API rate limits gracefully
- **Advanced Error Handling**: Graceful degradation and retry logic

### Data Flow
```
User Input → UI Component → Action → API Call → State Update → UI Re-render
     ↑                                                              ↓
     ←─────────────── Error/Success Feedback ←─────────────────────
```

## TODO: Advanced Features (Future Phases)

### Advanced Interaction Patterns
- **Select Multiple**: Checkbox selection with bulk actions
- **Drag & Drop**: Reorder memories, organize into collections
- **Swipe Actions** (mobile): Swipe left for delete, right for edit
- **Context Menus**: Right-click (desktop) or long-press (mobile)

### Advanced Search Features
- **Search History**: Recent searches dropdown
- **Search Suggestions**: Auto-complete based on memory content
- **Filter Chips**: Visual representation of active filters
- **Advanced Filters**: Date ranges, categories, people filters

### Advanced Navigation
- **Breadcrumbs**: Show current location and path
- **Deep Linking**: Shareable URLs for specific memories/searches
- **Tab Management**: Multiple memory tabs (desktop)

### Performance Optimizations
- **Virtual Scrolling**: Handle thousands of memories efficiently
- **Lazy Loading**: Load memory content on demand
- **Infinite Scroll**: Progressive loading with pagination fallback
- **Caching Strategy**: Memory cache, search cache, offline support

### Collaborative Features
- **Real-time Updates**: WebSocket for live collaboration
- **Memory Collections**: Organize memories into folders/projects
- **Sharing**: Share memories with other users
- **Version History**: Track changes to memories

---

*This UX design specification serves as the foundation for implementing a simple, user-friendly web interface that maintains the core functionality of the Info Agent CLI while being accessible to a broader audience.*
