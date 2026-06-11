"""Loop orchestrator for continuous pipeline execution with throttling."""
from pathlib import Path
import signal
import sys
import time
import logging
from typing import Callable

from pipeline.core.config import AppConfig

logger = logging.getLogger(__name__)


class LoopOrchestrator:
    """Manages continuous pipeline execution with configurable throttling."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._interrupted = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
    
    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._interrupted = True
    
    def run_loop(
        self,
        run_single_cycle: Callable[[], dict],
        max_cycles: int | None = None,
        until_empty: bool = False,
    ):
        """
        Run the pipeline in loop mode.
        
        Args:
            run_single_cycle: Function that executes one complete pipeline cycle.
                             Must return a dict with keys: 'work_processed', 'errors'
            max_cycles: Maximum number of cycles to run (overrides config if provided)
            until_empty: Stop when no work is found in a cycle
        """
        cfg = self.config.runtime
        cycle_limit = max_cycles if max_cycles is not None else cfg.max_cycles
        cycle_count = 0
        consecutive_empty_cycles = 0
        
        logger.info("Starting loop mode with conservative throttling")
        logger.info(f"Configuration: loop_interval={cfg.loop_interval_seconds}s, "
                   f"idle_interval={cfg.idle_interval_seconds}s, "
                   f"error_cooldown={cfg.error_cooldown_seconds}s")
        
        while not self._interrupted:
            if cycle_limit is not None and cycle_count >= cycle_limit:
                logger.info(f"Reached maximum cycles ({cycle_limit}), stopping.")
                break
            
            cycle_count += 1
            logger.info(f"=== Starting cycle {cycle_count} ===")
            
            try:
                result = run_single_cycle()
                work_processed = result.get('work_processed', False)
                errors_occurred = result.get('errors', False)
                
                if work_processed:
                    consecutive_empty_cycles = 0
                    if errors_occurred:
                        sleep_time = cfg.error_cooldown_seconds
                        logger.info(f"Cycle completed with errors. Cooldown: {sleep_time}s")
                    else:
                        sleep_time = cfg.loop_interval_seconds
                        logger.info(f"Cycle completed with work processed. Next cycle in: {sleep_time}s")
                else:
                    consecutive_empty_cycles += 1
                    sleep_time = cfg.idle_interval_seconds
                    logger.info(f"No work processed in this cycle (empty #{consecutive_empty_cycles}). "
                               f"Idle wait: {sleep_time}s")
                    
                    if until_empty and consecutive_empty_cycles >= 1:
                        logger.info("No work found and --until-empty was specified, stopping.")
                        break
                
                if self._interrupted:
                    logger.info("Interrupted during cycle processing, exiting.")
                    break
                
                logger.info(f"Sleeping for {sleep_time} seconds...")
                self._interruptible_sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in cycle {cycle_count}: {e}", exc_info=True)
                consecutive_empty_cycles += 1
                sleep_time = cfg.error_cooldown_seconds
                logger.info(f"Error cooldown: {sleep_time}s")
                
                if self._interrupted:
                    break
                    
                self._interruptible_sleep(sleep_time)
        
        logger.info(f"Loop mode stopped after {cycle_count} cycles.")
    
    def _interruptible_sleep(self, seconds: float):
        """Sleep in small increments, checking for interrupts."""
        interval = 1.0  # Check every second
        elapsed = 0.0
        while elapsed < seconds and not self._interrupted:
            time.sleep(min(interval, seconds - elapsed))
            elapsed += interval
