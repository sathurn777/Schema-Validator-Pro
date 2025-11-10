# Schema Validator Pro - Web Application

[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-v4-38bdf8.svg)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)

A modern web application for generating and validating Schema.org JSON-LD structured data.

## ✨ Features

- **Schema Generator** - Interactive forms for Article and Product schemas
- **Schema Validator** - Real-time validation with syntax highlighting
- **Live Preview** - See generated JSON-LD in real-time
- **Copy to Clipboard** - One-click copy for easy integration
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark Mode** - Beautiful dark theme support
- **Modern UI** - Built with shadcn/ui components

## 🚀 Tech Stack

- **Framework**: Next.js 16 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS v4
- **Components**: shadcn/ui
- **Validation**: @schema-validator-pro/core
- **TypeScript**: Full type safety

## 📦 Installation

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

## 🛠️ Development

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Project Structure

```
web-app/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Homepage
│   ├── generator/         # Schema generator pages
│   └── validator/         # Schema validator page
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   └── schema/           # Schema-specific components
└── lib/                  # Utilities and helpers
```

### Available Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm start` - Start production server
- `pnpm lint` - Run ESLint

## 🌐 Deployment

### Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/sathurn777/Schema-Validator-Pro)

```bash
vercel deploy --prod
```

### Netlify

```bash
pnpm build
# Upload .next/ to Netlify
```

### Docker

```bash
docker build -t schema-validator-pro-web .
docker run -p 3000:3000 schema-validator-pro-web
```

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)

## 📄 License

MIT License - See [LICENSE](../../LICENSE) for details
