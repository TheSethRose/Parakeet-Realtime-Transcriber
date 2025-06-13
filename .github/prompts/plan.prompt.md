---
description: "Requirements analysis and implementation planning with clear deliverables, timelines, and success criteria"
---

# Plan - Requirements Analysis & Implementation Planning

Apply the [general coding guidelines](./general.instructions.md) to all planning and analysis activities.

**Command:** `/plan`

## Purpose

Analyze requirements thoroughly and create detailed implementation plans with clear deliverables, timelines, and success criteria. When entering "Planner Mode" or "Architecture Mode", deeply reflect upon the changes being asked and analyze existing code to map the full scope of changes needed. Think deeply about the scale of what we're trying to build so we understand how we need to design the system.

## Usage

```
/plan [feature/project description]
```

## Planner Mode Workflow

When entering Planner Mode or Architecture Mode, the following process will be followed:

1. **Deep Analysis**: Thoroughly analyze the requested changes and examine existing codebase to understand full scope and scale of the system
2. **Architecture Tradeoff Analysis**: Generate a 5 paragraph tradeoff analysis of different ways to design the system considering constraints, scale, performance considerations and requirements
3. **Clarifying Questions**: Ask 4-6 targeted questions based on findings to assess the scale of the system we're trying to build
4. **System Design Architecture**: Draft a comprehensive system design architecture and request approval
5. **Iterative Refinement**: If feedback or questions are provided, engage in conversation to analyze tradeoffs further and revise the architecture - once revised, ask for approval again
6. **Implementation Planning**: Once architecture is approved, work on a plan to implement the architecture based on the provided requirements
7. **Plan Approval**: If feedback is provided on the implementation plan, revise and ask for approval again
8. **Phased Implementation**: Once approved, implement all steps in that plan
9. **Progress Tracking**: After each phase/step completion, provide status updates including:
   - What was just completed
   - What the next steps are
   - Remaining phases after current steps

## Planning Framework

### 1. Requirements Gathering

- **Functional Requirements**: What the system must do
- **Non-Functional Requirements**: Performance, scalability, security
- **User Stories**: User personas and their needs
- **Acceptance Criteria**: Definition of done for each requirement
- **Dependencies**: External systems, APIs, libraries required

### 2. Technical Analysis

- **Current State Assessment**: Existing architecture and capabilities
- **Gap Analysis**: What needs to be built or modified
- **Technology Evaluation**: Stack decisions and tool selection
- **Integration Points**: How new features connect to existing systems
- **Data Flow Mapping**: Information movement through the system

### 3. Architecture Planning

- **System Design**: High-level component architecture
- **Database Schema**: Data structures and relationships
- **API Design**: Endpoints, request/response formats
- **Security Considerations**: Authentication, authorization, data protection
- **Performance Requirements**: Load expectations and optimization needs

### 4. Implementation Strategy

- **Phased Approach**: Break work into manageable iterations
- **MVP Definition**: Minimum viable product scope
- **Feature Prioritization**: Critical path and dependencies
- **Resource Allocation**: Team assignments and skill requirements
- **Timeline Estimation**: Realistic delivery schedules

### 5. Risk Management

- **Technical Risks**: Complexity, unknown technologies
- **Resource Risks**: Availability, skill gaps
- **Timeline Risks**: Dependencies, scope creep
- **Mitigation Strategies**: Backup plans and alternatives

## Output Structure

```markdown
## Project Overview

- **Objective**: [Clear goal statement]
- **Scope**: [What's included/excluded]
- **Success Criteria**: [Measurable outcomes]

## Architecture Tradeoff Analysis

[5 paragraph analysis of different system design approaches considering constraints, scale, performance, and requirements]

## Requirements

### Functional Requirements

1. [Requirement with acceptance criteria]
2. [Requirement with acceptance criteria]

### Non-Functional Requirements

- **Performance**: [Specific metrics]
- **Security**: [Requirements and compliance]
- **Scalability**: [Growth expectations]
- **Accessibility**: [Standards and guidelines]

## Technical Specification

### Architecture Overview

[High-level system design]

### Technology Stack

- **Frontend**: [Technologies and rationale]
- **Backend**: [Technologies and rationale]
- **Database**: [Choice and structure]
- **Infrastructure**: [Hosting and deployment]

### API Design

[Endpoint specifications and data models]

## Implementation Plan

### Phase 1: [Name] (Timeline: [Duration])

- **Tasks**:
  - [ ] [Specific deliverable]
  - [ ] [Specific deliverable]
- **Dependencies**: [Prerequisites]
- **Deliverables**: [Concrete outputs]

### Phase 2: [Name] (Timeline: [Duration])

[Same structure]

### Phase 3: [Name] (Timeline: [Duration])

[Same structure]

## Testing Strategy

- **Unit Testing**: [Coverage requirements]
- **Integration Testing**: [Key scenarios]
- **End-to-End Testing**: [User journey validation]
- **Performance Testing**: [Load and stress testing]

## Deployment Plan

- **Environment Strategy**: [Dev, staging, production]
- **CI/CD Pipeline**: [Automation requirements]
- **Rollback Strategy**: [Risk mitigation]
- **Monitoring**: [Health checks and alerting]

## Risk Assessment

| Risk               | Impact       | Probability  | Mitigation |
| ------------------ | ------------ | ------------ | ---------- |
| [Risk description] | High/Med/Low | High/Med/Low | [Strategy] |

## Success Metrics

- **Technical Metrics**: [Performance, reliability]
- **User Metrics**: [Adoption, satisfaction]
- **Business Metrics**: [ROI, efficiency gains]
```

## Best Practices

- Start with user needs, not technical solutions
- Define clear, measurable success criteria
- Plan for iterative delivery and feedback loops
- Consider maintenance and long-term evolution
- Document assumptions and constraints
- Validate plans with stakeholders before implementation
- Include rollback and recovery strategies
- Plan for both happy path and edge cases
- Deeply analyze existing code before proposing changes
- Ask clarifying questions to ensure complete understanding
- Generate comprehensive tradeoff analysis for different architectural approaches
- Engage in iterative conversation to refine architecture before implementation
- Provide clear progress updates throughout implementation

## Integration

Use this command for:

- New feature development
- System refactoring initiatives
- Performance improvement projects
- Security enhancement planning
- Infrastructure upgrades
