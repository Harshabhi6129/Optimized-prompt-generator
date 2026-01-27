# 🔬 AI Prompt Refinement

## 🆓 100% FREE - Powered by Google Gemini

This application uses Google Gemini 1.5 Flash (FREE tier) for ALL AI operations:
- Custom filter generation
- Prompt refinement
- Interactive chat

### Get Your FREE API Key
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key to .env.local

### Free Tier Limits
- 15 requests per minute
- 1 million tokens per minute  
- 1,500 requests per day

More than enough for personal use!

Transform your prompts with AI-powered refinement and custom filters.

## ✨ Features

- 🤖 **AI-Powered Optimization** - Uses Gemini 1.5 Flash for intelligent prompt refinement
- 🎯 **Dynamic Custom Filters** - Automatically generates domain-specific filters
- 📁 **Multi-Format File Support** - Process PDFs, DOCX, and images with OCR
- 💬 **Interactive Chat** - Built-in chat interface with Gemini 1.5 Flash
- 🎨 **Modern UI** - Responsive design with dark mode support
- ⚡ **Real-Time Processing** - Instant feedback and streaming responses
- 🆓 **100% Free** - Uses only Google Gemini's free tier

## 📋 Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org/)
- **Google Gemini API Key** - [Get yours](https://makersuite.google.com/app/apikey) (100% FREE)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-prompt-refinement
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Setup environment variables**
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` and add your API key:
   ```env
   GOOGLE_GEMINI_API_KEY=your-gemini-key-here
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🌐 Deployment

### Deploy to Vercel (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your repository

3. **Add Environment Variables**
   - `GOOGLE_GEMINI_API_KEY`
   - `NEXT_PUBLIC_APP_URL` (your Vercel URL)

4. **Deploy!**
   - Vercel will automatically build and deploy

### Manual Deployment

```bash
npm run build
npm start
```

## 🛠️ Tech Stack

### Core
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **React 19** - Latest React features

### AI/ML
- **Google Gemini 1.5 Flash** - All AI operations (chat, filters, refinement)

### File Processing
- **Tesseract.js** - OCR for images
- **pdf-parse** - PDF text extraction
- **mammoth** - DOCX text extraction

### Validation & Forms
- **Zod** - Schema validation
- **react-hook-form** - Form management

### UI Components
- **lucide-react** - Icon library
- **next-themes** - Dark mode support
- **class-variance-authority** - Component variants

## 📁 Project Structure

```
ai-prompt-refinement/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/               # API routes
│   │   │   ├── chat/          # Chat endpoint
│   │   │   ├── generate-filters/  # Filter generation
│   │   │   ├── refine-prompt/ # Prompt refinement
│   │   │   └── upload/        # File upload
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── ui/               # UI primitives
│   │   ├── prompt-refinement-app.tsx
│   │   ├── chat-interface.tsx
│   │   ├── filter-panel.tsx
│   │   ├── file-upload.tsx
│   │   └── theme-provider.tsx
│   ├── lib/                   # Utilities & integrations
│   │   ├── gemini.ts         # Gemini API
│   │   ├── openai.ts         # OpenAI API
│   │   ├── file-processor.ts # File processing
│   │   └── utils.ts          # Helper functions
│   └── types/                 # TypeScript types
│       └── index.ts
├── public/                    # Static assets
├── .env.local.example        # Environment template
├── next.config.js            # Next.js config
├── tailwind.config.ts        # Tailwind config
├── tsconfig.json             # TypeScript config
└── package.json              # Dependencies
```

## 📖 Usage

1. **Enter Your Prompt**
   - Type your initial idea or question
   - Optionally upload files (PDF, DOCX, images)

2. **Generate Custom Filters** (Optional)
   - Click "Generate Custom Filters"
   - AI analyzes your prompt and creates relevant filters

3. **Configure Preferences**
   - Adjust default filters (tone, format, detail level)
   - Fill in custom filters if generated

4. **Refine Your Prompt**
   - Choose "Refine Directly" for quick refinement
   - Or "Refine with All Filters" for detailed optimization

5. **Start Chatting**
   - Your refined prompt is automatically loaded
   - Have an interactive conversation with AI

## 🔑 Getting API Key

### Google Gemini (FREE)
1. Visit [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and save it securely

**Note:** Gemini 1.5 Flash is completely free with generous limits!

## 🧪 Development

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm start        # Start production server
npm run lint     # Run ESLint
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_GEMINI_API_KEY` | Gemini API key for all AI operations | Yes |
| `NEXT_PUBLIC_APP_URL` | Application URL | No |

## 📚 Documentation

- [Setup Guide](./SETUP.md) - Detailed setup instructions
- [Quick Start](./QUICKSTART.md) - Get started quickly
- [API Reference](./API_REFERENCE.md) - API endpoints documentation
- [Component Showcase](./COMPONENT_SHOWCASE.md) - UI components guide

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - The React Framework
- [Vercel](https://vercel.com/) - Hosting platform

- [Google](https://ai.google.dev/) - Gemini AI
- [Tailwind CSS](https://tailwindcss.com/) - Styling framework
- [shadcn/ui](https://ui.shadcn.com/) - Component patterns

## 📧 Support

For support, email your-email@example.com or open an issue on GitHub.

---

Made with ❤️ using Next.js and AI
