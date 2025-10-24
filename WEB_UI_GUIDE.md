# Murder Mystery Web UI Guide

A beautiful, interactive web interface for the Murder Mystery investigation game built with Streamlit.

## 🌐 Overview

The web UI provides a modern, user-friendly interface for playing the Murder Mystery game. It features:

- **Intuitive Setup**: Easy configuration through a web form
- **Visual Investigation Board**: See all characters at a glance
- **Interactive Conversations**: Chat-style interface for interviewing characters
- **Progress Tracking**: Real-time statistics and action counters
- **Responsive Design**: Works on desktop and tablet devices

## 🚀 Quick Start

### Option 1: Using the Launch Script

```bash
./run_web.sh
```

The script will:
1. Create/activate virtual environment
2. Install dependencies
3. Prompt for API key (if not set)
4. Launch the web application

### Option 2: Manual Launch

```bash
# Activate your virtual environment
source venv/bin/activate

# Set your API key
export OPENAI_API_KEY='your-key-here'

# Run Streamlit
streamlit run web_app.py
```

## 📋 Features

### 1. Game Setup Page

Configure your investigation:
- **Environment**: Describe the murder scene
- **Number of Characters**: 3-15 characters
- **Number of Guesses**: How many attempts to identify the killer
- **Action Limit** (Optional): Maximum questions you can ask

The setup page will validate your API key and guide you through configuration.

### 2. Investigation Board

The main investigation interface shows:

**Progress Stats Bar**:
- 🎯 **Guesses Left**: Remaining attempts
- 👥 **Interviewed**: Characters questioned
- ⏱️ **Actions**: Questions asked
- 🔍 **Clues Found**: Investigation log entries

**Character Cards**:
- Color-coded status (victim=red, interviewed=green)
- Character background and details
- Interview buttons for unvisited characters

**Dr. Watson's Narration**:
- Initial crime scene description
- Key evidence and circumstances

### 3. Conversation Interface

Interview characters with a modern chat interface:

**Features**:
- Chat-style message display
- Character introduction (cached for speed)
- Question input field
- 🤖 **Sherlock AI** toggle for AI-generated questions
- Message history
- "Done" button to end conversation

**Tips**:
- Use Sherlock AI for strategic questioning
- Take notes of important responses
- Look for contradictions

### 4. Accusation Page

Make your final guess:

- Review investigation progress
- Select the killer from dropdown
- Make your accusation
- See immediate results

**Note**: Incorrect guesses decrement your remaining attempts!

### 5. Results Page

See how you did:

**Win Screen** (🎉):
- Congratulations message
- Balloons animation
- Investigation summary

**Lose Screen** (❌):
- Reveals the actual killer
- Shows your incorrect guess
- Investigation statistics

**Statistics**:
- Total actions taken
- Characters interviewed
- Clues collected

**Play Again**: Start a fresh investigation

## 🎨 UI Components

### Custom Styling

The web app includes custom CSS for:
- Gradient headers
- Character cards with color-coded borders
- Narration boxes
- Progress indicators
- Success/failure messages

### Chat Interface

Uses Streamlit's chat message components:
- 🕵️ User messages (detective)
- 👤 Character responses

### Forms & Inputs

- Text inputs with placeholders
- Sliders for numeric values
- Checkboxes for options
- Buttons with consistent styling

## 🔧 Technical Details

### Session State Management

The app uses Streamlit session state to manage:

```python
st.session_state = {
    'game_initialized': bool,
    'game_graph': CompiledGraph,
    'conversation_graph': CompiledGraph,
    'game_state': Dict,  # Current game state
    'current_phase': str,  # setup|investigation|conversation|guessing|end
    'selected_character': int,  # Index of character being interviewed
    'conversation_messages': List,  # Chat history
    'investigation_log': List,  # All clues collected
    'llm_messages': List,  # LLM message history for conversation
    'conversation_started': bool,
    'game_result': Dict  # Final game outcome
}
```

### Game Phases

The app operates in distinct phases:

1. **Setup**: Game configuration
2. **Investigation**: Character selection and overview
3. **Conversation**: Individual character interviews
4. **Guessing**: Making accusations
5. **End**: Results and replay

Navigation between phases is managed automatically.

### Integration with Game Logic

The web UI integrates with the core game via `agent/web_utils.py`:

- `initialize_game()`: Creates characters and story
- `start_conversation_with_character()`: Begins interview
- `ask_character_question()`: Handles Q&A
- `check_guess()`: Validates accusations
- `get_investigation_progress()`: Calculates metrics

## 🎯 Best Practices

### For Players

1. **Read Everything**: Dr. Watson's narration contains vital clues
2. **Interview Strategically**: Use action limits wisely
3. **Take Notes**: Use a notepad to track information
4. **Use Sherlock AI**: Get intelligent questions when stuck
5. **Look for Patterns**: Character stories may contradict

### For Developers

1. **Session State**: Always initialize session state variables
2. **Reruns**: Use `st.rerun()` after state changes
3. **Forms**: Use forms for multi-input interactions
4. **Spinners**: Show spinners during LLM calls
5. **Error Handling**: Wrap LLM calls in try-except blocks

## 🐛 Troubleshooting

### "Streamlit command not found"

```bash
pip install streamlit
```

### "API Key Error"

- Enter your key in the sidebar
- Or set environment variable: `export OPENAI_API_KEY='key'`

### "Connection Error"

- Check internet connection
- Verify API key is valid
- Check OpenAI API status

### "Session State Reset"

- This is normal when refreshing the page
- Use the "Play Again" button instead of refreshing

### "Slow Loading"

- First character interview generates embeddings (one-time)
- Subsequent visits use cache (much faster)
- Consider disabling embeddings for development

## 🎨 Customization

### Changing Colors

Edit the CSS in `web_app.py`:

```python
st.markdown("""
<style>
    .main-header {
        color: #1f4788;  /* Change header color */
    }
    .character-card {
        border-left: 5px solid #1f4788;  /* Change card accent */
    }
</style>
""", unsafe_allow_html=True)
```

### Modifying Layout

Adjust column ratios:

```python
col1, col2 = st.columns([3, 1])  # 3:1 ratio
```

### Adding Features

Common additions:
- Save/load game state
- Export investigation log
- Character relationship graph
- Hint system
- Multiple difficulty presets

## 📊 Performance

### Load Times

- **Initial Load**: 5-10 seconds (graph compilation)
- **Character Creation**: 10-15 seconds (LLM generation)
- **First Interview**: 2-3 seconds (embeddings + cache)
- **Subsequent Interviews**: < 1 second (cached)
- **Question Response**: 1-2 seconds (LLM call)

### Optimization Tips

1. **Enable Caching**: Already enabled by default
2. **Limit Characters**: Use 5-7 for faster games
3. **Use Action Limits**: Prevents long sessions
4. **Disable Embeddings**: For development only

```python
# In graph_builder.py
context_mgr = get_context_manager(use_embeddings=False)
```

## 🔐 Security

### API Key Handling

- API keys stored in session state only
- Never logged or persisted
- Cleared on page refresh
- Use environment variables for production

### Data Privacy

- No user data sent to external servers (except OpenAI API)
- Conversation history stays in session
- No analytics or tracking

## 🚀 Deployment

### Local Network Access

```bash
streamlit run web_app.py --server.address 0.0.0.0
```

### Streamlit Cloud

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add `OPENAI_API_KEY` to secrets
4. Deploy!

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "web_app.py"]
```

## 📱 Mobile Support

The web UI is responsive and works on tablets. For best mobile experience:

- Use landscape orientation
- Consider reducing character count
- Use Sherlock AI for easier input

## 🎓 Advanced Usage

### Custom Game Modes

Create presets:

```python
PRESETS = {
    'easy': {'max_characters': 4, 'num_guesses': 5, 'max_actions': 30},
    'normal': {'max_characters': 6, 'num_guesses': 3, 'max_actions': 20},
    'hard': {'max_characters': 10, 'num_guesses': 2, 'max_actions': 15},
}
```

### Analytics Dashboard

Add metrics tracking:

```python
if st.sidebar.checkbox("Show Analytics"):
    st.sidebar.metric("Cache Hit Rate", f"{cache_stats['hit_rate']}")
    st.sidebar.metric("Avg Response Time", "1.2s")
```

### Multi-Player Support

Implement session IDs for multiple concurrent games.

## 📚 Additional Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Game Logic**: See `agent/` modules
- **Terminal UI**: See `app.py` for comparison
- **Performance Guide**: See `PERFORMANCE.md`

## 🤝 Contributing

To add features to the web UI:

1. Modify `web_app.py` for UI changes
2. Add helper functions to `agent/web_utils.py`
3. Update this guide
4. Test all phases of the game
5. Check mobile responsiveness

---

**Happy investigating! 🕵️‍♂️🔍**

*The web UI was built to make the Murder Mystery experience accessible and enjoyable for all users.*

