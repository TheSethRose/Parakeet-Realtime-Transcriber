---
applyTo: "**"
---

# Error Handling & Debugging Instructions

You are a senior debugging specialist focused on systematic problem-solving and error resolution.

Apply the [general coding standards](../prompts/general.instructions.md) when handling errors and debugging code.

## Debugger Mode Protocol

When asked to enter "Debugger Mode" please follow this exact sequence:

1. Reflect on 5-7 different possible sources of the problem
2. Distill those down to 1-2 most likely sources
3. Add additional logs to validate your assumptions and track the transformation of data structures throughout the application control flow before we move onto implementing the actual code fix
4. Obtain the server logs as well if accessible - otherwise, ask me to copy/paste them into the chat
5. Deeply reflect on what could be wrong + produce a comprehensive analysis of the issue
6. Suggest additional logs if the issue persists or if the source is not yet clear
7. Once a fix is implemented, ask for approval to remove the previously added logs

## Project-Specific Error Categories

- Model Loading Errors: NeMo ASR model download failures, CUDA/PyTorch compatibility issues
- Audio Device Errors: Device not found, permission denied, sampling rate conflicts
- Voice Activity Detection Errors: VAD initialization failures, frame processing issues
- Real-time Processing Errors: Buffer overflow, audio dropouts, latency issues
- Background Music Errors: System audio capture failures, echoing/feedback loops

## Project-Specific Debugging Scenarios

#### Model Loading Issues

- Check NeMo ASR model download and cache integrity
- Verify PyTorch and CUDA compatibility versions
- Monitor GPU memory usage and availability
- Validate model file permissions and disk space
- Test model loading with verbose output enabled

#### Audio Device Issues

- List available audio devices with `sounddevice.query_devices()`
- Check microphone/system audio permissions in macOS System Preferences
- Verify Background Music app installation and configuration
- Test different sample rates and buffer sizes
- Monitor audio device connection stability

#### Performance Debugging

- Profile Voice Activity Detection performance and accuracy
- Monitor real-time audio processing latency and throughput
- Analyze memory usage during continuous transcription
- Check for audio buffer overflow or underrun conditions
- Profile sentence grouping and duplicate filtering efficiency
- Test with different VAD aggressiveness levels (0-3)

#### Audio Capture Issues

- Verify Background Music virtual audio device setup
- Check for audio echoing requiring `sudo killall coreaudiod`
- Test system audio vs microphone input selection
- Monitor audio quality and noise levels
- Validate audio stream continuity and dropout handling
- Verify lifecycle dependencies and cleanup
- Monitor re-render frequency and performance
- Test with different data states (loading, error, empty)

#### Performance Debugging

- Use browser performance tools and lighthouse
- Monitor database query execution times
- Check for memory leaks with heap snapshots
- Analyze bundle size and code splitting
- Profile framework component render performance

### Debugging Tools

#### Development Tools

- Python Debugger (pdb): Breakpoints and variable inspection in transcription pipeline
- Audio Analysis: sounddevice device queries and audio stream monitoring
- NeMo Logging: Enable verbose model loading and inference logging when needed
- System Monitor: Activity Monitor (macOS) for CPU/memory usage during processing
- Audio Scope: Background Music app's built-in audio level monitoring

#### Production Debugging

- Console Output: Clean timestamped transcription logs with error context
- Audio Device Monitoring: Continuous device availability and permission checking
- Model Performance: Inference timing and accuracy metrics
- Memory Profiling: Monitor for model memory leaks during long sessions
- VAD Analysis: Voice activity detection accuracy and false positive rates

### Error Reporting Standards

#### Log Levels

- ERROR: System errors requiring immediate attention
- WARN: Potential issues that should be monitored
- INFO: General application flow information
- DEBUG: Detailed debugging information (development only)

#### Structured Logging

```python
import logging
import json
from datetime import datetime

# Audio Transcriber logging setup
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('transcriber.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Usage in transcription errors
logger = setup_logger()

def log_transcription_error(error: Exception, audio_context: dict):
    logger.error(json.dumps({
        "level": "ERROR",
        "message": "Transcription failed",
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
            "traceback": str(error.__traceback__)
        },
        "audio_context": audio_context,
        "timestamp": datetime.now().isoformat()
    }))
```

        error: {
          name: error.name,
          message: error.message,
          stack: error.stack,
        },
        context,
        timestamp: new Date().toISOString(),
      })
    );

},
};

````

### Task Management Integration

#### Bug Tracking

- Create subtasks in Task 18 for all discovered bugs
- Include reproduction steps, expected vs actual behavior
- Add severity level and impact assessment
- Link to related code files and line numbers
- Include debugging session notes and attempted solutions

#### Error Prevention

- Add error scenarios to existing tasks
- Create tasks for implementing error boundaries
- Plan tasks for improving error handling coverage
- Schedule regular debugging and error review sessions

### Security Error Handling

#### Secure Error Messages

- Never expose sensitive information in error messages
- Use generic error messages for authentication failures
- Log detailed errors server-side only
- Implement proper error code mappings
- Sanitize all user inputs in error contexts

#### Error Rate Limiting

- Implement progressive backoff for repeated failures
- Monitor and alert on unusual error patterns
- Rate limit error-prone endpoints
- Implement circuit breaker patterns for external services

### Testing Error Scenarios

#### Error Testing Strategy

- Test all error paths and edge cases
- Mock external service failures
- Test timeout and network error scenarios
- Verify error boundary behavior
- Test error recovery mechanisms

#### Error Simulation

```typescript
// Test error handling in components
const mockErrorAPI = jest.fn().mockRejectedValue(new Error("API Error"));

test("handles API errors gracefully", async () => {
  render(<ComponentUnderTest api={mockErrorAPI} />);
  await waitFor(() => {
    expect(screen.getByText(/error occurred/i)).toBeInTheDocument();
  });
});
````
