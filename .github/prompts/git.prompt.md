---
description: "Comprehensive Git operations with strict process adherence, safety checks, and automated workflow management"
---

# Git - Comprehensive Git Operations & Workflow Management

Apply the [general coding guidelines](./general.instructions.md) to all Git operations and commit messages.

**Command:** `/git`

## Purpose

Execute comprehensive Git operations with strict process adherence, safety checks, and automated workflow management across the entire development lifecycle.

## Usage

```
/git [subcommand] [options]
```

## Message File Management

**CRITICAL**: All commit messages, PR descriptions, and other long-form text content must be written to temporary files to prevent terminal line breaks and formatting issues.

**Process:**

1. **Temp Directory Setup**

   - Ensure `temp/` directory exists
   - Verify `temp/` is added to `.gitignore`
   - Create necessary temporary files

2. **File-based Message Handling**

   - Write commit messages to `temp/commit.txt`
   - Write PR descriptions to `temp/pr_body.txt`
   - Write issue descriptions to `temp/issue.txt`
   - Use `git commit -F temp/commit.txt` instead of `-m` flag
   - Use `gh pr create --title "Title" --body-file temp/pr_body.txt`

3. **Cleanup**
   - Delete temporary files after successful operations
   - Ensure temp directory is clean between operations
   - Handle cleanup even if operations fail

**File Usage Examples:**

```bash
# Instead of: git commit -m "Long message that might break..."
echo "commit message content" > temp/commit.txt
git commit -F temp/commit.txt
rm temp/commit.txt

# Instead of: gh pr create --body "Long body..."
echo "PR body content" > temp/pr_body.txt
gh pr create --title "Title" --body-file temp/pr_body.txt
rm temp/pr_body.txt
```

## Subcommands

### `/git commit` - Strict Commit Process

Execute the complete commit workflow with automated checks and conventional commit formatting.

**Process:**

1. **Pre-commit Validation**

   - Check git status to identify all changed files
   - Run linting and formatting checks
   - Execute relevant tests
   - Validate build process
   - Check for sensitive data exposure

2. **Staging Review**

   - Display all changes for review using git status
   - Confirm intent for each modified file
   - Validate file additions/deletions
   - Check for unintended changes

3. **Commit Message Generation**

   - Create commits for individual files or group related changes
   - Generate descriptive commit messages that briefly describe changes
   - Write commit message to `temp/commit.txt`
   - Follow Conventional Commits specification when appropriate
   - Include breaking change indicators
   - Reference related issues/tickets

4. **Final Validation**
   - Confirm commit message accuracy
   - Verify staged changes match intent
   - Execute final safety checks
   - Use `git commit -F temp/commit.txt` for committing
   - Clean up temporary files after successful commit

**Conventional Commit Format:**

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:** feat, fix, docs, style, refactor, perf, test, build, ci, chore

### `/git pr` - Pull Request Creation

Create pull requests using GitHub CLI following a structured process.

**Process:**

1. **Status Check**

   - Run `git status` to check for uncommitted changes

2. **Staging (if needed)**

   - Run `git add .` to add all changes to staging area

3. **Commit (if needed)**

   - Write commit message to `temp/commit.txt`
   - Run `git commit -F temp/commit.txt` with descriptive message
   - Delete commit file in temp/commit.txt

4. **Push (if needed)**

   - Run `git push` to push changes to remote repository

5. **Branch Verification**

   - Run `git branch` to check current branch

6. **Change Analysis**

   - Run `git log main..[current branch]` to see commits on current branch
   - Run `git diff --name-status main` to check what files have been changed

7. **PR Creation**
   - Write PR body content to `temp/pr_body.txt`
   - Use `gh pr create --title "Title goes here..." --body-file temp/pr_body.txt`
   - Include comprehensive description of changes in the file
   - Clean up temporary files after PR creation

### `/git branch` - Feature Branch Management

Create and manage feature branches with proper naming conventions and workflow integration.

**Process:**

1. **Branch Planning**

   - Analyze current branch status
   - Determine appropriate base branch
   - Generate descriptive branch name
   - Validate naming convention compliance

2. **Branch Creation**

   - Ensure clean working directory
   - Create branch from appropriate base
   - Set up tracking relationships
   - Configure branch-specific settings

3. **Workflow Setup**
   - Initialize any required branch-specific configurations
   - Set up CI/CD pipeline associations
   - Configure code review requirements

**Naming Convention:**

```
<type>/<ticket-id>-<brief-description>
```

Examples: `feature/PROJ-123-user-authentication`, `fix/PROJ-456-memory-leak`

### `/git issue` - GitHub Issue Generation

Generate comprehensive GitHub issues from current development context.

**Process:**

1. **Context Analysis**

   - Analyze current codebase state
   - Identify related components
   - Gather relevant error messages/logs
   - Determine issue scope and impact

2. **Issue Template Population**

   - Select appropriate issue template
   - Generate descriptive title and description
   - Write issue content to `temp/issue.txt`
   - Add relevant labels and milestones
   - Include reproduction steps if applicable

3. **Documentation Generation**
   - Create detailed problem description in temporary file
   - Include system environment details
   - Add code examples and error logs
   - Suggest potential solutions or workarounds
   - Use `gh issue create --title "Title" --body-file temp/issue.txt`
   - Clean up temporary files after issue creation

**Issue Template Structure:**

```markdown
## Issue Description

[Clear, concise description of the problem or feature request]

## Steps to Reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior

[What should happen]

## Actual Behavior

[What currently happens]

## Environment

- **OS**: [Operating system]
- **Node Version**: [Version]
- **Browser**: [If applicable]
- **Dependencies**: [Relevant package versions]

## Additional Context

[Screenshots, logs, or other relevant information]

## Proposed Solution

[If available, suggest potential fixes or approaches]
```

### `/git merge` - Safe Branch Merging

Merge branches with comprehensive safety checks, conflict resolution, and cleanup.

**Process:**

1. **Pre-merge Validation**

   - Verify all tests pass on source branch
   - Confirm code review approval
   - Check for merge conflicts
   - Validate CI/CD pipeline status

2. **Merge Strategy Selection**

   - Determine appropriate merge strategy (merge, squash, rebase)
   - Consider project workflow requirements
   - Evaluate commit history preservation needs

3. **Conflict Resolution**

   - Identify and analyze merge conflicts
   - Provide guided resolution strategies
   - Validate resolution completeness
   - Run tests after conflict resolution

4. **Post-merge Cleanup**
   - Delete merged feature branches
   - Update local branch tracking
   - Trigger deployment pipelines if configured
   - Notify relevant stakeholders

**Merge Strategies:**

- **Merge Commit**: Preserves branch history, creates merge commit
- **Squash and Merge**: Combines commits into single commit
- **Rebase and Merge**: Linear history without merge commits

### `/git release` - Release Preparation & Management

Prepare releases with automated changelog generation, versioning, and deployment preparation.

**Process:**

1. **Release Planning**

   - Analyze changes since last release
   - Determine semantic version increment
   - Validate release readiness criteria
   - Check for breaking changes

2. **Version Management**

   - Update version numbers in package files
   - Generate or update changelog
   - Create release branch if needed
   - Tag release appropriately

3. **Documentation Generation**

   - Generate comprehensive changelog
   - Update API documentation
   - Create migration guides for breaking changes
   - Prepare release notes

4. **Release Validation**
   - Run full test suite
   - Validate build processes
   - Check deployment readiness
   - Confirm rollback procedures

**Semantic Versioning:**

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Changelog Format:**

```markdown
# Changelog

## [Version] - YYYY-MM-DD

### Added

- New features

### Changed

- Changes in existing functionality

### Deprecated

- Soon-to-be removed features

### Removed

- Removed features

### Fixed

- Bug fixes

### Security

- Security improvements
```

## Safety Checks & Validations

### Pre-operation Checks

- [ ] Working directory is clean
- [ ] Local branch is up to date
- [ ] No uncommitted changes
- [ ] Tests are passing
- [ ] Build is successful
- [ ] `temp/` directory exists and is in `.gitignore`

### Code Quality Checks

- [ ] Linting passes
- [ ] Formatting is consistent
- [ ] No TypeScript errors
- [ ] Security vulnerabilities addressed
- [ ] Performance implications reviewed

### Process Validations

- [ ] Conventional commit format
- [ ] Branch naming conventions
- [ ] Pull request requirements met
- [ ] Code review approvals obtained
- [ ] CI/CD pipeline success
- [ ] Temporary files cleaned up after operations

## Integration with Project Workflow

### Task Management Integration

- Link commits to specific tasks
- Update task status based on commit activity
- Generate task completion reports
- Track development progress

### CI/CD Pipeline Integration

- Trigger appropriate pipeline stages
- Validate deployment readiness
- Monitor build and test results
- Coordinate release deployments

### Team Collaboration

- Notify relevant team members
- Update project documentation
- Coordinate code review processes
- Manage merge conflicts collaboratively

## Error Handling & Recovery

### Conflict Resolution

- Provide guided conflict resolution
- Suggest resolution strategies
- Validate resolution completeness
- Offer rollback options if needed

### Failed Operations

- Detailed error analysis and reporting
- Suggested remediation steps
- Safe rollback procedures
- Prevention strategies for future occurrences
- Clean up temporary files even after failures

### Recovery Procedures

- Workspace cleanup after failed operations
- Branch restoration capabilities
- Commit history recovery
- Lost work recovery strategies
- Temporary file cleanup and recovery

## Best Practices

### Commit Hygiene

- Atomic commits with single responsibility
- Descriptive commit messages
- Logical change grouping
- Avoid commits with multiple unrelated changes
- Always use file-based commit messages for complex commits

### Branch Management

- Short-lived feature branches
- Regular synchronization with main branch
- Clean branch history
- Proper branch cleanup after merging

### Release Management

- Regular, predictable release cycles
- Comprehensive testing before releases
- Clear communication of breaking changes
- Proper versioning and documentation

### File Management

- Always ensure `temp/` is in `.gitignore`
- Clean up temporary files after each operation
- Handle file cleanup in error scenarios
- Use appropriate temporary file names for different operations

## Security Considerations

### Sensitive Data Protection

- Scan for accidentally committed secrets
- Validate .gitignore effectiveness
- Check for exposed API keys or passwords
- Ensure proper environment variable usage
- Verify `temp/` directory is properly ignored

### Access Control

- Validate branch protection rules
- Confirm required review processes
- Check merge permissions
- Audit commit signing requirements

## Monitoring & Reporting

### Operation Metrics

- Track commit frequency and patterns
- Monitor branch lifecycle duration
- Measure code review turnaround times
- Analyze merge conflict frequency

### Quality Metrics

- Code review approval rates
- Test coverage trends
- Build success rates
- Security vulnerability resolution times

This comprehensive Git workflow system ensures consistent, safe, and efficient version control operations while maintaining high code quality and team collaboration standards.
