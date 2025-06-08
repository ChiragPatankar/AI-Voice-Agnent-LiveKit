#!/usr/bin/env python3
"""
Deployment script for LiveKit AI Voice Agent
Handles environment setup, validation, and agent deployment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceAgentDeployment:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        
    def check_env_file(self) -> bool:
        """Check if .env file exists and has required keys"""
        if not self.env_file.exists():
            logger.error("❌ .env file not found!")
            self.create_env_template()
            return False
        
        load_dotenv(self.env_file)
        
        required_keys = [
            "LIVEKIT_URL",
            "LIVEKIT_API_KEY", 
            "LIVEKIT_API_SECRET"
        ]
        
        # Optional keys based on provider choice
        provider_keys = {
            "deepgram": ["DEEPGRAM_API_KEY"],
            "groq": ["GROQ_API_KEY"],
            "cartesia": ["CARTESIA_API_KEY"],
            "elevenlabs": ["ELEVENLABS_API_KEY"],
            "openai": ["OPENAI_API_KEY"]
        }
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        # Check provider-specific keys
        stt_provider = os.getenv("STT_PROVIDER", "deepgram")
        llm_provider = os.getenv("LLM_PROVIDER", "groq") 
        tts_provider = os.getenv("TTS_PROVIDER", "cartesia")
        
        for provider in [stt_provider, llm_provider, tts_provider]:
            if provider in provider_keys:
                for key in provider_keys[provider]:
                    if not os.getenv(key):
                        missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
            return False
            
        logger.info("✅ Environment variables validated")
        return True
    
    def create_env_template(self):
        """Create a template .env file"""
        template = """# 🆓 FREE TIER CONFIGURATION - LiveKit AI Voice Agent
# This setup uses only FREE API services - no credit card required!

# ═══════════════════════════════════════════════════════════════
# 🔐 LIVEKIT CONFIGURATION (Required) - FREE TIER AVAILABLE
# ═══════════════════════════════════════════════════════════════
# Get free LiveKit keys at: https://console.livekit.io
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-free-livekit-api-key  
LIVEKIT_API_SECRET=your-free-livekit-api-secret

# ═══════════════════════════════════════════════════════════════
# 🎛️ PROVIDER CONFIGURATION (Optimized for Free Tier)
# ═══════════════════════════════════════════════════════════════
STT_PROVIDER=deepgram   # FREE: 12,000 minutes/month
LLM_PROVIDER=groq       # FREE: Very fast inference, generous limits  
TTS_PROVIDER=cartesia   # FREE: Good quality voice synthesis

# ═══════════════════════════════════════════════════════════════
# 🔑 FREE API KEYS (No Credit Card Required)
# ═══════════════════════════════════════════════════════════════

# Deepgram STT (FREE: 12,000 minutes/month)
# Sign up: https://console.deepgram.com
DEEPGRAM_API_KEY=your-deepgram-free-key

# Groq LLM (FREE: Fast inference, generous limits)
# Sign up: https://console.groq.com  
GROQ_API_KEY=your-groq-free-key

# Cartesia TTS (FREE: Quality voice synthesis)
# Sign up: https://cartesia.ai
CARTESIA_API_KEY=your-cartesia-free-key

# ═══════════════════════════════════════════════════════════════
# ⚡ PERFORMANCE SETTINGS (Optimized for Free Tier)
# ═══════════════════════════════════════════════════════════════
GROQ_MODEL=llama-3.1-8b-instant     # Fast free model for <2s latency
MAX_LATENCY_THRESHOLD=2.0            # Alert if response > 2 seconds

# ═══════════════════════════════════════════════════════════════
# 📊 OPTIONAL: Alternative Providers (If you have paid accounts)
# ═══════════════════════════════════════════════════════════════
# Uncomment and use these if you have paid API access:

# OPENAI_API_KEY=your-openai-key      # For STT (Whisper) or LLM (GPT-4)
# ELEVENLABS_API_KEY=your-elevenlabs-key  # For premium TTS voices
# ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# ═══════════════════════════════════════════════════════════════
# 🎯 GETTING STARTED:
# ═══════════════════════════════════════════════════════════════
# 1. Fill in the API keys above (all free!)
# 2. Run: python test_agent.py
# 3. Deploy: python deployment.py
# ═══════════════════════════════════════════════════════════════
"""
        
        with open(self.env_file, 'w') as f:
            f.write(template)
            
        logger.info(f"📄 Created .env template at {self.env_file}")
        logger.info("🔧 Please fill in your API keys and configuration before running again")
    
    def install_dependencies(self):
        """Install required Python packages"""
        logger.info("📦 Installing dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            logger.info("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False
    
    def validate_imports(self):
        """Validate that all required packages can be imported"""
        logger.info("🔍 Validating imports...")
        
        required_imports = [
            "livekit",
            "livekit.agents",
            "openai",
            "deepgram",
            "pandas",
            "openpyxl"
        ]
        
        failed_imports = []
        
        for module in required_imports:
            try:
                __import__(module)
            except ImportError as e:
                failed_imports.append(f"{module}: {e}")
        
        if failed_imports:
            logger.error("❌ Import validation failed:")
            for failure in failed_imports:
                logger.error(f"  - {failure}")
            return False
        
        logger.info("✅ All imports validated")
        return True
    
    def run_agent(self, dev_mode=True):
        """Run the voice agent"""
        logger.info("🚀 Starting Voice Agent...")
        
        cmd = [sys.executable, "voice_agent.py"]
        
        if dev_mode:
            cmd.extend(["--dev"])
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Agent failed to start: {e}")
            return False
        except KeyboardInterrupt:
            logger.info("🛑 Agent stopped by user")
            return True
    
    def deploy(self, skip_install=False, dev_mode=True):
        """Full deployment process"""
        logger.info("🎯 Starting LiveKit Voice Agent Deployment")
        
        # Check environment
        if not self.check_env_file():
            return False
        
        # Install dependencies
        if not skip_install:
            if not self.install_dependencies():
                return False
        
        # Validate imports
        if not self.validate_imports():
            return False
        
        # Run agent
        return self.run_agent(dev_mode=dev_mode)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy LiveKit Voice Agent")
    parser.add_argument("--skip-install", action="store_true", 
                       help="Skip dependency installation")
    parser.add_argument("--production", action="store_true",
                       help="Run in production mode")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate environment and dependencies")
    
    args = parser.parse_args()
    
    deployment = VoiceAgentDeployment()
    
    if args.validate_only:
        success = (deployment.check_env_file() and 
                  deployment.validate_imports())
        if success:
            logger.info("✅ Validation completed successfully")
        else:
            logger.error("❌ Validation failed")
        return success
    
    success = deployment.deploy(
        skip_install=args.skip_install,
        dev_mode=not args.production
    )
    
    if success:
        logger.info("🎉 Deployment completed successfully!")
    else:
        logger.error("💥 Deployment failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 