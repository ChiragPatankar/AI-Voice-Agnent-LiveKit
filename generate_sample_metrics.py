#!/usr/bin/env python3
"""
Sample metrics generator for demonstration purposes.
This creates sample Excel files to show the metrics reporting capability.
"""

import time
import random
from metrics_logger import MetricsLogger

def generate_sample_metrics():
    """Generate sample conversation metrics for demonstration"""
    
    print("🎯 Generating sample metrics for demonstration...")
    
    # Initialize metrics logger
    metrics_logger = MetricsLogger()
    metrics_logger.start_session()
    
    # Simulate a conversation with 5 turns
    for turn in range(1, 6):
        print(f"  📊 Generating turn {turn} metrics...")
        
        # Generate realistic latency values
        eou_delay = random.uniform(0.1, 0.4)  # STT processing time
        ttft = random.uniform(0.3, 1.2)       # LLM first token time
        ttfb = random.uniform(0.1, 0.3)       # TTS first byte time
        total_latency = eou_delay + ttft + ttfb + random.uniform(0.1, 0.3)
        
        # Create turn metrics
        turn_metrics = {
            'turn_number': turn,
            'eou_delay': eou_delay,
            'ttft': ttft,
            'ttfb': ttfb,
            'total_latency': total_latency,
            'interrupted': random.choice([False, False, False, True]),  # 25% interruption rate
            'agent_response': f"Sample response for turn {turn}",
            'user_input': f"User question {turn}",
            'timestamp': time.time()
        }
        
        metrics_logger.add_turn_metrics(turn_metrics)
        
        # Simulate some delay between turns
        time.sleep(0.5)
    
    # Generate session summary
    session_summary = {
        'total_turns': 5,
        'successful_turns': 4,
        'interrupted_turns': 1,
        'config': {
            'stt': 'deepgram',
            'llm': 'groq', 
            'tts': 'cartesia',
            'version': 'demo'
        },
        'demo_mode': True
    }
    
    # End session and generate Excel file
    metrics_logger.end_session(session_summary)
    
    print("✅ Sample metrics generated successfully!")
    print("📁 Check the 'metrics/' directory for the Excel file")
    print("🎉 This demonstrates the full metrics logging capability")

if __name__ == "__main__":
    generate_sample_metrics() 