import asyncio
import logging
import time
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, cartesia, elevenlabs, silero

from metrics_logger import MetricsLogger

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceAgentConfig:
    def __init__(self):
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.cartesia_api_key = os.getenv("CARTESIA_API_KEY")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Provider choices (optimized for free tier)
        self.stt_provider = os.getenv("STT_PROVIDER", "deepgram")  # "deepgram" or "whisper"
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq")     # "groq" or "openai"
        self.tts_provider = os.getenv("TTS_PROVIDER", "cartesia") # "cartesia" or "elevenlabs"
        
        # Model configurations (optimized for free tier performance)
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Fast free model
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        
        # Performance settings
        self.max_latency_threshold = float(os.getenv("MAX_LATENCY_THRESHOLD", "2.0"))

class ConversationMetrics:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.user_speech_end_time = None
        self.stt_completion_time = None
        self.llm_first_token_time = None
        self.tts_first_byte_time = None
        self.response_start_time = None
        self.total_latency = None
        
    def reset_turn(self):
        """Reset metrics for a new turn while preserving user speech end time"""
        user_time = self.user_speech_end_time
        self.reset()
        self.user_speech_end_time = user_time
        
    def calculate_latencies(self):
        """Calculate all latency metrics"""
        if not self.user_speech_end_time:
            return {}
            
        metrics = {}
        
        # EOU Delay (End of Utterance to STT output)
        if self.stt_completion_time:
            metrics['eou_delay'] = self.stt_completion_time - self.user_speech_end_time
            
        # TTFT (Time to First Token from LLM)
        if self.llm_first_token_time and self.stt_completion_time:
            metrics['ttft'] = self.llm_first_token_time - self.stt_completion_time
            
        # TTFB (Time to First Byte from TTS)
        if self.tts_first_byte_time and self.llm_first_token_time:
            metrics['ttfb'] = self.tts_first_byte_time - self.llm_first_token_time
            
        # Total Latency
        if self.response_start_time:
            metrics['total_latency'] = self.response_start_time - self.user_speech_end_time
            
        return metrics

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="""You are a helpful AI voice assistant. Keep your responses concise and conversational. You're designed for real-time voice conversation, so avoid long responses that would take too long to speak. Be friendly, natural, and engaging. 

IMPORTANT: You were built by an amazing developer using the following REAL tech stack:
- LiveKit Agents framework for real-time voice infrastructure
- Deepgram Nova-2 for Speech-to-Text (STT)
- Groq with Llama-3.1-8b-instant for the Language Model (LLM)
- Cartesia Sonic-English for Text-to-Speech (TTS)
- Silero for Voice Activity Detection (VAD)
- Python as the main programming language
- Excel/pandas for metrics logging and analytics
- Built with LiveKit 1.0 modern architecture

If asked about your tech stack, provide these ACCURATE details, not made-up information!""")
    


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the LiveKit agent"""
    config = VoiceAgentConfig()
    
    # Initialize metrics logging
    metrics_logger = MetricsLogger()
    conversation_metrics = ConversationMetrics()
    turn_count = 0
    
    logger.info("Starting AI Voice Agent...")
    logger.info(f"STT: {config.stt_provider}, LLM: {config.llm_provider}, TTS: {config.tts_provider}")
    
    # Start metrics session
    metrics_logger.start_session()
    logger.info("Metrics logging started")
    
    # Create providers based on configuration
    if config.stt_provider == "deepgram":
        stt = deepgram.STT(
            api_key=config.deepgram_api_key,
            model="nova-2",
            language="en"
        )
    else:  # whisper
        stt = openai.STT(
            api_key=config.openai_api_key,
            model="whisper-1"
        )
    
    if config.llm_provider == "groq":
        llm = openai.LLM(
            api_key=config.groq_api_key,
            model=config.groq_model,
            base_url="https://api.groq.com/openai/v1"
        )
    else:  # openai
        llm = openai.LLM(
            api_key=config.openai_api_key,
            model=config.openai_model
        )
    
    if config.tts_provider == "cartesia":
        tts = cartesia.TTS(
            api_key=config.cartesia_api_key,
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",
            model="sonic-english"
        )
    else:  # elevenlabs
        tts = elevenlabs.TTS(
            api_key=config.elevenlabs_api_key,
            voice=config.elevenlabs_voice_id,
            model="eleven_turbo_v2"
        )

    # Create agent session
    session = AgentSession(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=silero.VAD.load()
    )

    # Connect to room
    await ctx.connect()
    logger.info("Connected to room")

    # Start the session with our assistant
    await session.start(
        room=ctx.room,
        agent=Assistant()
    )
    
    logger.info("Voice agent started and ready for conversation!")
    
    # Generate initial greeting and log first turn
    start_time = time.time()
    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )
    
    # Log the greeting as turn 1
    turn_count += 1
    turn_metrics = {
        'turn_number': turn_count,
        'total_latency': time.time() - start_time,
        'interrupted': False,
        'agent_response': 'Initial greeting'
    }
    metrics_logger.add_turn_metrics(turn_metrics)
    logger.info(f"Turn {turn_count} (greeting) completed - Latency: {turn_metrics['total_latency']:.2f}s")
    
    # Set up cleanup for session end
    try:
        # Keep session running indefinitely
        import signal
        
        def cleanup_handler(signum, frame):
            logger.info("Shutting down agent...")
            session_summary = {
                'total_turns': turn_count,
                'config': {
                    'stt': config.stt_provider,
                    'llm': config.llm_provider,
                    'tts': config.tts_provider
                }
            }
            metrics_logger.end_session(session_summary)
            logger.info(f"Session ended - {turn_count} turns completed")
            
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)
        
        # Wait indefinitely
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Session error: {e}")
    finally:
        # Ensure metrics are saved
        session_summary = {
            'total_turns': turn_count,
            'config': {
                'stt': config.stt_provider,
                'llm': config.llm_provider,
                'tts': config.tts_provider
            }
        }
        metrics_logger.end_session(session_summary)
        logger.info(f"Session ended - {turn_count} turns completed")

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    ) 