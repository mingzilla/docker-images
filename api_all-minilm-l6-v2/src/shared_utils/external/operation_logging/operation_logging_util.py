"""Common operation logging utility for consistent timing and progress tracking.

This utility provides the foundation for module-specific OperationLogger classes,
handling generic timing mechanics, log formatting, and context management.
It follows the Python style guide rule #5 by extracting pure computation logic
into static utility methods.
"""

import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PhaseStats:
    """Statistics for a processing phase."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    operations: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Get phase duration in seconds."""
        return (self.end_time or time.time()) - self.start_time


@dataclass
class BatchStats:
    """Statistics for a batch operation."""
    batch_number: int
    batch_size: int
    start_time: float
    operations: Dict[str, float] = field(default_factory=dict)
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    
    @property
    def duration(self) -> float:
        """Get batch duration in seconds."""
        return time.time() - self.start_time


class OperationLoggingUtil:
    """Static utility for operation logging mechanics.
    
    Provides common timing, formatting, and logging functionality that can be
    used by module-specific OperationLogger classes. This class handles the
    pure computation aspects while module-specific classes handle context.
    """
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration (e.g., "15.2s", "1.3m", "2.1h")
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    @staticmethod
    def format_batch_timing(batch_stats: BatchStats) -> str:
        """Format batch timing in bullet-point format.
        
        Args:
            batch_stats: Batch statistics to format
            
        Returns:
            Formatted timing string with bullet points
        """
        operations_str = ", ".join(
            f"{op}={dur:.4f}" for op, dur in batch_stats.operations.items()
        )
        
        timing_parts = [f"batch_size={batch_stats.batch_size}"]
        if operations_str:
            timing_parts.append(operations_str)
        timing_parts.append(f"total={batch_stats.duration:.4f}")
        
        return f"Batch {batch_stats.batch_number} timing (seconds):\n- " + ", ".join(timing_parts) + "\n"

    @staticmethod
    def log_operation_details(operation: str, duration: float, details: Dict[str, Any] = None) -> None:
        """Log operation details in bullet-point format.

        Args:
            operation: Operation name
            duration: Duration in seconds
            details: Additional details to log
        """
        details = details or {}
        details_str = ", ".join(f"{k}={v}" for k, v in details.items())

        if details_str:
            logger.info(f"{operation}:\n- duration={duration:.4f}s, {details_str}")
        else:
            logger.info(f"{operation}:\n- duration={duration:.4f}s")

    @staticmethod
    def log_phase_summary(phases: List[PhaseStats], module_name: str) -> None:
        """Log summary of all phases.

        Args:
            phases: List of completed phases
            module_name: Name of the module for context
        """
        if not phases:
            return

        logger.info(f"{module_name} Processing Summary:")
        for phase in phases:
            if phase.end_time:  # Only log completed phases
                duration_str = OperationLoggingUtil.format_duration(phase.duration)
                logger.info(f"- {phase.name}: {duration_str}")

    @staticmethod
    def validate_timing_data(batch_stats: BatchStats) -> List[str]:
        """Validate batch timing data for consistency.

        Args:
            batch_stats: Batch statistics to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if batch_stats.batch_size <= 0:
            errors.append("Batch size must be > 0")

        if batch_stats.duration < 0:
            errors.append("Batch duration cannot be negative")

        # Check for unreasonable operation times (> total batch time)
        for op_name, op_duration in batch_stats.operations.items():
            if op_duration < 0:
                errors.append(f"Operation '{op_name}' duration cannot be negative")
            elif op_duration > batch_stats.duration + 1.0:  # Allow 1s tolerance
                errors.append(f"Operation '{op_name}' duration exceeds batch duration")

        return errors


class BaseOperationTracker:
    """Base class for operation tracking with common functionality.

    This class provides the common mechanics that module-specific OperationLogger
    classes can inherit from or compose with. It handles phases, batches, and
    timing without being tied to specific parameter types.
    """

    def __init__(self, module_name: str):
        """Initialize operation tracker.

        Args:
            module_name: Name of the module being tracked
        """
        self.module_name = module_name
        self.start_time = time.time()
        self.phases: List[PhaseStats] = []
        self.current_phase: Optional[PhaseStats] = None
        self.current_batch: Optional[BatchStats] = None
        self.error_count = 0
        self.success = True

    def start_phase(self, phase_name: str) -> None:
        """Start a new processing phase.

        Args:
            phase_name: Name of the phase (e.g., "service_validation", "batch_processing")
        """
        # Complete current phase if exists
        if self.current_phase and not self.current_phase.end_time:
            self.current_phase.end_time = time.time()

        # Start new phase
        self.current_phase = PhaseStats(phase_name, time.time())
        self.phases.append(self.current_phase)
        print("\n")
        logger.info(f"Phase started: {phase_name}")

    def start_batch(self, batch_number: int, batch_size: int) -> 'BatchContext':
        """Start tracking a batch operation.

        Args:
            batch_number: Sequential batch number
            batch_size: Number of items in batch

        Returns:
            Batch context for tracking operations
        """
        self.current_batch = BatchStats(batch_number, batch_size, time.time())
        return BatchContext(self, self.current_batch)

    def log_operation(self, operation: str, duration: float, details: Dict[str, Any] = None) -> None:
        """Log a completed operation.

        Args:
            operation: Operation name
            duration: Duration in seconds
            details: Additional details to log
        """
        # Add to current phase if exists
        if self.current_phase:
            self.current_phase.operations.append({
                'operation': operation,
                'duration': duration,
                'details': details or {}
            })

        # Log the operation
        OperationLoggingUtil.log_operation_details(operation, duration, details)

    def record_error(self, error_message: str) -> None:
        """Record an error during processing.

        Args:
            error_message: Description of the error
        """
        self.error_count += 1
        self.success = False
        logger.error(f"Error recorded: {error_message}")

    def get_total_duration(self) -> float:
        """Get total processing duration in seconds."""
        return time.time() - self.start_time

    def log_final_summary(self) -> None:
        """Log final processing summary."""
        total_duration = self.get_total_duration()

        if self.success:
            logger.info(f"=== {self.module_name} Processing Completed Successfully ===")
        else:
            logger.error(f"=== {self.module_name} Processing Failed ===")
            logger.error(f"Total errors: {self.error_count}")

        logger.info(f"Total Duration: {OperationLoggingUtil.format_duration(total_duration)}")

        # Log phase summary
        OperationLoggingUtil.log_phase_summary(self.phases, self.module_name)


class BatchContext:
    """Context manager for tracking batch operations.

    Provides a clean interface for tracking sub-operations within a batch
    and automatically logs batch completion with timing details.
    """

    def __init__(self, tracker: BaseOperationTracker, batch_stats: BatchStats):
        """Initialize batch context.

        Args:
            tracker: Parent operation tracker
            batch_stats: Batch statistics to update
        """
        self.tracker = tracker
        self.batch_stats = batch_stats
        self._operation_start_times: Dict[str, float] = {}

    @property
    def operations(self) -> Dict[str, float]:
        """Get operation timings dictionary."""
        return self.batch_stats.operations

    @property
    def duration(self) -> float:
        """Get current batch duration in seconds."""
        return self.batch_stats.duration
    
    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation within this batch.
        
        Args:
            operation_name: Name of the operation (e.g., "transformation", "upload")
        """
        self._operation_start_times[operation_name] = time.time()
    
    def end_operation(self, operation_name: str) -> None:
        """End timing an operation and record duration.
        
        Args:
            operation_name: Name of the operation to end
        """
        if operation_name in self._operation_start_times:
            duration = time.time() - self._operation_start_times[operation_name]
            self.batch_stats.operations[operation_name] = duration
            del self._operation_start_times[operation_name]
    
    def complete_batch(self, success_count: Optional[int] = None, error_count: Optional[int] = None) -> None:
        """Complete the batch and log timing summary.
        
        Args:
            success_count: Number of successfully processed items
            error_count: Number of items that failed processing
        """
        self.batch_stats.success_count = success_count
        self.batch_stats.error_count = error_count
        
        # Validate timing data
        validation_errors = OperationLoggingUtil.validate_timing_data(self.batch_stats)
        if validation_errors:
            logger.warning(f"Batch timing validation issues: {'; '.join(validation_errors)}")
        
        # Log batch completion
        timing_msg = OperationLoggingUtil.format_batch_timing(self.batch_stats)
        logger.info(timing_msg)
        
        # Update tracker error count
        if error_count and error_count > 0:
            self.tracker.error_count += error_count


# Context manager for operation timing
class OperationTimer:
    """Context manager for timing individual operations.
    
    Usage:
        with OperationTimer() as timer:
            # do work
        duration = timer.duration
    """
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


if __name__ == "__main__":
    # Test the operation logging utilities
    print("Testing OperationLoggingUtil...")
    
    # Test duration formatting
    test_durations = [5.234, 65.7, 3721.5]
    for duration in test_durations:
        formatted = OperationLoggingUtil.format_duration(duration)
        print(f"Duration {duration}s -> {formatted}")
    
    # Test batch stats formatting
    batch_stats = BatchStats(
        batch_number=1,
        batch_size=1000,
        start_time=time.time() - 5.0
    )
    batch_stats.operations = {
        "transformation": 0.0091,
        "upload": 0.2777
    }
    
    formatted = OperationLoggingUtil.format_batch_timing(batch_stats)
    print(f"\nBatch formatting:\n{formatted}")
    
    # Test operation tracker
    tracker = BaseOperationTracker("TEST_MODULE")
    tracker.start_phase("validation")
    time.sleep(0.1)  # Simulate work
    tracker.start_phase("processing")
    
    batch_ctx = tracker.start_batch(1, 100)
    batch_ctx.start_operation("test_op")
    time.sleep(0.05)  # Simulate work
    batch_ctx.end_operation("test_op")
    batch_ctx.complete_batch(success_count=95, error_count=5)
    
    tracker.log_final_summary()
    print("✅ OperationLoggingUtil test completed")