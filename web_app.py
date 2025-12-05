"""
Murder Mystery Game - Streamlit Web Application

A beautiful web interface for the Murder Mystery investigation game.
Run with: streamlit run web_app.py
"""

import streamlit as st
import os
from typing import Optional, Dict, Any
import time

from agent.graph_builder import build_murder_mystery_game
from agent.schemas import Character, GenerateGameState
from agent.web_utils import (
    initialize_game,
    start_conversation_with_character,
    ask_character_question,
    check_guess,
    get_investigation_progress,
    mark_character_visited,
    is_action_limit_reached,
    decrement_guesses,
    get_suspects_list
)


# Page configuration
st.set_page_config(
    page_title="Murder Mystery Investigation",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Sherlock Holmes themed styling
st.markdown("""
<style>
    /* Import Victorian-style font */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap');
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Main header with Victorian styling */
    .main-header {
        font-family: 'Cinzel', serif;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #d4af37, #f4e7c3, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        letter-spacing: 2px;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));
    }
    
    /* Character cards with mystery vibe */
    .character-card {
        background: linear-gradient(135deg, #2d3561 0%, #1f2544 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #d4af37;
        border-right: 1px solid rgba(212, 175, 55, 0.3);
        margin-bottom: 1rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        color: #e8dcc4;
        font-family: 'Cormorant Garamond', serif;
    }
    
    .character-card h3 {
        color: #d4af37;
        font-family: 'Cinzel', serif;
        font-size: 1.4rem;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }
    
    .character-card p {
        color: #c9b896;
        line-height: 1.6;
    }
    
    /* Visited character - green detective stamp */
    .visited-character {
        border-left: 5px solid #4a9d5f;
        background: linear-gradient(135deg, #2d4a36 0%, #1f3329 100%);
        opacity: 0.95;
    }
    
    /* Victim card - blood red accent */
    .victim-card {
        border-left: 5px solid #8b0000;
        background: linear-gradient(135deg, #4a2633 0%, #331a24 100%);
        box-shadow: 0 8px 16px rgba(139, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    /* Dr. Watson's narration box - aged paper look */
    .narration-box {
        background: linear-gradient(135deg, #2c2416 0%, #3d3021 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 3px solid #d4af37;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(212, 175, 55, 0.1);
        margin: 1rem 0;
        color: #e8dcc4;
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.1rem;
        line-height: 1.8;
        position: relative;
    }
    
    .narration-box h3 {
        color: #d4af37;
        font-family: 'Cinzel', serif;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }
    
    .narration-box::before {
        content: "📜";
        position: absolute;
        top: -15px;
        left: 20px;
        font-size: 2rem;
        filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.5));
    }
    
    /* Progress box - detective notebook style */
    .progress-box {
        background: linear-gradient(135deg, #3d2a1f 0%, #2c1e14 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #d4af37;
        border-right: 1px solid rgba(212, 175, 55, 0.2);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        color: #e8dcc4;
        font-family: 'Cormorant Garamond', serif;
    }
    
    .progress-box h3 {
        color: #d4af37;
        font-family: 'Cinzel', serif;
    }
    
    /* Success box - case solved! */
    .success-box {
        background: linear-gradient(135deg, #2a4a2e 0%, #1d3321 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 3px solid #4a9d5f;
        box-shadow: 0 10px 25px rgba(74, 157, 95, 0.3), inset 0 0 20px rgba(74, 157, 95, 0.1);
        color: #d4f4dd;
        text-align: center;
    }
    
    .success-box h2 {
        color: #6fd97f;
        font-family: 'Cinzel', serif;
        text-shadow: 0 0 15px rgba(111, 217, 127, 0.5);
    }
    
    /* Failure box - case unsolved */
    .failure-box {
        background: linear-gradient(135deg, #4a2633 0%, #331a24 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 3px solid #8b0000;
        box-shadow: 0 10px 25px rgba(139, 0, 0, 0.4), inset 0 0 20px rgba(139, 0, 0, 0.1);
        color: #f4d4d4;
        text-align: center;
    }
    
    .failure-box h2 {
        color: #ff6b6b;
        font-family: 'Cinzel', serif;
        text-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
    }
    
    /* Buttons with Victorian style */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #d4af37 0%, #b8941f 100%);
        color: #1a1a2e;
        font-family: 'Cinzel', serif;
        font-weight: 600;
        border: 2px solid #f4e7c3;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #f4e7c3 0%, #d4af37 100%);
        box-shadow: 0 6px 12px rgba(212, 175, 55, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 2px solid #d4af37;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #d4af37;
        font-family: 'Cinzel', serif;
    }
    
    [data-testid="stSidebar"] label {
        color: #c9b896;
        font-family: 'Cormorant Garamond', serif;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        color: #d4af37;
        font-family: 'Cinzel', serif;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: #c9b896;
        font-family: 'Cormorant Garamond', serif;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(45, 53, 97, 0.6);
        border-radius: 10px;
        border-left: 3px solid #d4af37;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Cormorant Garamond', serif;
        color: #e8dcc4;
    }
    
    /* Text inputs */
    .stTextInput>div>div>input {
        background-color: #2d3561;
        color: #e8dcc4;
        border: 2px solid #d4af37;
        border-radius: 8px;
        font-family: 'Cormorant Garamond', serif;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #f4e7c3;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }
    
    /* Selectbox */
    .stSelectbox>div>div>div {
        background-color: #2d3561;
        color: #e8dcc4;
        border: 2px solid #d4af37;
        font-family: 'Cormorant Garamond', serif;
    }
    
    /* Headers throughout the app */
    h1, h2, h3 {
        color: #d4af37;
        font-family: 'Cinzel', serif;
    }
    
    /* Regular text */
    p, div, span {
        color: #c9b896;
    }
    
    /* Decorative element */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #d4af37, transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'game_initialized' not in st.session_state:
        st.session_state.game_initialized = False
    if 'game_graph' not in st.session_state:
        st.session_state.game_graph = None
    if 'conversation_graph' not in st.session_state:
        st.session_state.conversation_graph = None
    if 'game_state' not in st.session_state:
        st.session_state.game_state = None
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = 'setup'  # setup, investigation, conversation, guessing, end
    if 'selected_character' not in st.session_state:
        st.session_state.selected_character = None
    if 'conversation_messages' not in st.session_state:
        st.session_state.conversation_messages = []
    if 'investigation_log' not in st.session_state:
        st.session_state.investigation_log = []


def setup_page():
    """Display the game setup page."""
    st.markdown('<h1 class="main-header">🕵️‍♂️ MURDER MYSTERY INVESTIGATION 🔍</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="narration-box">
    <h3>🎩 Welcome, Mr. Holmes!</h3>
    <p style="font-style: italic; font-size: 1.15rem;">
    "Come, Watson! The game is afoot!"
    </p>
    <p>A most curious case has landed upon our doorstep at 221B Baker Street. 
    Scotland Yard is utterly baffled, and you, the world's foremost consulting detective, 
    must employ your powers of deduction to unravel this mystery.</p>
    <p><strong>Your Methods of Investigation:</strong></p>
    <ul style="list-style-type: none; padding-left: 1rem;">
        <li>🔍 <strong>Interview</strong> the suspects with penetrating questions</li>
        <li>🧩 <strong>Gather</strong> clues from their testimonies</li>
        <li>🎯 <strong>Deduce</strong> the identity of the perpetrator</li>
    </ul>
    <p style="font-style: italic; margin-top: 1rem; border-top: 1px solid rgba(212, 175, 55, 0.3); padding-top: 1rem;">
    "When you have eliminated the impossible, whatever remains, however improbable, must be the truth."
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    with st.sidebar:
        st.markdown("### 🎩 Case Configuration")
        st.markdown("*Prepare your investigation, Mr. Holmes*")
        st.markdown("---")
        
        # API Key input if not set
        if not api_key:
            st.warning("⚠️ OpenAI API Key Required")
            api_key_input = st.text_input("Enter your OpenAI API Key", type="password")
            if api_key_input:
                os.environ["OPENAI_API_KEY"] = api_key_input
                api_key = api_key_input
        else:
            st.success("✅ API Key configured")
        
        st.markdown("---")
        
        # Game settings
        environment = st.text_input(
            "🌍 Environment",
            value="Mistral office in Paris",
            help="Describe where the murder took place"
        )
        
        max_characters = st.slider(
            "👥 Number of Characters",
            min_value=3,
            max_value=15,
            value=5,
            help="More characters = more complex mystery"
        )
        
        num_guesses = st.slider(
            "🎲 Number of Guesses",
            min_value=1,
            max_value=10,
            value=3,
            help="How many attempts to identify the killer"
        )
        
        use_action_limit = st.checkbox("⏱️ Use Action Limit", value=True)
        max_actions = None
        if use_action_limit:
            max_actions = st.slider(
                "Maximum Actions",
                min_value=5,
                max_value=50,
                value=20,
                help="Total questions you can ask"
            )
        
        st.markdown("---")
        
        if st.button("🔍 BEGIN INVESTIGATION", type="primary", disabled=not api_key):
            if not api_key:
                st.error("Please provide an OpenAI API key!")
            else:
                with st.spinner("🔄 Generating your murder mystery..."):
                    try:
                        # Build the game graphs
                        game_graph, conversation_graph = build_murder_mystery_game()
                        
                        # Prepare initial state
                        game_state = {
                            "environment": environment,
                            "max_characters": max_characters,
                            "num_guesses_left": num_guesses,
                        }
                        if max_actions:
                            game_state["max_actions"] = max_actions
                        
                        # Initialize the game (create characters, story, narration)
                        game_state = initialize_game(game_graph, game_state)
                        
                        # Store in session
                        st.session_state.game_graph = game_graph
                        st.session_state.conversation_graph = conversation_graph
                        st.session_state.game_state = game_state
                        st.session_state.game_initialized = True
                        st.session_state.current_phase = 'investigation'
                        
                        st.success("✅ Mystery generated successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error initializing game: {e}")


def display_progress_stats():
    """Display investigation progress statistics."""
    state = st.session_state.game_state
    if not state:
        return
    
    progress = get_investigation_progress(state)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Guesses Left",
            progress['guesses_left']
        )
    
    with col2:
        st.metric(
            "👥 Interviewed",
            f"{progress['interviewed']}/{progress['total_characters']}"
        )
    
    with col3:
        if progress['max_actions']:
            st.metric(
                "⏱️ Actions",
                f"{progress['actions_taken']}/{progress['max_actions']}"
            )
        else:
            st.metric(
                "⏱️ Actions",
                progress['actions_taken']
            )
    
    with col4:
        clues = len(st.session_state.investigation_log)
        st.metric(
            "🔍 Clues Found",
            clues
        )
    
    # Show action limit warning if close
    if progress['actions_remaining'] is not None and progress['actions_remaining'] <= 3:
        st.warning(f"⚠️ Only {progress['actions_remaining']} actions remaining!")


def display_character_card(character: Character, index: int, is_visited: bool = False):
    """Display a character card."""
    is_victim = character.role == 'Victim'
    
    card_class = "character-card"
    if is_visited:
        card_class += " visited-character"
    if is_victim:
        card_class += " victim-card"
    
    status_icon = ""
    if is_victim:
        status_icon = "💀 VICTIM"
    elif is_visited:
        status_icon = "✅ Interviewed"
    else:
        status_icon = "❓ Not Interviewed"
    
    st.markdown(f"""
    <div class="{card_class}">
        <h3>{character.name}</h3>
        <p><strong>{status_icon}</strong></p>
        <p><em>{character.backstory}</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    if not is_victim and not is_visited:
        # Check action limit
        state = st.session_state.game_state
        if is_action_limit_reached(state):
            st.warning("⏱️ Action limit reached! Make your accusation.")
        else:
            if st.button(f"🗣️ Interview {character.name}", key=f"interview_{index}"):
                st.session_state.selected_character = index
                st.session_state.current_phase = 'conversation'
                st.session_state.conversation_messages = []
                st.session_state.conversation_started = False
                st.rerun()


def investigation_page():
    """Display the main investigation page."""
    st.markdown('<h1 class="main-header">🔍 Investigation Board</h1>', unsafe_allow_html=True)
    
    # Display progress
    display_progress_stats()
    
    st.markdown("---")
    
    # Display narration if not already shown
    if 'narration_shown' not in st.session_state:
        state = st.session_state.game_state
        if state and 'messages' in state and len(state['messages']) > 0:
            narration = state['messages'][0]
            st.markdown(f"""
            <div class="narration-box">
                <h3>📜 Dr. Watson's Account of the Crime</h3>
                <p style="font-style: italic; color: #d4af37;">"Holmes, you must read this at once!"</p>
                <p style="margin-top: 1rem; line-height: 1.8;">{narration.content}</p>
                <p style="font-style: italic; margin-top: 1rem; border-top: 1px solid rgba(212, 175, 55, 0.3); padding-top: 1rem;">
                ~ Faithfully recorded by Dr. John H. Watson, M.D.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.narration_shown = True
    
    # Action buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 👥 The Suspects")
        st.markdown("*Interview those who may hold the key to this mystery*")
    with col2:
        if st.button("⚖️ FINAL ACCUSATION", type="primary"):
            st.session_state.current_phase = 'guessing'
            st.rerun()
    
    # Display characters
    state = st.session_state.game_state
    if state and 'characters' in state:
        visited = state.get('visited_characters', set())
        
        # Create columns for character cards
        cols = st.columns(2)
        for idx, character in enumerate(state['characters']):
            with cols[idx % 2]:
                display_character_card(character, idx, idx in visited)


def conversation_page():
    """Display the conversation interface."""
    state = st.session_state.game_state
    char_idx = st.session_state.selected_character
    
    if char_idx is None or not state or 'characters' not in state:
        st.session_state.current_phase = 'investigation'
        st.rerun()
        return
    
    character = state['characters'][char_idx]
    story_details = state.get('story_details')
    
    st.markdown(f'<h1 class="main-header">💬 Interview with {character.name}</h1>', unsafe_allow_html=True)
    
    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            # Mark character as visited
            turns_taken = len([m for m in st.session_state.conversation_messages if m['role'] == 'user'])
            st.session_state.game_state = mark_character_visited(state, char_idx, max(1, turns_taken))
            st.session_state.current_phase = 'investigation'
            st.session_state.selected_character = None
            st.rerun()
    
    with col2:
        st.write("")  # Spacer
    
    st.markdown("---")
    
    # Character info
    st.markdown(f"""
    <div class="character-card">
        <h3>{character.name}</h3>
        <p><em>{character.backstory}</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Start conversation if not started
    if 'conversation_started' not in st.session_state or not st.session_state.conversation_started:
        with st.spinner("Character is speaking..."):
            intro_text, messages = start_conversation_with_character(
                st.session_state.conversation_graph,
                character,
                story_details
            )
            st.session_state.conversation_messages.append({
                'role': 'character',
                'content': intro_text
            })
            st.session_state.llm_messages = messages
            st.session_state.conversation_started = True
            st.rerun()
    
    # Conversation history
    st.subheader("🗣️ Conversation")
    
    # Display messages
    for msg in st.session_state.conversation_messages:
        if msg['role'] == 'character':
            st.chat_message("assistant", avatar="👤").write(f"**{character.name}**: {msg['content']}")
        else:
            st.chat_message("user", avatar="🕵️").write(msg['content'])
    
    # Question input
    st.markdown("---")
    
    # Input form
    with st.form(key="question_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input(
                "❓ Your Question",
                placeholder=f"Ask {character.name} a question...",
                label_visibility="collapsed"
            )
        with col2:
            use_sherlock_ai = st.checkbox("🤖 AI", value=False, help="Use Sherlock AI to generate question")
        
        col_a, col_b, col_c = st.columns([1, 1, 4])
        with col_a:
            submit = st.form_submit_button("📤 Ask", type="primary", use_container_width=True)
        with col_b:
            end_conv = st.form_submit_button("✅ Done", use_container_width=True)
        
        if end_conv:
            # Mark character as visited and return
            turns_taken = len([m for m in st.session_state.conversation_messages if m['role'] == 'user'])
            st.session_state.game_state = mark_character_visited(state, char_idx, max(1, turns_taken))
            st.session_state.current_phase = 'investigation'
            st.session_state.selected_character = None
            st.rerun()
        
        if submit and (question or use_sherlock_ai):
            with st.spinner("Getting response..."):
                try:
                    # Get response from character
                    llm_messages = st.session_state.get('llm_messages', [])
                    response_text, updated_messages = ask_character_question(
                        character,
                        story_details,
                        llm_messages,
                        question,
                        use_sherlock_ai
                    )
                    
                    # Update conversation
                    display_question = question if not use_sherlock_ai else updated_messages[-2].content
                    st.session_state.conversation_messages.append({
                        'role': 'user',
                        'content': display_question
                    })
                    st.session_state.conversation_messages.append({
                        'role': 'character',
                        'content': response_text
                    })
                    st.session_state.llm_messages = updated_messages
                    
                    # Add to investigation log
                    st.session_state.investigation_log.append({
                        'character': character.name,
                        'question': display_question,
                        'response': response_text,
                        'timestamp': time.time()
                    })
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error getting response: {e}")


def guessing_page():
    """Display the killer guessing interface."""
    st.markdown('<h1 class="main-header">🎯 Final Accusation</h1>', unsafe_allow_html=True)
    
    state = st.session_state.game_state
    if not state or 'characters' not in state:
        st.session_state.current_phase = 'investigation'
        st.rerun()
        return
    
    st.markdown("""
    <div class="progress-box">
        <h3>⚖️ The Final Deduction</h3>
        <p style="font-style: italic;">"Now, Watson, we have picked up our thread, and all we have to do is to follow it."</p>
        <p>Review all evidence with the utmost care. Your accusation must be certain, for justice depends upon it.</p>
        <p><strong>Who among them is the murderer?</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display progress
    display_progress_stats()
    
    st.markdown("---")
    
    # Back button
    if st.button("⬅️ Continue Investigation"):
        st.session_state.current_phase = 'investigation'
        st.rerun()
    
    st.subheader("🔍 Select the Killer")
    
    # Get non-victim characters
    suspects = [c for c in state['characters'] if c.role != 'Victim']
    suspect_names = [c.name for c in suspects]
    
    selected_suspect = st.selectbox(
        "Who committed the murder?",
        options=suspect_names,
        key="suspect_selection"
    )
    
    if st.button("🎯 Make Accusation", type="primary"):
        # Check the guess
        is_correct, killer_name = check_guess(state['characters'], selected_suspect)
        
        # Decrement guesses
        st.session_state.game_state = decrement_guesses(st.session_state.game_state)
        
        if is_correct:
            st.session_state.game_result = {
                'correct': True,
                'killer': killer_name,
                'guess': selected_suspect
            }
            st.session_state.current_phase = 'end'
            st.rerun()
        else:
            # Check if out of guesses
            if st.session_state.game_state['num_guesses_left'] == 0:
                st.session_state.game_result = {
                    'correct': False,
                    'killer': killer_name,
                    'guess': selected_suspect
                }
                st.session_state.current_phase = 'end'
                st.rerun()
            else:
                st.error(f"❌ Incorrect! {selected_suspect} was innocent. You have {st.session_state.game_state['num_guesses_left']} guesses left.")
                time.sleep(2)
                st.rerun()


def end_page():
    """Display the game end page."""
    result = st.session_state.get('game_result', {})
    is_win = result.get('correct', False)
    
    st.markdown('<h1 class="main-header">🎬 Case Closed</h1>', unsafe_allow_html=True)
    
    if is_win:
        st.markdown("""
        <div class="success-box">
            <h2>🎩 Elementary, My Dear Watson!</h2>
            <p style="font-size: 1.3rem; font-style: italic;">
            "You have done it! The case is solved!"
            </p>
            <p style="margin-top: 1rem;">Your powers of deduction have proven superior. Through careful observation
            and logical reasoning, you have identified the perpetrator and brought them to justice.</p>
            <p style="font-weight: bold; margin-top: 1rem;">
            Scotland Yard is most impressed with your methods, Mr. Holmes!
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"""
        <div class="failure-box">
            <h2>⚠️ The Case Grows Cold</h2>
            <p style="font-size: 1.2rem; font-style: italic;">
            "I fear we have been outwitted, Watson..."
            </p>
            <p style="margin-top: 1rem;">The true murderer was <strong>{result.get('killer', 'Unknown')}</strong>, 
            yet you accused <strong>{result.get('guess', 'Unknown')}</strong>.</p>
            <p style="margin-top: 1rem;">Even the great Sherlock Holmes cannot solve every case on the first attempt. 
            Study the evidence anew, and perhaps you shall perceive what you previously overlooked.</p>
            <p style="font-style: italic; margin-top: 1rem;">
            "The world is full of obvious things which nobody by any chance ever observes."
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display statistics
    st.subheader("📊 Investigation Summary")
    state = st.session_state.game_state
    if state:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Actions", state.get('total_actions', 0))
        with col2:
            st.metric("Characters Interviewed", len(state.get('visited_characters', set())))
        with col3:
            st.metric("Clues Collected", len(st.session_state.investigation_log))
    
    st.markdown("---")
    
    if st.button("🎩 INVESTIGATE ANOTHER CASE", type="primary"):
        # Reset game state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Route to appropriate page based on current phase
    if not st.session_state.game_initialized:
        setup_page()
    elif st.session_state.current_phase == 'setup':
        setup_page()
    elif st.session_state.current_phase == 'investigation':
        investigation_page()
    elif st.session_state.current_phase == 'conversation':
        conversation_page()
    elif st.session_state.current_phase == 'guessing':
        guessing_page()
    elif st.session_state.current_phase == 'end':
        end_page()


if __name__ == "__main__":
    main()

