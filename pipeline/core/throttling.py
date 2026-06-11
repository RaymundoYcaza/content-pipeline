"""Throttling utilities for AI calls and pipeline stages."""
import time
import logging
from typing import Callable, TypeVar, Any

from pipeline.core.config import AppConfig
from pipeline.core.retry import retry_with_backoff, RetryError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ThrottledCaller:
    """Wraps AI calls with throttling, retry, and backoff logic."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._last_call_time: float | None = None
    
    def call_with_throttling(
        self,
        func: Callable[[], T],
        description: str = "AI call",
    ) -> T:
        """
        Execute a function with throttling and retry logic.
        
        Args:
            func: The function to execute (typically an AI API call)
            description: Human-readable description for logging
            
        Returns:
            The result of the function call
            
        Raises:
            RetryError: If all retries are exhausted
        """
        cfg = self.config.runtime
        
        # Apply delay since last call if needed
        if self._last_call_time is not None:
            elapsed = time.time() - self._last_call_time
            delay_seconds = cfg.delay_between_calls_ms / 1000.0
            if elapsed < delay_seconds:
                sleep_time = delay_seconds - elapsed
                logger.debug(f"Throttling {description}: waiting {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        # Execute with retry/backoff
        def wrapped():
            result = func()
            self._last_call_time = time.time()
            return result
        
        try:
            result = retry_with_backoff(
                wrapped,
                max_retries=cfg.max_retries,
                base_delay_seconds=cfg.retry_backoff_seconds,
            )
            logger.debug(f"{description} completed successfully")
            return result
        except RetryError as e:
            logger.error(f"{description} failed after retries: {e}")
            raise


def apply_step_delay(config: AppConfig, step_name: str = "pipeline step"):
    """
    Apply delay between pipeline stages.
    
    This should be called after completing a stage that used AI or 
    generated effective transitions.
    
    Args:
        config: Pipeline configuration
        step_name: Name of the completed step for logging
    """
    cfg = config.runtime
    delay_seconds = cfg.delay_between_steps_ms / 1000.0
    
    if delay_seconds > 0:
        logger.info(f"Applying {delay_seconds}s delay after {step_name}")
        time.sleep(delay_seconds)
