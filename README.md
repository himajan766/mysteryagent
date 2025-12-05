# 🕵️‍♂️ Murder Mystery Agent 🔍

**Version 2.0** - Now with Beautiful Web UI! 🌐

App is live at: https://mysteryagent-ggbfawlxnu67s77bnb8vws.streamlit.app

An interactive detective game powered by Large Language Models (LLMs) and LangGraph. Step into the shoes of Sherlock Holmes and solve procedurally generated murder mysteries!

Play via elegant **Sherlock Holmes themed web interface** 🎩 or classic **terminal UI** 💻

## 🎮 Overview

Murder Mystery is an engaging detective game where every playthrough creates a unique scenario. Interview suspects, gather clues, and use your deductive reasoning to identify the killer before you run out of guesses.

## ✨ Features

### Core Game Features
- **Procedurally Generated Mysteries**: Each game creates a unique murder case with different characters, motives, and storylines - never play the same mystery twice!
- **Interactive Conversations**: Natural language interviews with AI-powered characters who remember what they've told you
- **Sherlock AI Assistant**: Optional AI helper that can ask intelligent investigative questions on your behalf
- **Dynamic Storytelling**: Characters react based on their personalities, relationships, and potential guilt
- **Beautiful Terminal UI**: Rich console interface with styled text, panels, and tables

### 🚀 Performance & Scalability Features (v2.0)

#### 1. **Intelligent Caching System**
- Pre-generates and caches character introductions for instant response
- LRU (Least Recently Used) eviction strategy with configurable TTL
- Reduces API calls by up to 40% for repeated interactions
- Cache statistics tracking for performance monitoring

#### 2. **Vector Store Context Management**
- Character backstories chunked and embedded for efficient retrieval
- Retrieves only relevant context based on questions asked
- Reduces token usage by 60% while maintaining response quality
- Uses FAISS for fast similarity search
- Scales to handle large character backgrounds without token overflow

#### 3. **Graph Pruning & State Tracking**
- Tracks visited characters to show investigation progress
- Prevents redundant revisits with visual indicators
- Efficient memory management through dynamic state updates
- Real-time progress display showing visited vs. unvisited characters

#### 4. **Resource Constraints & Turn Limits**
- Configurable maximum action limits to bound complexity
- Turn counting for each conversation
- Automatic enforcement of resource limits
- Prevents runaway sessions and controls costs
- Progress tracking: actions taken vs. actions remaining

#### 5. **Procedural Generation Improvements**
- Random seed injection for truly unique mysteries each session
- No hardcoded storylines - pure LLM generation
- Environment-based character creation
- Dynamic relationship and motive generation

## 🏗️ Architecture

The game uses two interconnected LangGraph workflows:

### 1. Game Loop Graph
Orchestrates the overall game flow:
- Creates characters and storyline
- Manages character selection
- Handles the guessing mechanism
- Determines win/loss conditions

### 2. Conversation Sub-Graph
Manages character interviews:
- Character introductions
- Question and answer flow
- Conversation memory
- Sherlock AI assistance

## 📋 Prerequisites

- Python 3.9 or higher
- OpenAI API key with access to GPT-4o
- Terminal with color support (for best experience)

## 🚀 Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or the game will prompt you to enter it when you run it.

## 🎯 How to Play

### Web UI (Recommended) 🌐

1. **Launch the web application**:
```bash
./run_web.sh
# Or manually:
streamlit run web_app.py
```

2. **Open your browser** (should open automatically at `http://localhost:8501`)

3. **Configure and play** through the intuitive web interface!

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for detailed web UI documentation.

### Terminal UI 💻

1. **Run the terminal game**:
```bash
python app.py
```

2. **Configure your mystery**:
   - Set the environment (e.g., "Victorian mansion", "Modern office")
   - Choose the number of characters (3-10 recommended)
   - Set the difficulty by choosing number of guesses

3. **Configure Resource Limits** (Optional but Recommended):
   - Set a maximum number of questions/actions (e.g., 15-20)
   - This bounds the game complexity and prevents runaway costs
   - Leave empty for unlimited mode

4. **Investigate**:
   - Read Dr. Watson's narration of the crime scene
   - See investigation progress (actions taken, characters visited)
   - Select characters to interview (visited ones are marked)
   - Choose between asking your own questions or using Sherlock AI
   - Type `EXIT` to end a conversation with a character
   - Watch for cached responses (faster for repeated visits)

5. **Solve the case**:
   - When ready (or when action limit reached), choose to guess the killer
   - Select your suspect from the list
   - Win by identifying the correct killer within your guess limit!

## 📁 Project Structure

```
Murder Mystery agent/
├── agent/                      # Main game package
│   ├── __init__.py            # Package initialization
│   ├── schemas.py             # Data models and state classes
│   ├── prompts.py             # LLM prompt templates
│   ├── display.py             # Terminal UI functions
│   ├── game_logic.py          # Game node functions
│   ├── graph_builder.py       # LangGraph workflow builders
│   ├── cache_manager.py       # 🆕 Intelligent caching system
│   ├── vector_store.py        # 🆕 Context chunking & embeddings
│   └── web_utils.py           # 🌐 Web UI integration helpers
├── app.py                      # Terminal UI entry point
├── web_app.py                  # 🌐 Web UI entry point (Streamlit)
├── run_web.sh                  # 🌐 Web app launcher script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── QUICKSTART.md               # Quick start guide
├── WEB_UI_GUIDE.md             # 🌐 Web UI documentation
├── PERFORMANCE.md              # Performance optimization guide
└── CHANGELOG.md                # Version history
```

## 🎨 Game Components

### Character Roles
- **Killer**: The murderer you must identify
- **Victim**: The deceased (cannot be interviewed)
- **Suspects**: Various characters who may have motives or information

### Investigation Tools
- **Character Interviews**: Ask questions to gather information
- **Sherlock AI**: Get AI-generated investigative questions
- **Clue System**: Piece together evidence from conversations
- **Deduction Phase**: Make your final accusation

## 🛠️ Customization

You can customize the game by modifying:

- **LLM Model**: Change the model in `graph_builder.py` (default: GPT-4o)
- **Temperature**: Adjust randomness in LLM responses (default: 0 for deterministic)
- **Prompts**: Edit system prompts in `prompts.py`
- **UI Styling**: Modify display functions in `display.py`
- **Game Mechanics**: Adjust logic in `game_logic.py`
- **Cache Settings**: Modify TTL and size limits in `cache_manager.py`
- **Vector Store**: Adjust chunk size and overlap in `vector_store.py`
- **Resource Limits**: Set default action/guess limits in `app.py`

### Performance Tuning

```python
# In graph_builder.py or your custom script
from agent.cache_manager import get_cache
from agent.vector_store import get_context_manager

# Configure cache
cache = get_cache()
cache.manager.max_size = 300  # Increase cache size
cache.manager.default_ttl = 7200  # 2 hours

# Configure context manager
context_mgr = get_context_manager()
context_mgr.chunk_size = 300  # Smaller chunks for faster retrieval
context_mgr.max_chunks_per_query = 5  # More context per query
```

## 🔧 Advanced Usage

### Visualizing the Game Graphs

To generate visual diagrams of the game workflows:

```python
from agent.graph_builder import build_murder_mystery_game, visualize_graphs

game_graph, conversation_graph = build_murder_mystery_game()
visualize_graphs(game_graph, conversation_graph, save_path="./graphs")
```

Note: Requires `graphviz` system package installed.

### Using as a Library

```python
from agent import build_murder_mystery_game

# Build the game
game_graph, conversation_graph = build_murder_mystery_game(
    model_name="gpt-4o",
    temperature=0
)

# Run a game
output = game_graph.invoke({
    "environment": "Victorian London mansion",
    "max_characters": 5,
    "num_guesses_left": 3
})
```

## 🧩 Key Technologies

- **LangChain**: Framework for building LLM applications
- **LangGraph**: State graph orchestration for complex workflows
- **OpenAI GPT-4o**: Large language model for natural language generation
- **Pydantic**: Data validation and settings management
- **Rich**: Beautiful terminal formatting and UI
- **FAISS**: Vector similarity search for context retrieval (v2.0)
- **NumPy**: Numerical computing for vector operations (v2.0)

## 💡 Tips for Success

1. **Take Notes**: Keep track of what each character says
2. **Look for Inconsistencies**: Characters may lie or contradict each other
3. **Use Sherlock AI**: The AI assistant can ask strategic questions
4. **Consider Motives**: Think about who had reason to commit the crime
5. **Pay Attention to Details**: Small clues in the crime scene description matter
6. **Set Action Limits**: Using limits forces more strategic questioning
7. **Track Progress**: Monitor visited characters and actions remaining
8. **Watch Cache Notifications**: Cached responses appear instantly - use this for quick re-interviews

## 🐛 Troubleshooting

### API Key Issues
- Ensure your OpenAI API key is valid and has GPT-4o access
- Check that the key is properly set in environment variables

### Import Errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're using Python 3.9 or higher
- For FAISS issues: `pip install faiss-cpu --force-reinstall`

### Display Issues
- Use a terminal that supports ANSI color codes
- Try a different terminal emulator if text appears garbled

### Performance Issues
- **Slow First Run**: First game generates embeddings (normal)
- **Memory Usage**: Reduce cache size or chunk count in configuration
- **Token Limits**: Vector store automatically chunks large contexts
- Clear cache between sessions: `from agent import reset_cache; reset_cache()`

### Cache/Vector Store Issues
- If embeddings fail, the system automatically falls back to simple text chunking
- Check OpenAI API rate limits if you see embedding errors
- Cache persists across runs - use `reset_cache()` for fresh start

---

## 📚 Inspiration

This project is inspired by the paper "UNBOUNDED: A Generative Infinite Game of Character Life Simulation" (Li et al., 2024), which introduced concepts of generative infinite games using LLMs.

## 🤝 Contributing

Feel free to fork this project and customize it for your own use! Some ideas for enhancements:

- Add more complex clue systems
- Implement multiple crime types
- Create a web-based UI
- Add save/load game functionality
- Include time pressure mechanics
- Add character relationship graphs

## 📄 License

This project is open source and available for educational and personal use.

## 🙏 Acknowledgments

- LangChain and LangGraph teams for the excellent frameworks
- OpenAI for GPT-4o
- The "UNBOUNDED" paper authors for inspiration

---

**Happy Detective Work! 🔍**

*"Once you eliminate the impossible, whatever remains, no matter how improbable, must be the truth." - Sherlock Holmes*

