# CrashLens App — Frontend

#### [Live Demo URL](http://tidb-hackathon-static-site.s3-website-us-east-1.amazonaws.com)

## Overview

CrashLens frontend is a modern dashboard for crash monitoring, RCA visualization, and repository management. It provides real-time insights

## Tech Stack

- React (TypeScript)
- Vite
- Tailwind CSS
- shadcn-ui (component library)
- Framer Motion (animations)
- React Query (data fetching)
- WebSockets (notifications)

## How to Run Locally

1. **Install dependencies:**
   ```sh
   cd crash-lens-app/frontend
   npm install
   ```

2. **Start the development server:**
   ```sh
   npm run dev
   ```

3. **Build for production:**
   ```sh
   npm run build
   ```

## Key Features

- **Dashboard:** Crash stats, severity charts, trends.
- **Crash List:** Filter, search, and view crash details.
- **Crash Detail:** RCA report, log viewer, git diff viewer, PR creation.
- **Repository Manager:** Add/remove repositories.
- **Real-time Notifications:** WebSocket-powered updates.

## Design Highlights

- Responsive, glassmorphic UI with animated gradients
- Modular component structure for scalability
- Integrated diff viewer for code changes
- Markdown rendering for RCA sections
- Context-based state management for repositories

## API Integration

- Connects to backend at `/api/v1`
- Uses [`apiService`](src/services/apiService.ts) for all requests
---
