# 🚀 GETTING STARTED - 5 MINUTES TO VISUALIZATION

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.11 or higher
- ✅ pip (Python package manager)
- ✅ Git (optional, for version control)

## Installation Steps

### 1️⃣ Install Ollama (One-Time Setup)

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai

**Verify Installation:**
```bash
ollama --version
```

### 2️⃣ Start Ollama and Pull a Model

```bash
# Start Ollama server (in a terminal, keep running)
ollama serve

# In another terminal, pull a model
ollama pull llama3.2

# Or try other models
# ollama pull mistral
# ollama pull codellama
```

### 3️⃣ Set Up the Django Application

```bash
# Navigate to project directory
cd LLM-Data-Visualiser-Django-App

# Run automated setup script
./setup.sh

# Or manually:
# python -m venv venv
# source venv/bin/activate  # Windows: venv\Scripts\activate
# pip install -r requirements.txt
# python manage.py migrate
# python manage.py collectstatic --no-input
```

### 4️⃣ Start the Django Server

```bash
# Activate virtual environment (if not already)
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run the development server
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### 5️⃣ Configure Ollama Models

1. Open browser: http://localhost:8000/ollama-config/
2. Click **"🔍 Auto-Detect Models"**
3. Wait for models to be detected
4. Click **"Activate"** on your preferred model (e.g., llama3.2)
5. Wait for green status indicator

### 6️⃣ Start Visualizing!

1. Go to: http://localhost:8000/
2. Upload a data file:
   - Try the sample files in `sample_data/`
   - Or use your own CSV, Excel, JSON file
3. Ask the AI to create visualizations:
   - "Create a bar chart showing sales by month"
   - "Show me a pie chart of categories"
   - "Visualize the trends over time"

## 🎯 Quick Test

### Test with Sample Data

```bash
# The project includes sample data files
# Upload: sample_data/sales_data.csv

# Then try these prompts:
# - "Show me sales trends over the year"
# - "Create a bar chart comparing profit by region"
# - "Visualize monthly sales, expenses, and profit together"
```

## 📋 Common Commands

```bash
# Start Django server
python manage.py runserver

# Create admin superuser
python manage.py createsuperuser

# Access admin panel
# http://localhost:8000/admin/

# Run migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Access Django shell
python manage.py shell
```

## 🔍 Verify Everything Works

### Health Check

```bash
curl http://localhost:8000/api/health/

# Expected response:
# {
#   "status": "healthy",
#   "ollama_connected": true,
#   "active_model": "llama3.2"
# }
```

### Test API Endpoints

```bash
# List Ollama models
curl http://localhost:8000/api/ollama/

# Auto-detect models
curl -X POST http://localhost:8000/api/ollama/auto_detect/

# Get active model
curl http://localhost:8000/api/ollama/active/
```

## 🚨 Troubleshooting

### Problem: "Ollama not connected"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it:
ollama serve

# Check if models are available:
ollama list
```

### Problem: "No models found"

**Solution:**
```bash
# Pull a model
ollama pull llama3.2

# Then refresh the Ollama config page
# Click "Auto-Detect Models" again
```

### Problem: "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Problem: "Database errors"

**Solution:**
```bash
# Reset database (WARNING: deletes all data)
rm db.sqlite3
python manage.py migrate
```

### Problem: "Static files not loading"

**Solution:**
```bash
python manage.py collectstatic --clear --no-input
```

## 🎓 Learning Path

1. **Start Simple**
   - Upload `sample_data/sales_data.csv`
   - Ask for basic charts
   - Experiment with different prompts

2. **Try Different Data**
   - Upload `sample_data/products.json`
   - Try more complex visualizations
   - Ask for multiple charts

3. **Explore Features**
   - Test different chart types
   - Use the admin panel
   - Check the conversation history

4. **Customize**
   - Modify colors in `static/css/style.css`
   - Adjust prompts in `visualizer/services.py`
   - Add your own chart types

## 📚 Next Steps

- Read **PROJECT_SUMMARY.md** for complete overview
- Check **README.md** for deployment instructions
- Review **QUICKSTART.md** for detailed setup
- Explore the API documentation in README
- Try deploying to Render.com

## 💡 Tips for Best Results

1. **Use clear prompts**: Be specific about what you want to visualize
2. **Quality data**: Clean, structured data works best
3. **Right model**: llama3.2 or mistral work well for visualizations
4. **Multiple requests**: Ask for one type of chart at a time initially
5. **Check samples**: Use the sample_data folder for inspiration

## ✅ You're Ready!

If you can:
- ✅ Access http://localhost:8000/
- ✅ See green status for Ollama
- ✅ Upload a file
- ✅ Generate a chart

**You're all set! Start exploring your data! 🎉📊**

---

For help: Open an issue on GitHub or check the troubleshooting sections in README.md
