# 🚀 Quick Start Guide

Get up and running with Murder Mystery Agent in 5 minutes!

**Version 2.0** - Now with Web UI and Sherlock Holmes theme! 🎩

## Prerequisites

- Python 3.9+ installed
- OpenAI API key

## Installation Steps

### Option 1: Using the Setup Script (macOS/Linux)

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh

# Activate the virtual environment
source venv/bin/activate

# Set your API key
export OPENAI_API_KEY='your-api-key-here'

# Run the game!
python app.py
```

### Option 2: Manual Setup

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENAI_API_KEY='your-api-key-here'

# Run the game!
python app.py
```

## First Game

### Web UI (Recommended) 🌐

1. **Start the web app**: `./run_web.sh` or `streamlit run web_app.py`

2. **Open browser**: Automatically opens at `http://localhost:8501`

3. **Configure**: Use the elegant Sherlock Holmes themed interface!

### Terminal UI 💻

1. **Start the terminal game**: `python app.py`

2. **Configure your mystery**:
   - Environment: Try "Victorian London mansion" or "Modern tech startup"
   - Characters: Start with 5 for your first game
   - Guesses: 3 is a good difficulty level

3. **Play the game**:
   - Read the crime scene description carefully
   - Interview characters by selecting their number
   - Try using Sherlock AI (type 'y') for your first questions
   - Type `EXIT` when done talking to a character
   - Choose `-1` when ready to guess the killer

4. **Solve the mystery**:
   - Review your notes
   - Make your accusation
   - See if you got it right!

## Tips for Your First Game

- **Start with Sherlock AI**: Type 'y' to let the AI ask intelligent questions
- **Take mental notes**: Pay attention to contradictions
- **Don't rush to guess**: Interview at least 2-3 suspects first
- **Look for motives**: Who had a reason?

## Troubleshooting

### "No module named 'agent'"
Make sure you're running from the project root directory.

### "OpenAI API error"
Check that your API key is valid and set correctly:
```bash
echo $OPENAI_API_KEY  # Should display your key
```

### Import errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Example Game Configuration

**Easy Mode** (Good for first-time players):
- Environment: "Small village pub"
- Characters: 4
- Guesses: 5

**Normal Mode** (Balanced experience):
- Environment: "Corporate office building"
- Characters: 5-6
- Guesses: 3

**Hard Mode** (For experienced detectives):
- Environment: "Large masquerade ball"
- Characters: 8-10
- Guesses: 2

## Next Steps

Once you've played a few games:
- Try different environments and settings
- Experiment with asking your own questions
- Increase the number of characters for more complexity
- Read the full README.md for customization options

---

**Need help?** Check the full [README.md](README.md) for detailed documentation.

**Ready to investigate?** `python app.py` 🔍

