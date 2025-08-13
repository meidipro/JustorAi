# Legal AI Application

A modern legal AI chat application built with TypeScript, Vite, and FastAPI.

## Features

- ✅ Interactive chat interface
- ✅ Multi-language support (English/Bengali)
- ✅ Dark/Light mode toggle
- ✅ Voice input and speech synthesis
- ✅ Responsive design
- 🚀 **Coming Soon**: Document upload and analysis

## Tech Stack

### Frontend
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Vanilla JS/TS** - No framework dependencies
- **Supabase** - Authentication and database
- **Groq SDK** - AI chat functionality

### Backend (Optional)
- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server

## Deployment

### Deploy to Vercel

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ukilpro
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Build the project**
   ```bash
   npm run build
   ```

4. **Deploy to Vercel**
   - Connect your repository to Vercel
   - Set the build command to: `npm run build`
   - Set the output directory to: `dist`
   - Deploy!

### Environment Variables

Create a `.env.local` file with the following variables:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_GROQ_API_KEY=your_groq_api_key
VITE_DIFY_GENERAL_API_KEY=your_dify_api_key
```

## Development

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

4. **Preview production build**
   ```bash
   npm run preview
   ```

## Backend (Optional)

The Python backend is optional and provides additional features:

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the backend**
   ```bash
   uvicorn backend:app --reload
   ```

## File Structure

```
├── src/
│   ├── pages/           # Application pages
│   ├── components/      # Reusable components
│   ├── locales/         # Internationalization
│   └── style.css       # Global styles
├── public/              # Static assets
├── dist/               # Build output
├── backend.py          # Python backend (optional)
├── requirements.txt    # Python dependencies
├── package.json        # Node dependencies
├── vercel.json        # Vercel configuration
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is private and proprietary.

---

**Note**: Document upload and analysis features are currently under development and will be available in a future release.