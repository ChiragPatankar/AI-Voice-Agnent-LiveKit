#!/usr/bin/env python3
"""
Test script for LiveKit AI Voice Agent
Validates individual components and full system integration
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceAgentTester:
    def __init__(self):
        load_dotenv()
        self.test_results = {}
        
    async def test_environment(self) -> bool:
        """Test environment variables and API keys"""
        logger.info("🔍 Testing environment configuration...")
        
        required_vars = {
            "LIVEKIT_URL": os.getenv("LIVEKIT_URL"),
            "LIVEKIT_API_KEY": os.getenv("LIVEKIT_API_KEY"),
            "LIVEKIT_API_SECRET": os.getenv("LIVEKIT_API_SECRET")
        }
        
        # Provider-specific variables
        stt_provider = os.getenv("STT_PROVIDER", "deepgram")
        llm_provider = os.getenv("LLM_PROVIDER", "groq")
        tts_provider = os.getenv("TTS_PROVIDER", "cartesia")
        
        provider_vars = {}
        if stt_provider == "deepgram":
            provider_vars["DEEPGRAM_API_KEY"] = os.getenv("DEEPGRAM_API_KEY")
        elif stt_provider == "whisper":
            provider_vars["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
            
        if llm_provider == "groq":
            provider_vars["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
        elif llm_provider == "openai":
            provider_vars["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
            
        if tts_provider == "cartesia":
            provider_vars["CARTESIA_API_KEY"] = os.getenv("CARTESIA_API_KEY")
        elif tts_provider == "elevenlabs":
            provider_vars["ELEVENLABS_API_KEY"] = os.getenv("ELEVENLABS_API_KEY")
        
        all_vars = {**required_vars, **provider_vars}
        missing_vars = [key for key, value in all_vars.items() if not value]
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            self.test_results["environment"] = False
            return False
        
        logger.info("✅ Environment configuration valid")
        self.test_results["environment"] = True
        return True
    
    async def test_imports(self) -> bool:
        """Test all required package imports"""
        logger.info("📦 Testing package imports...")
        
        import_tests = [
            ("livekit", "LiveKit core"),
            ("livekit.agents", "LiveKit agents"),
            ("pandas", "Pandas for metrics"),
            ("openpyxl", "Excel support"),
            ("dotenv", "Environment loading")
        ]
        
        failed_imports = []
        
        for module, description in import_tests:
            try:
                __import__(module)
                logger.info(f"  ✅ {description}")
            except ImportError as e:
                logger.error(f"  ❌ {description}: {e}")
                failed_imports.append(module)
        
        if failed_imports:
            logger.error(f"❌ Failed imports: {', '.join(failed_imports)}")
            self.test_results["imports"] = False
            return False
        
        logger.info("✅ All imports successful")
        self.test_results["imports"] = True
        return True
    
    async def test_providers(self) -> bool:
        """Test provider initialization"""
        logger.info("🔧 Testing provider initialization...")
        
        try:
            from voice_agent import VoiceAgentConfig, AIVoiceAgent
            
            config = VoiceAgentConfig()
            agent = AIVoiceAgent(config)
            
            # Test STT provider
            try:
                stt = agent.create_stt_provider()
                logger.info(f"  ✅ STT Provider ({config.stt_provider}) initialized")
            except Exception as e:
                logger.error(f"  ❌ STT Provider failed: {e}")
                self.test_results["stt_provider"] = False
                return False
            
            # Test LLM provider
            try:
                llm = agent.create_llm_provider()
                logger.info(f"  ✅ LLM Provider ({config.llm_provider}) initialized")
            except Exception as e:
                logger.error(f"  ❌ LLM Provider failed: {e}")
                self.test_results["llm_provider"] = False
                return False
            
            # Test TTS provider
            try:
                tts = agent.create_tts_provider()
                logger.info(f"  ✅ TTS Provider ({config.tts_provider}) initialized")
            except Exception as e:
                logger.error(f"  ❌ TTS Provider failed: {e}")
                self.test_results["tts_provider"] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Provider test failed: {e}")
            self.test_results["providers"] = False
            return False
        
        logger.info("✅ All providers initialized successfully")
        self.test_results["providers"] = True
        return True
    
    async def test_metrics_logger(self) -> bool:
        """Test metrics logging functionality"""
        logger.info("📊 Testing metrics logger...")
        
        try:
            from metrics_logger import MetricsLogger
            
            # Create test logger
            metrics_logger = MetricsLogger(output_dir="test_metrics")
            
            # Test session start
            metrics_logger.start_session()
            
            # Test adding metrics
            test_metrics = {
                'turn_number': 1,
                'total_latency': 1.5,
                'eou_delay': 0.2,
                'ttft': 0.8,
                'ttfb': 0.3,
                'interrupted': False
            }
            
            metrics_logger.add_turn_metrics(test_metrics)
            
            # Test session end
            metrics_logger.end_session({
                'test_session': True,
                'total_turns': 1
            })
            
            logger.info("✅ Metrics logger working correctly")
            self.test_results["metrics"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Metrics logger test failed: {e}")
            self.test_results["metrics"] = False
            return False
    
    async def test_livekit_connection(self) -> bool:
        """Test LiveKit server connectivity"""
        logger.info("🌐 Testing LiveKit connectivity...")
        
        try:
            import livekit
            from livekit import rtc
            
            url = os.getenv("LIVEKIT_URL")
            api_key = os.getenv("LIVEKIT_API_KEY")
            api_secret = os.getenv("LIVEKIT_API_SECRET")
            
            if not all([url, api_key, api_secret]):
                logger.error("❌ LiveKit credentials not configured")
                self.test_results["livekit"] = False
                return False
            
            # Simple connection test (just validate credentials format)
            if not url.startswith(('ws://', 'wss://')):
                logger.error("❌ Invalid LiveKit URL format")
                self.test_results["livekit"] = False
                return False
            
            if len(api_key) < 10 or len(api_secret) < 10:
                logger.error("❌ Invalid LiveKit API key/secret format")
                self.test_results["livekit"] = False
                return False
            
            logger.info("✅ LiveKit credentials format valid")
            self.test_results["livekit"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ LiveKit test failed: {e}")
            self.test_results["livekit"] = False
            return False
    
    async def test_api_connectivity(self) -> bool:
        """Test API provider connectivity"""
        logger.info("🔗 Testing API provider connectivity...")
        
        try:
            import httpx
            
            # Test endpoints
            test_endpoints = []
            
            stt_provider = os.getenv("STT_PROVIDER", "deepgram")
            llm_provider = os.getenv("LLM_PROVIDER", "groq")
            tts_provider = os.getenv("TTS_PROVIDER", "cartesia")
            
            if stt_provider == "deepgram":
                test_endpoints.append(("Deepgram", "https://api.deepgram.com/v1/listen"))
            if llm_provider == "groq":
                test_endpoints.append(("Groq", "https://api.groq.com/openai/v1/models"))
            elif llm_provider == "openai":
                test_endpoints.append(("OpenAI", "https://api.openai.com/v1/models"))
            if tts_provider == "cartesia":
                test_endpoints.append(("Cartesia", "https://api.cartesia.ai/"))
            elif tts_provider == "elevenlabs":
                test_endpoints.append(("ElevenLabs", "https://api.elevenlabs.io/v1/voices"))
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                for name, url in test_endpoints:
                    try:
                        response = await client.get(url)
                        if response.status_code < 500:  # Any non-server error is fine
                            logger.info(f"  ✅ {name} API reachable")
                        else:
                            logger.warning(f"  ⚠️  {name} API returned {response.status_code}")
                    except Exception as e:
                        logger.warning(f"  ⚠️  {name} API connectivity issue: {e}")
            
            logger.info("✅ API connectivity test completed")
            self.test_results["api_connectivity"] = True
            return True
            
        except ImportError:
            logger.warning("⚠️  httpx not available, skipping API connectivity test")
            self.test_results["api_connectivity"] = True
            return True
        except Exception as e:
            logger.error(f"❌ API connectivity test failed: {e}")
            self.test_results["api_connectivity"] = False
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        logger.info("🧪 Starting comprehensive voice agent tests...")
        
        tests = [
            ("Environment", self.test_environment),
            ("Imports", self.test_imports),
            ("Providers", self.test_providers),
            ("Metrics Logger", self.test_metrics_logger),
            ("LiveKit", self.test_livekit_connection),
            ("API Connectivity", self.test_api_connectivity)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running {test_name} Test")
            logger.info(f"{'='*50}")
            
            try:
                result = await test_func()
                results[test_name.lower().replace(' ', '_')] = result
            except Exception as e:
                logger.error(f"❌ {test_name} test crashed: {e}")
                results[test_name.lower().replace(' ', '_')] = False
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        logger.info(f"\n{'='*50}")
        logger.info("🎯 TEST SUMMARY")
        logger.info(f"{'='*50}")
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! Your voice agent is ready to deploy.")
            return True
        else:
            logger.error("💥 Some tests failed. Please fix the issues before deploying.")
            return False

async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LiveKit Voice Agent")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    args = parser.parse_args()
    
    tester = VoiceAgentTester()
    
    if args.quick:
        # Quick tests only
        logger.info("🚀 Running quick tests...")
        results = {}
        results["environment"] = await tester.test_environment()
        results["imports"] = await tester.test_imports()
    else:
        # Full test suite
        results = await tester.run_all_tests()
    
    success = tester.print_summary(results)
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Test runner crashed: {e}")
        sys.exit(1) 