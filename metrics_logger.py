import pandas as pd
import openpyxl
from datetime import datetime
import os
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MetricsLogger:
    def __init__(self, output_dir: str = "metrics"):
        self.output_dir = output_dir
        self.session_data = {}
        self.turn_metrics = []
        self.session_start_time = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def start_session(self):
        """Initialize a new session"""
        self.session_start_time = datetime.now()
        self.session_data = {
            'session_id': self.session_start_time.strftime("%Y%m%d_%H%M%S"),
            'start_time': self.session_start_time,
            'end_time': None,
            'duration': None,
            'total_turns': 0,
            'successful_turns': 0,
            'interrupted_turns': 0,
            'avg_latency': 0,
            'avg_eou_delay': 0,
            'avg_ttft': 0,
            'avg_ttfb': 0,
            'max_latency': 0,
            'min_latency': float('inf'),
            'high_latency_turns': 0,
            'config': {}
        }
        self.turn_metrics = []
        logger.info(f"Started new session: {self.session_data['session_id']}")
    
    def add_turn_metrics(self, metrics: Dict[str, Any]):
        """Add metrics for a single conversation turn"""
        if not self.session_start_time:
            logger.warning("Session not started. Call start_session() first.")
            return
        
        # Add timestamp
        metrics['timestamp'] = datetime.now()
        metrics['session_id'] = self.session_data['session_id']
        
        # Add to turn metrics list
        self.turn_metrics.append(metrics)
        
        # Update session totals
        self.session_data['total_turns'] += 1
        
        if metrics.get('interrupted', False):
            self.session_data['interrupted_turns'] += 1
        else:
            self.session_data['successful_turns'] += 1
        
        # Update latency statistics
        total_latency = metrics.get('total_latency', 0)
        if total_latency > 0:
            if total_latency > self.session_data['max_latency']:
                self.session_data['max_latency'] = total_latency
            
            if total_latency < self.session_data['min_latency']:
                self.session_data['min_latency'] = total_latency
            
            if total_latency > 2.0:  # High latency threshold
                self.session_data['high_latency_turns'] += 1
        
        logger.info(f"Added turn metrics: Turn {metrics.get('turn_number', 'Unknown')}")
    
    def end_session(self, session_summary: Dict[str, Any] = None):
        """End the session and save metrics to Excel"""
        if not self.session_start_time:
            logger.warning("No active session to end.")
            return
        
        self.session_data['end_time'] = datetime.now()
        self.session_data['duration'] = (self.session_data['end_time'] - self.session_data['start_time']).total_seconds()
        
        if session_summary:
            self.session_data.update(session_summary)
        
        # Calculate average metrics
        if self.turn_metrics:
            self._calculate_averages()
        
        # Fix min_latency if no valid turns
        if self.session_data['min_latency'] == float('inf'):
            self.session_data['min_latency'] = 0
        
        # Save to Excel
        self._save_to_excel()
        
        logger.info(f"Session ended: {self.session_data['session_id']}")
        logger.info(f"Duration: {self.session_data['duration']:.2f}s, Turns: {self.session_data['total_turns']}")
    
    def _calculate_averages(self):
        """Calculate average metrics from all turns"""
        valid_turns = [t for t in self.turn_metrics if not t.get('interrupted', False)]
        
        if not valid_turns:
            return
        
        # Calculate averages for each metric
        metrics_to_avg = ['total_latency', 'eou_delay', 'ttft', 'ttfb']
        
        for metric in metrics_to_avg:
            values = [t.get(metric, 0) for t in valid_turns if t.get(metric, 0) > 0]
            if values:
                avg_key = f'avg_{metric}'
                self.session_data[avg_key] = sum(values) / len(values)
    
    def _save_to_excel(self):
        """Save session and turn metrics to Excel files"""
        session_id = self.session_data['session_id']
        
        # Create filename with timestamp
        filename = f"voice_agent_metrics_{session_id}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Session Summary Sheet
                session_df = pd.DataFrame([self.session_data])
                session_df.to_excel(writer, sheet_name='Session_Summary', index=False)
                
                # Turn Details Sheet
                if self.turn_metrics:
                    turn_df = pd.DataFrame(self.turn_metrics)
                    turn_df.to_excel(writer, sheet_name='Turn_Details', index=False)
                
                # Latency Analysis Sheet
                self._create_latency_analysis_sheet(writer)
            
            logger.info(f"Metrics saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save metrics to Excel: {e}")
            # Fallback: save as CSV
            self._save_as_csv_fallback(session_id)
    
    def _create_latency_analysis_sheet(self, writer):
        """Create a detailed latency analysis sheet"""
        if not self.turn_metrics:
            return
        
        valid_turns = [t for t in self.turn_metrics if not t.get('interrupted', False)]
        
        if not valid_turns:
            return
        
        analysis_data = []
        
        # Overall statistics
        latencies = [t.get('total_latency', 0) for t in valid_turns if t.get('total_latency', 0) > 0]
        eou_delays = [t.get('eou_delay', 0) for t in valid_turns if t.get('eou_delay', 0) > 0]
        ttfts = [t.get('ttft', 0) for t in valid_turns if t.get('ttft', 0) > 0]
        ttfbs = [t.get('ttfb', 0) for t in valid_turns if t.get('ttfb', 0) > 0]
        
        if latencies:
            analysis_data.extend([
                {'Metric': 'Total Latency', 'Average': sum(latencies)/len(latencies), 
                 'Min': min(latencies), 'Max': max(latencies), 'Count': len(latencies)},
                {'Metric': 'EOU Delay', 'Average': sum(eou_delays)/len(eou_delays) if eou_delays else 0, 
                 'Min': min(eou_delays) if eou_delays else 0, 'Max': max(eou_delays) if eou_delays else 0, 'Count': len(eou_delays)},
                {'Metric': 'TTFT', 'Average': sum(ttfts)/len(ttfts) if ttfts else 0, 
                 'Min': min(ttfts) if ttfts else 0, 'Max': max(ttfts) if ttfts else 0, 'Count': len(ttfts)},
                {'Metric': 'TTFB', 'Average': sum(ttfbs)/len(ttfbs) if ttfbs else 0, 
                 'Min': min(ttfbs) if ttfbs else 0, 'Max': max(ttfbs) if ttfbs else 0, 'Count': len(ttfbs)}
            ])
        
        # Performance thresholds
        analysis_data.extend([
            {'Metric': 'Turns > 2s latency', 'Count': len([l for l in latencies if l > 2.0])},
            {'Metric': 'Turns > 1s latency', 'Count': len([l for l in latencies if l > 1.0])},
            {'Metric': 'Turns < 0.5s latency', 'Count': len([l for l in latencies if l < 0.5])},
        ])
        
        analysis_df = pd.DataFrame(analysis_data)
        analysis_df.to_excel(writer, sheet_name='Latency_Analysis', index=False)
    
    def _save_as_csv_fallback(self, session_id: str):
        """Fallback method to save as CSV if Excel fails"""
        try:
            # Save session summary
            session_df = pd.DataFrame([self.session_data])
            session_csv = os.path.join(self.output_dir, f"session_summary_{session_id}.csv")
            session_df.to_csv(session_csv, index=False)
            
            # Save turn details
            if self.turn_metrics:
                turn_df = pd.DataFrame(self.turn_metrics)
                turn_csv = os.path.join(self.output_dir, f"turn_details_{session_id}.csv")
                turn_df.to_csv(turn_csv, index=False)
            
            logger.info(f"Metrics saved as CSV files in: {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save CSV fallback: {e}")
    
    def get_average_latency(self) -> float:
        """Get the current average latency"""
        valid_turns = [t for t in self.turn_metrics if not t.get('interrupted', False)]
        latencies = [t.get('total_latency', 0) for t in valid_turns if t.get('total_latency', 0) > 0]
        
        if latencies:
            return sum(latencies) / len(latencies)
        return 0.0
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        stats = self.session_data.copy()
        stats['current_avg_latency'] = self.get_average_latency()
        return stats 