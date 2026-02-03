# EverythingInBot

🌟 **The Ultimate Telegram Super-App** - 10 Powerful Modules in One Bot

## 🚀 Features

### 🤖 M1: AI Engine Hub
- Multi-AI support (GPT-4o, Claude 3.5, Gemini 1.5, Llama 3)
- Text chat, vision, image generation
- Document analysis (PDF, Resume, Logs)

### 🔐 M2: Breach Check
- Email breach checking
- Password exposure detection
- Security recommendations
- Powered by XposedOrNot API

### 📚 M3: Courses & Learning
- Ethical Hacking, Cybersecurity, Programming
- Video lessons, PDFs, quizzes
- Progress tracking

### 💼 M4: Jobs & Careers
- IT, Non-IT, Government, Remote jobs
- AI Resume Builder
- AI Cover Letter Generator
- Interview Simulator

### 🛠 M5: Tools & Utilities
- **PDF**: Merge, Split, Compress, OCR
- **Image**: Background removal, Resize, Convert
- **Text**: Summarize, Rephrase, Format
- **URL**: Shortener, Safety checker
- **QR/Barcode**: Generate & Scan
- **Converters**: PDF↔Word, Image↔Text, Audio↔Text
- **Calculators**: GST, EMI, Salary, Currency

### ✅ M6: Productivity Tools
- To-Do Manager, Notes, Habit Tracker
- Reminders, Daily Goals, Journal

### 👨‍💻 M7: Developer Tools
- JSON/JWT/Base64 utilities
- Regex generator, API tester
- Cron builder, Git/Docker cheat sheets

### 🔒 M8: Cybersecurity Tools
- Nmap analyzer, Burp parser
- Hash identifier, Log analyzer
- Threat Intelligence (CVE/KEV)

### 🔍 M9: OSINT Tools
- WHOIS/DNS Lookup
- IP Geolocation
- Username availability (legal & safe)

### 🎮 M10: Entertainment
- AI Story/Joke/Poem generators
- Games: Quiz, Trivia, Riddles

---

## 🏗️ Architecture

### Technology Stack
- **Bot**: Aiogram 3.x (Webhook mode)
- **Backend**: FastAPI (async)
- **Database**: MongoDB Atlas (Motor driver)
- **Cache/Queue**: Redis (Render Key-Value)
- **Worker**: Celery (background tasks)
- **Deployment**: Render.com

### Project Structure
```
EverythingInBot/
├── app/                    # Main application
│   ├── main.py            # FastAPI + Aiogram entry
│   ├── config.py          # Configuration
│   ├── database.py        # MongoDB connection
│   ├── redis_client.py    # Redis connection
│   ├── bot/               # Telegram bot
│   │   ├── handlers/      # Command handlers (M1-M10)
│   │   ├── keyboards/     # Inline keyboards
│   │   └── middlewares/   # Auth, rate limiting
│   ├── api/               # FastAPI routers
│   ├── models/            # Pydantic models
│   └── services/          # Business logic
├── worker/                # Celery workers
│   ├── celery_app.py
│   └── tasks.py
├── render.yaml            # Render Blueprint
└── requirements.txt
```

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- MongoDB Atlas account
- Telegram Bot Token
- API Keys (OpenAI, Claude, Gemini, etc.)

### Local Development

1. **Clone repository**
```bash
git clone <your-repo-url>
cd EverythingInBot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Run locally**
```bash
# Start FastAPI + Bot
uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A worker.celery_app worker --loglevel=info
```

---

## 🚀 Deployment to Render.com

### One-Click Deployment

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Connect to Render**
- Go to [Render Dashboard](https://dashboard.render.com)
- Click "New" → "Blueprint"
- Connect your GitHub repository
- Select `render.yaml`

3. **Configure Environment Variables**
Set these in Render dashboard:
- `TELEGRAM_BOT_TOKEN`
- `MONGODB_URI` (MongoDB Atlas connection string)
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_AI_API_KEY`
- `XPOSEDORNOT_API_KEY`
- Payment keys (Razorpay, Stripe)

4. **Deploy**
- Click "Apply"
- Wait for deployment to complete

5. **Set Webhook**
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-app.onrender.com/webhook/<YOUR_BOT_TOKEN>"
```

---

## 🔧 Configuration

### MongoDB Atlas Setup
1. Create free M0 cluster
2. Create database user
3. Whitelist IP: `0.0.0.0/0` (for Render)
4. Copy connection string to `MONGODB_URI`

### Render Redis
- Automatically created via `render.yaml`
- Connection string auto-injected as `REDIS_URL`

---

## 📚 API Documentation

Once deployed, visit:
- **API Docs**: `https://your-app.onrender.com/docs`
- **Health Check**: `https://your-app.onrender.com/health`

---

## 🔐 Security

- All API keys stored as environment variables
- Webhook secured with secret token
- Password hashing (SHA-1) for breach checks
- User consent required for OSINT/Breach tools
- Rate limiting per tier (Guest/Free/Pro)

---

## 💰 Subscription Tiers

| Tier | Requests/Day | Features |
|------|--------------|----------|
| 🆓 **Free** | 5 | Basic features |
| ⭐ **Pro** | Unlimited | All features + priority support |

---

## 🛠 Development

### Adding New Module
1. Create handler in `app/bot/handlers/`
2. Register router in `app/bot/dispatcher.py`
3. Add button to `app/bot/keyboards/main_menu.py`
4. Create Celery tasks if needed in `worker/tasks.py`

### Running Tests
```bash
pytest tests/ -v
```

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Support

- **Issues**: GitHub Issues
- **Telegram**: @YourSupportBot
- **Email**: support@example.com

---

## 🎯 Roadmap

- [ ] Complete all 10 modules
- [ ] Telegram Mini App (React dashboard)
- [ ] Payment integration (Razorpay, Stripe)
- [ ] Admin panel
- [ ] Analytics dashboard
- [ ] Multi-language support

---

**Built with ❤️ for the Telegram community**
