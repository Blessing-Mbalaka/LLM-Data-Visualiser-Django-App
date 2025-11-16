# Quick Start Guide

## First Time Setup

1. **Install Ollama** (if not already installed)
   ```bash
   # Visit https://ollama.ai and follow installation instructions
   # Or on Linux:
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Ollama and pull a model**
   ```bash
   # Start Ollama server
   ollama serve
   
   # In another terminal, pull a model
   ollama pull llama3.2
   # or
   ollama pull mistral
   ```

3. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults should work for local development)
   ```

5. **Initialize database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Optional: for admin access
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic --no-input
   ```

7. **Run the server**
   ```bash
   python manage.py runserver
   ```

8. **Configure Ollama models**
   - Open http://localhost:8000/ollama-config/
   - Click "Auto-Detect Models"
   - Activate your preferred model

9. **Start visualizing!**
   - Go to http://localhost:8000/
   - Upload a data file (CSV, Excel, JSON, etc.)
   - Ask the AI to create visualizations

## Sample Prompts

Once you've uploaded data, try these prompts:

- "Show me a bar chart of the top 10 items"
- "Create a pie chart showing the distribution of categories"
- "Visualize sales trends over time with a line chart"
- "Compare values across different groups with a bar chart"
- "Show me a radar chart comparing multiple metrics"

## Troubleshooting

### Ollama connection issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it:
ollama serve
```

### Migration errors
```bash
# Reset database (WARNING: deletes all data)
rm db.sqlite3
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic --clear --no-input
```

## Admin Panel

Access Django admin at http://localhost:8000/admin/

You can:
- View uploaded files
- Browse conversations
- Manage Ollama configurations
- Monitor processing jobs

## Development Tips

### Watch logs
```bash
# In the terminal running the server, you'll see logs
# For more detailed logs, enable DEBUG=True in .env
```

### Test API endpoints
```bash
# Check health
curl http://localhost:8000/api/health/

# List models
curl http://localhost:8000/api/ollama/

# Auto-detect models
curl -X POST http://localhost:8000/api/ollama/auto_detect/
```

### Using different Ollama models

```bash
# Pull different models
ollama pull llama3.2
ollama pull mistral
ollama pull codellama

# They'll appear in the config page after auto-detection
```

## Next Steps

1. Upload sample data files to test
2. Experiment with different prompts
3. Try different Ollama models
4. Customize the UI (edit static/css/style.css)
5. Extend the API (edit visualizer/views.py)

For deployment instructions, see README.md
