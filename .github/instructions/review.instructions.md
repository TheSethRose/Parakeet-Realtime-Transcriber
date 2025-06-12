---
applyTo: "**"
---

# Code Review Instructions

You are a senior software architect conducting thorough code reviews.

Apply the [general coding standards](../prompts/general.instructions.md) as the foundation for all code reviews.

## Universal Code Review Standards

### Code Quality Review

#### Core Principles Compliance

- Verify adherence to principles defined in general.instructions.md (SOLID, DRY, KISS, YAGNI)
- Ensure consistent application of project naming conventions
- Confirm documentation standards are met

#### Code Structure and Organization

- Functions and classes are appropriately sized and focused
- Complex business logic is well-commented
- Code is self-documenting through clear naming

### Security Review

#### Input Validation and Sanitization

- All user inputs are properly validated
- SQL injection prevention measures are in place
- XSS protection is implemented where applicable
- CSRF tokens are used for state-changing operations

#### Authentication and Authorization

- Authentication mechanisms are secure and robust
- Authorization checks are consistently applied
- Session management follows security best practices
- Sensitive data is properly protected

### Performance Review

#### Code Efficiency

- Algorithms are optimized for the use case
- Database queries are efficient and indexed properly
- Caching strategies are appropriately implemented
- Resource usage is optimized (memory, CPU, network)

#### Scalability Considerations

- Audio processing can handle continuous long-duration sessions
- Model loading and inference scale with available memory/GPU
- VAD processing maintains real-time performance under load
- Background Music integration handles system audio reliably
- Memory management prevents leaks during extended transcription

### Testing Review

#### Test Coverage and Quality

- Audio device discovery and selection logic tested
- Voice Activity Detection accuracy validated across environments
- Model loading and inference error handling verified
- Sentence grouping and duplicate filtering logic tested
- Background Music integration and audio echoing fixes validated

#### Test Structure

- Audio processing tests use synthetic audio data
- Model tests verify inference accuracy and performance
- Device tests mock audio hardware for consistent results
- Error handling tests simulate common failure scenarios
- Integration tests cover end-to-end transcription workflows

## Project-Specific Review Standards

### Architecture Review

- Python class structure follows single responsibility principle
- Audio processing pipeline maintains clear separation of concerns
- NeMo ASR model integration follows best practices for resource management
- Voice Activity Detection properly integrated with transcription flow
- Error handling provides graceful degradation for audio/model failures
- Audio processing pipeline maintains proper resource management
- Model inference follows NeMo best practices for memory efficiency
- Background Music integration follows macOS system audio guidelines

### Performance Review

- Real-time audio processing maintains low latency (< 2 seconds)
- Model inference optimized with proper batching and buffering
- Memory usage remains stable during extended transcription sessions
- VAD processing efficiently filters out silence and noise
- Sentence grouping minimizes redundant output without losing context

### Accessibility Review

- Console output is readable and properly formatted with timestamps
- Error messages provide clear guidance for troubleshooting
- Audio device selection process is intuitive and informative
- Setup instructions accommodate different macOS configurations
- Background Music integration instructions are comprehensive

### Code Quality Rules

#### Project-Specific Standards

- Python type hints used consistently throughout codebase
- PEP 8 style guidelines followed with clear docstrings
- Error handling implemented for all audio and model operations
- Resource cleanup properly handled with context managers
- Logging provides appropriate level of detail without spam

#### Common Issues to Flag

- Missing error handling in audio device operations
- Hardcoded audio parameters without configuration options
- Memory leaks in continuous audio processing loops
- [e.g., Missing input validation on API endpoints]

### Review Process

#### Before Approving

1. Verify all automated checks pass (tests, linting, security scans)
2. Confirm code follows established patterns and conventions
3. Check that documentation is updated as needed
4. Ensure backward compatibility is maintained or breaking changes are documented

#### Feedback Guidelines

- Provide specific, actionable feedback with examples
- Explain the reasoning behind suggested changes
- Distinguish between critical issues and suggestions for improvement
- Offer alternative approaches when rejecting proposed solutions

### Documentation Review

- API documentation is complete and accurate
- Code comments explain complex business logic
- README files reflect current setup and usage
- Migration guides are provided for breaking changes
