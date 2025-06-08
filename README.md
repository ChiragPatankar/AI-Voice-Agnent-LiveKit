# AI Voice Agent with LiveKit

A real-time AI voice agent built with LiveKit that enables natural voice conversations using Speech-to-Text, Large Language Model, and Text-to-Speech technologies.

## 🎯 Features

- **Real-time Voice Conversation**: Natural voice interactions with AI
- **Interruption Handling**: Users can interrupt the agent mid-response
- **Comprehensive Metrics Logging**: Detailed performance metrics saved to Excel
- **Low Latency**: Optimized for sub-2 second response times
- **Multi-provider Support**: Flexible configuration for different AI providers

## 🏗️ Architecture

```
User Speech → Deepgram STT → Groq LLM → Cartesia TTS → Audio Output
                                ↓
                         Metrics Logger (Excel)
```

### Pipeline Components:
- **STT**: Deepgram Nova-2 (free tier)
- **LLM**: Groq with Llama-3.1-8b-instant (free tier)
- **TTS**: Cartesia Sonic-English (free trial)
- **VAD**: Silero Voice Activity Detection

## 📊 Metrics Captured

The system logs detailed metrics for each conversation turn:

- **EOU Delay**: End of Utterance to STT output
- **TTFT**: Time to First Token from LLM
- **TTFB**: Time to First Byte from TTS
- **Total Latency**: End-to-end response time
- **Session Summary**: Overall conversation statistics

Metrics are automatically saved to Excel files in the `metrics/` directory.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- LiveKit Cloud account (free)
- API keys for Deepgram, Groq, and Cartesia

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ai-voice-agent
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download model files:
```bash
python voice_agent.py download-files
```

### Configuration

Create a `.env` file with your API keys:

```env
# LiveKit Configuration
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_server_url

# AI Provider APIs
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
CARTESIA_API_KEY=your_cartesia_api_key

# Optional: Alternative providers
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Configuration
STT_PROVIDER=deepgram
LLM_PROVIDER=groq
TTS_PROVIDER=cartesia
MAX_LATENCY_THRESHOLD=2.0
```

### Running the Agent

1. **Console Mode** (local testing):
```bash
python voice_agent.py console
```

2. **Development Mode** (LiveKit Playground):
```bash
python voice_agent.py dev
```

3. **Production Mode**:
```bash
python voice_agent.py start
```

## 🧪 Testing

1. Start the agent in dev mode
2. Open the LiveKit Agents Playground
3. Join the room and enable microphone access
4. Start speaking - the agent will respond with voice
5. Check `metrics/` directory for Excel reports after the session

## 📁 Project Structure

```
ai-voice-agent/
├── voice_agent.py          # Main agent implementation
├── metrics_logger.py       # Excel metrics logging
├── requirements.txt        # Python dependencies
├── .env                   # API keys (not committed)
├── README.md              # This file
└── metrics/               # Generated Excel reports
```

## 🔧 Customization

### Changing AI Providers

Modify the `.env` file to switch providers:
- STT: `deepgram` or `whisper`
- LLM: `groq` or `openai`
- TTS: `cartesia` or `elevenlabs`

### Adjusting Agent Personality

Edit the instructions in the `Assistant` class in `voice_agent.py`:

```python
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="Your custom personality here...")
```

### Latency Optimization

- Monitor metrics for bottlenecks
- Adjust model choices (faster models = lower latency)
- Optimize network connectivity
- Use edge deployment for production

## 📈 Performance Metrics

The system tracks:
- Average latency per session
- High latency turn detection (>2s)
- Interruption handling statistics
- Provider-specific performance data

## 🛠️ Development

### Adding New Features

1. Extend the `Assistant` class for new capabilities
2. Add function tools for specific tasks
3. Implement custom metrics in `ConversationMetrics`

### Debugging

- Check terminal logs for real-time metrics
- Review Excel reports for detailed analysis
- Use console mode for local debugging

## 📋 Requirements Met

✅ Simple agent session pipeline (STT, LLM, TTS)  
✅ Real-time voice conversation  
✅ Interruption handling  
✅ Metrics logging to Excel (EOU, TTFT, TTFB, Total Latency)  
✅ Sub-2 second latency optimization  
✅ Free tier API usage  
✅ Secure API key management  
✅ LiveKit Playground compatibility  

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙋‍♂️ Support

For issues or questions:
1. Check the LiveKit documentation
2. Review the metrics logs for performance issues
3. Test with different API providers if needed

---

**Built with ❤️ using LiveKit, Deepgram, Groq, and Cartesia** 