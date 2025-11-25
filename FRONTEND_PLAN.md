# Next.js Frontend Implementation Plan

## Overview

Modern, production-ready Next.js 14 frontend for Mocktailverse GenAI platform.

**Tech Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- React Query for data fetching
- Deployed on CloudFront + S3

---

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── search/
│   │   └── page.tsx            # Semantic search UI
│   ├── chat/
│   │   └── page.tsx            # AI Bartender chat
│   ├── explore/
│   │   └── page.tsx            # Browse cocktails
│   └── api/
│       ├── search/route.ts     # Proxy to API Gateway
│       ├── rag/route.ts        # RAG endpoint proxy
│       └── agent/route.ts      # Agent endpoint proxy
│
├── components/
│   ├── ui/                     # Shadcn components
│   ├── SearchBar.tsx           # Semantic search input
│   ├── ChatInterface.tsx       # Agent chat UI
│   ├── CocktailCard.tsx        # Recipe display
│   ├── VectorVisualization.tsx # Embedding viz
│   └── ArchitectureDiagram.tsx # System diagram
│
├── lib/
│   ├── api-client.ts           # API Gateway client
│   ├── types.ts                # TypeScript types
│   └── utils.ts                # Helper functions
│
├── public/
│   └── assets/                 # Static assets
│
└── next.config.js              # Next.js config
```

---

## Pages

### 1. Home Page (`/`)

**Purpose**: Landing page with hero section and feature highlights

**Components:**
```tsx
- Hero section with animated gradient
- Feature cards (Semantic Search, RAG, AI Agent)
- Architecture diagram (interactive)
- Live metrics (total cocktails, embeddings, searches)
- CTA buttons → Search, Chat, Explore
```

**Design:**
- Dark mode by default
- Glassmorphism effects
- Smooth animations (Framer Motion)
- Responsive grid layout

---

### 2. Semantic Search (`/search`)

**Purpose**: Vector-powered cocktail search

**Features:**
```tsx
- Search bar with autocomplete
- Real-time search as you type (debounced)
- Results with relevance scores
- Filters: category, alcoholic/non-alcoholic
- Sort: relevance, name, popularity
- Infinite scroll pagination
```

**UI Flow:**
```
User types: "refreshing summer drinks"
    ↓
Debounce 300ms
    ↓
POST /api/search { query: "..." }
    ↓
Display results with:
  - Cocktail name
  - Image
  - Relevance score (0-1)
  - Quick preview
  - "View Details" button
```

**API Integration:**
```typescript
// lib/api-client.ts
export async function searchCocktails(query: string) {
  const response = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  return response.json();
}
```

---

### 3. AI Bartender Chat (`/chat`)

**Purpose**: Conversational interface with Bedrock Agent

**Features:**
```tsx
- Chat interface (WhatsApp-style)
- Multi-turn conversations
- Typing indicators
- Message history
- Suggested prompts
- Copy/share responses
```

**Example Conversation:**
```
User: "I want something tropical but not too sweet"

Agent: "I'd recommend a Tropical Mojito! Here's why:
       - Fresh lime balances sweetness
       - Mint adds refreshing notes
       - Pineapple juice for tropical flavor
       
       Would you like the full recipe?"

User: "Yes, and make it spicy"

Agent: "Great choice! I'll add jalapeño to the recipe..."
```

**UI Components:**
```tsx
<ChatInterface>
  <MessageList messages={messages} />
  <InputBox onSend={handleSend} />
  <SuggestedPrompts prompts={suggestions} />
</ChatInterface>
```

---

### 4. Explore (`/explore`)

**Purpose**: Browse all cocktails with filters

**Features:**
```tsx
- Grid view of all cocktails
- Filter sidebar:
  - Category (Cocktail, Shot, Punch, etc.)
  - Type (Alcoholic, Non-Alcoholic)
  - Glass type
  - Ingredients
- Sort options
- Pagination
- Recipe detail modal
```

**Layout:**
```
┌─────────────────────────────────────────┐
│  Filters (sidebar)  │  Grid (3 columns) │
│  ─────────────────  │  ───────────────  │
│  □ Category         │  [Card] [Card]    │
│  □ Type             │  [Card] [Card]    │
│  □ Glass            │  [Card] [Card]    │
│                     │                   │
└─────────────────────────────────────────┘
```

---

## Components

### SearchBar Component

```tsx
// components/SearchBar.tsx
'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';
import { useDebounce } from '@/lib/hooks';

export function SearchBar({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery) {
      onSearch(debouncedQuery);
    }
  }, [debouncedQuery]);

  return (
    <div className="relative">
      <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for cocktails..."
        className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </div>
  );
}
```

### ChatInterface Component

```tsx
// components/ChatInterface.tsx
'use client';

import { useState } from 'react';
import { Send } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] border rounded-lg">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && <div className="text-gray-400">AI is thinking...</div>}
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask the AI Bartender..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
```

### CocktailCard Component

```tsx
// components/CocktailCard.tsx
interface CocktailCardProps {
  name: string;
  category: string;
  image?: string;
  relevanceScore?: number;
  onClick: () => void;
}

export function CocktailCard({ 
  name, 
  category, 
  image, 
  relevanceScore,
  onClick 
}: CocktailCardProps) {
  return (
    <div
      onClick={onClick}
      className="group cursor-pointer rounded-lg border border-gray-200 
                 hover:shadow-lg transition-all duration-200"
    >
      {/* Image */}
      <div className="aspect-square overflow-hidden rounded-t-lg bg-gray-100">
        {image ? (
          <img
            src={image}
            alt={name}
            className="h-full w-full object-cover group-hover:scale-105 transition-transform"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            🍹
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-lg">{name}</h3>
        <p className="text-sm text-gray-500">{category}</p>
        
        {relevanceScore !== undefined && (
          <div className="mt-2 flex items-center gap-2">
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full"
                style={{ width: `${relevanceScore * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-500">
              {(relevanceScore * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## API Routes (Next.js)

### Search Proxy

```typescript
// app/api/search/route.ts
import { NextRequest, NextResponse } from 'next/server';

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${API_GATEWAY_URL}/v1/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Search failed' },
      { status: 500 }
    );
  }
}
```

### Agent Proxy

```typescript
// app/api/agent/route.ts
import { NextRequest, NextResponse } from 'next/server';

const API_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL;

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json();
    
    const response = await fetch(`${API_GATEWAY_URL}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Agent request failed' },
      { status: 500 }
    );
  }
}
```

---

## Deployment to CloudFront

### Build Configuration

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Static export for S3
  images: {
    unoptimized: true // Required for static export
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
  }
};

module.exports = nextConfig;
```

### Deployment Script

```bash
#!/bin/bash
# deploy-frontend.sh

set -e

echo "Building Next.js app..."
npm run build

echo "Syncing to S3..."
aws s3 sync out/ s3://mocktailverse-frontend --delete

echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_DIST_ID \
  --paths "/*"

echo "✅ Deployment complete!"
echo "URL: https://mocktailverse.dev"
```

### Terraform for CloudFront

```hcl
# terraform/cloudfront.tf

resource "aws_s3_bucket" "frontend" {
  bucket = "mocktailverse-frontend"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "404.html"
  }
}

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100" # US, Canada, Europe

  origin {
    domain_name = aws_s3_bucket_website_configuration.frontend.website_endpoint
    origin_id   = "S3-mocktailverse-frontend"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-mocktailverse-frontend"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

output "cloudfront_url" {
  value = aws_cloudfront_distribution.frontend.domain_name
}
```

---

## Design System

### Color Palette

```css
/* Tailwind config */
colors: {
  primary: {
    50: '#f0f9ff',
    500: '#3b82f6',
    900: '#1e3a8a'
  },
  accent: {
    500: '#8b5cf6' // Purple for AI features
  },
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444'
}
```

### Typography

```css
font-family: {
  sans: ['Inter', 'system-ui', 'sans-serif'],
  mono: ['Fira Code', 'monospace']
}
```

### Component Library

Use **Shadcn/ui** for:
- Buttons
- Input fields
- Cards
- Modals
- Dropdowns
- Tooltips

---

## Performance Optimizations

1. **Image Optimization**
   - Use Next.js Image component
   - Lazy load images
   - WebP format

2. **Code Splitting**
   - Dynamic imports for heavy components
   - Route-based splitting (automatic)

3. **Caching**
   - CloudFront edge caching
   - React Query for API caching
   - Service worker for offline support

4. **Bundle Size**
   - Tree shaking
   - Remove unused Tailwind classes
   - Analyze bundle with `@next/bundle-analyzer`

---

## Timeline

**Week 1**: Setup + Core Pages
- Initialize Next.js project
- Setup Tailwind + Shadcn
- Build Home, Search, Explore pages

**Week 2**: AI Features
- Chat interface
- API integration
- Real-time updates

**Week 3**: Polish + Deploy
- Animations
- Responsive design
- CloudFront deployment
- Testing

---

## Cost Estimate

| Service | Monthly Cost |
|---------|-------------|
| CloudFront | $0.85 (10GB transfer) |
| S3 | $0.02 (1GB storage) |
| **Total** | **$0.87/month** |

Frontend adds less than $1/month to total system cost!

---

## Success Metrics

- **Performance**: Lighthouse score > 90
- **Accessibility**: WCAG AA compliant
- **SEO**: Meta tags, sitemap, robots.txt
- **Mobile**: Fully responsive
- **Load Time**: < 2s on 3G

---

This plan gives you a production-ready, modern frontend that showcases the GenAI backend beautifully.
