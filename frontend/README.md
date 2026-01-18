# SK Brands Retail AI - Frontend

Modern, professional dashboard built with Next.js, Tailwind CSS, and Framer Motion for real-time AI agent visualization.

## Design

Inspired by modern enterprise applications with:
- **Clean, light theme** - Professional data-centric design
- **Tailwind CSS** - Utility-first styling with custom configurations
- **Framer Motion** - Smooth, performant animations
- **Lucide React** - Beautiful icon system
- **Glassmorphism** - Subtle backdrop blur effects
- **Gradient accents** - Color-coded agent status

## Features

### Dashboard
- **Real-time Analysis** - Live SSE streaming from backend
- **6 AI Agent Cards** - Color-coded with animated status indicators
- **Progress Stream** - Live message feed with animations
- **Statistics Grid** - 6 metrics with gradient styling
- **Responsive Layout** - 12-column grid system

### Agent Pages
- Individual pages for each of the 6 agents
- Clean, card-based layouts
- Placeholder for analysis results
- Consistent navigation

### Decisions Page
- Human-in-the-Loop approval system
- Approve/Reject actions with animations
- Color-coded decision types
- Real-time updates

### Animations
- **Page Load** - Staggered fade-in with spring physics
- **Agent Cards** - Scale animation when running
- **Progress Bars** - Spring easing with gradient fills
- **Buttons** - Hover scale and shadow effects
- **Lists** - Sequential entrance animations
- **State Changes** - Smooth transitions

## Tech Stack

- **Next.js 16.0.3** - React framework with App Router
- **React 19** - Latest React with improved performance
- **TypeScript** - Full type safety
- **Tailwind CSS 4** - Modern utility-first CSS
- **Framer Motion 12** - Professional animations
- **Lucide React** - Icon library
- **Axios** - API client

## Getting Started

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

App runs at `http://localhost:3000`

### Start Backend

Make sure the backend is running:

```bash
cd ../backend
python run.py
```

Backend runs at `http://localhost:8000`

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Main dashboard
│   ├── layout.tsx            # Root layout
│   ├── agents/
│   │   ├── demand/page.tsx
│   │   ├── trend/page.tsx
│   │   ├── inventory/page.tsx
│   │   ├── replenishment/page.tsx
│   │   ├── pricing/page.tsx
│   │   └── campaign/page.tsx
│   └── decisions/page.tsx    # HITL decisions
├── components/
│   ├── AgentCard.tsx         # Agent status card
│   └── ProgressStream.tsx    # Real-time SSE feed
├── lib/
│   ├── api.ts               # API client
│   └── types.ts             # TypeScript types
└── styles/
    └── globals.css          # Global styles + Tailwind
```

## Design System

### Colors

- **Primary**: Blue (500-600)
- **Success**: Green (500-600)
- **Warning**: Amber/Orange (500-600)
- **Error**: Red (500-600)
- **Neutral**: Gray (50-900)

### Typography

- **System Font Stack** - -apple-system, BlinkMacSystemFont, etc.
- **Font Sizes**: text-xs to text-3xl
- **Font Weights**: Regular, Medium, Semibold, Bold

### Spacing

- **Base Unit**: 4px (Tailwind default)
- **Scale**: 0-96 (0, 1, 2, 3, 4, 6, 8, 12, 16, 24, etc.)
- **Gap**: gap-2 to gap-6 for layouts

### Border Radius

- **rounded-xl** - Large containers (12px)
- **rounded-2xl** - Cards and sections (16px)
- **rounded-full** - Badges and buttons

### Shadows

- **shadow-md** - Default elevation
- **shadow-lg** - Hover states
- **shadow-xl** - Active/focused states

## Components

### AgentCard

Displays agent status with:
- Color-coded border based on status
- Gradient background for active states
- Animated progress bar
- Pulsing indicator for running state
- Checkmark for completed state

**Status Styles:**
- `idle` - Gray border, white background
- `running` - Blue border, blue gradient glow
- `completed` - Green border, green gradient
- `error` - Red border, red gradient

### ProgressStream

Real-time message feed with:
- SSE connection to backend
- Message animations (slide-in from right)
- Color-coded by message type
- Auto-scroll to latest
- Connection status indicator

### Layout

- Sticky navigation with glassmorphism
- Gradient logo and title
- Responsive navigation links
- Max-width container for content

## How It Works

1. **Click "Analyze SK Brands"** - Triggers SSE connection
2. **Backend streams events** - Progress messages in real-time
3. **Agent cards animate** - Status changes with smooth transitions
4. **Progress feed updates** - Live messages appear
5. **Stats update** - On completion, summary stats populate
6. **Navigate to details** - Click agent cards for detail pages

## API Integration

Connects to backend endpoints:
- `POST /orchestrator/run/stream` - Real-time analysis (SSE)
- `GET /stores` - List stores
- `GET /products` - List products
- `GET /decisions/pending` - Pending decisions
- `POST /decisions/{id}/approve` - Approve decision
- `POST /decisions/{id}/reject` - Reject decision

## Responsive Design

- **Mobile**: Single column, stacked layout
- **Tablet**: 2-column grid for cards
- **Desktop**: 8/4 column split (main/sidebar)
- **Large**: Full 12-column grid

## Performance

- **GPU-accelerated animations** - transform and opacity only
- **Lazy loading** - Components load on demand
- **Optimized images** - Next.js image optimization
- **Code splitting** - Automatic route-based splitting
- **60fps animations** - Smooth Framer Motion transitions

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Customization

### Change Colors

Edit `tailwind.config.ts` to modify color palette.

### Adjust Animations

Modify transition values in Framer Motion components:
- `initial` - Starting state
- `animate` - End state
- `transition` - Duration, easing, delay

### Update Grid Layout

Change Tailwind grid classes:
- `grid-cols-{n}` - Number of columns
- `lg:col-span-{n}` - Column span at breakpoint

## Build for Production

```bash
npm run build
npm start
```

## Environment Variables

Create `.env.local` if needed:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Tailwind styles not applying

1. Restart dev server: `npm run dev`
2. Clear Next.js cache: `rm -rf .next`
3. Reinstall: `rm -rf node_modules && npm install`

### Animations laggy

1. Reduce `transition.delay` values
2. Use `layout` prop sparingly in Framer Motion
3. Check browser dev tools Performance tab

### SSE connection fails

1. Verify backend is running on port 8000
2. Check browser console for CORS errors
3. Ensure `/orchestrator/run/stream` endpoint is accessible

## Future Enhancements

- [ ] Data visualization charts (Chart.js)
- [ ] Agent reasoning panel with syntax highlighting
- [ ] Campaign image gallery
- [ ] Export functionality (PDF reports)
- [ ] Advanced filtering and search
- [ ] WebSocket fallback for SSE
- [ ] Dark mode toggle
- [ ] Mobile app view
