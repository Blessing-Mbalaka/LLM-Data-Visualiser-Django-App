# LLM Data Visualizer - Django App

A powerful Django web application that uses local LLMs (via Ollama) to automatically generate beautiful data visualizations from uploaded files.

## Features

- 🤖 **Ollama Integration**: Auto-detect and use local LLM models
- 📊 **Smart Visualizations**: AI-powered chart generation using Chart.js
- 📁 **Multiple File Formats**: Support for CSV, Excel, JSON, YAML, and PDF
- 💬 **Conversational Interface**: Chat-based interaction with your data
- 🎨 **Beautiful UI**: Modern dark theme with gold accents
- 🔄 **Real-time Processing**: Track visualization generation progress
- 🚀 **Deployable**: Ready for deployment on Render.com

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) installed and running
- At least one Ollama model pulled (e.g., `llama3.2`)

### Installation

1. **Clone the repository**
   ```bash
   cd LLM-Data-Visualiser-Django-App
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create static files directory**
   ```bash
   python manage.py collectstatic --no-input
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start Ollama**
   ```bash
   # In a separate terminal
   ollama serve
   
   # Pull a model if you haven't already
   ollama pull llama3.2
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

10. **Open your browser**
    - Main app: http://localhost:8000/
    - Ollama config: http://localhost:8000/ollama-config/
    - Admin panel: http://localhost:8000/admin/

## Usage

### Configure Ollama

1. Go to http://localhost:8000/ollama-config/
2. Click "Auto-Detect Models" to scan for available Ollama models
3. Click "Activate" on your preferred model
4. The model indicator in the header will turn green when connected

### Upload and Visualize Data

1. Click or drag-and-drop files to upload (CSV, Excel, JSON, YAML, PDF)
2. Wait for files to be parsed
3. Ask questions like:
   - "Create a bar chart showing sales by month"
   - "Visualize the distribution of categories"
   - "Show me trends over time"
4. The AI will generate appropriate visualizations

## API Endpoints

### Ollama Configuration
- `GET /api/ollama/` - List all configured models
- `POST /api/ollama/auto_detect/` - Auto-detect available models
- `GET /api/ollama/active/` - Get active model
- `POST /api/ollama/{id}/set_active/` - Set model as active
- `POST /api/ollama/pull_model/` - Pull new model from registry

### File Management
- `POST /api/files/` - Upload files
- `GET /api/files/by_session/?session_id={id}` - Get files by session

### Conversations & Visualization
- `POST /api/conversations/chat/` - Send message and generate visualizations
- `GET /api/conversations/by_session/?session_id={id}` - Get conversation history

### Processing Jobs
- `GET /api/jobs/status/?job_id={id}` - Check job status

### Health Check
- `GET /api/health/` - Check system and Ollama connection status

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub**

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables**
   - Set `ALLOWED_HOSTS` to your Render URL
   - Set `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`
   - Set `CREATE_SUPERUSER=1` for initial deployment

4. **Deploy**
   - Click "Apply" to deploy

### Option 2: Manual Setup

1. **Create Web Service**
   - New → Web Service
   - Connect repository
   - Build Command: `./build.sh`
   - Start Command: `gunicorn llm_visualizer.wsgi:application`

2. **Create PostgreSQL Database**
   - New → PostgreSQL
   - Copy connection string to `DATABASE_URL` env var

3. **Set Environment Variables**
   ```
   SECRET_KEY=<generate-secure-key>
   DEBUG=False
   ALLOWED_HOSTS=<your-app>.onrender.com
   DATABASE_URL=<from-database>
   PYTHON_VERSION=3.11.0
   ```

4. **Deploy**

### Important Notes for Deployment

- **Ollama on Render**: Ollama requires a separate server. You'll need to:
  - Deploy Ollama on a separate service with persistent storage
  - Set `OLLAMA_BASE_URL` to point to your Ollama server
  - OR use cloud LLM APIs (Claude, OpenAI) instead of Ollama

- **File Uploads**: Configure persistent storage for media files
- **Static Files**: Handled by WhiteNoise automatically

## Project Structure

```
LLM-Data-Visualiser-Django-App/
├── llm_visualizer/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── visualizer/              # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   ├── services.py         # Ollama & visualization services
│   ├── parsers.py          # File parsers
│   ├── validators.py       # JSON schema validators
│   ├── urls.py             # API URLs
│   └── frontend_urls.py    # Frontend URLs
├── templates/               # Django templates
│   └── visualizer/
│       ├── index.html      # Main visualizer interface
│       └── ollama_config.html  # Ollama configuration page
├── static/                  # Static files
│   └── css/
│       └── style.css       # Main stylesheet
├── media/                   # Uploaded files (created at runtime)
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
├── build.sh                # Render build script
├── render.yaml             # Render deployment config
└── README.md               # This file
```

## Models

- **OllamaConfiguration**: Store Ollama model configurations
- **UploadedFile**: Track uploaded data files
- **Conversation**: Store chat sessions
- **Message**: Individual chat messages
- **Visualization**: Generated chart configurations
- **ProcessingJob**: Track long-running jobs with progress

## Technologies

- **Backend**: Django 5.0, Django REST Framework
- **LLM Integration**: Ollama API
- **Data Processing**: Pandas, openpyxl, PyPDF2, PyYAML
- **Visualization**: Chart.js
- **Database**: PostgreSQL (production) / SQLite (development)
- **Deployment**: Gunicorn, WhiteNoise, Render.com

## Development

### Run Tests
```bash
python manage.py test
```

### Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Access Django Shell
```bash
python manage.py shell
```

## Troubleshooting

### Ollama Not Connected
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_BASE_URL` in settings
- Verify firewall/network settings

### File Upload Errors
- Check `MEDIA_ROOT` permissions
- Verify file size limits in settings
- Ensure supported file format

### Visualization Generation Fails
- Check active model in Ollama config
- Verify model has sufficient context window
- Review Django logs for errors

## License

MIT License - feel free to use this project for any purpose

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.