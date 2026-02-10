# Contributing to FinOps SaaS

Thank you for your interest in contributing to the FinOps SaaS platform! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Node.js 18+, Python 3.10+, Go 1.21+ (depending on component)
- Docker and Docker Compose
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/sivaatluri/fintek.git
cd fintek

# Install dependencies
make install

# Start development tools
make tools

# Run migrations and seed data
make bootstrap
```

## Development Process

### 1. Create an Issue

Before starting work:
- Check if an issue already exists
- Create a new issue describing the bug or feature
- Wait for maintainer feedback before starting work

### 2. Fork and Branch

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/fintek.git
cd fintek

# Add upstream remote
git remote add upstream https://github.com/sivaatluri/fintek.git

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run linters
make lint

# Run tests
make test

# Run smoke tests
make smoke-test
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Go to GitHub and create a Pull Request
- Fill in the PR template
- Link related issues
- Request review from maintainers

## Coding Standards

### General

- **DRY (Don't Repeat Yourself)**: Avoid code duplication
- **SOLID Principles**: Follow object-oriented design principles
- **YAGNI**: You Aren't Gonna Need It - don't over-engineer
- **Clean Code**: Write self-documenting code with clear names

### TypeScript/JavaScript

- Use TypeScript for type safety
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use async/await over promises
- Prefer const over let, never use var
- Use functional programming patterns where appropriate

```typescript
// Good
const getUserData = async (userId: string): Promise<User> => {
  const user = await userRepository.findById(userId);
  if (!user) {
    throw new NotFoundError('User not found');
  }
  return user;
};

// Bad
function getUserData(userId) {
  return userRepository.findById(userId).then(user => {
    if (!user) throw new Error('User not found');
    return user;
  });
}
```

### Python

- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Use docstrings for functions and classes
- Prefer list comprehensions over loops when appropriate

```python
# Good
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the list."""
    return [user for user in users if user.is_active]

# Bad
def get_active_users(users):
    result = []
    for user in users:
        if user.is_active:
            result.append(user)
    return result
```

### Go

- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Use `gofmt` for formatting
- Handle errors explicitly
- Use interfaces for abstraction

## Testing Guidelines

### Test Coverage

- Aim for >80% code coverage
- Write unit tests for all new functions
- Write integration tests for API endpoints
- Write e2e tests for critical user flows

### Test Structure

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create a new user with valid data', async () => {
      // Arrange
      const userData = { email: 'test@example.com', name: 'Test User' };
      
      // Act
      const user = await userService.createUser(userData);
      
      // Assert
      expect(user.email).toBe(userData.email);
      expect(user.id).toBeDefined();
    });

    it('should throw error with duplicate email', async () => {
      // Test implementation
    });
  });
});
```

### Test Types

1. **Unit Tests**: Test individual functions/classes
   - Location: `*.test.ts`, `*_test.py`, `*_test.go`
   - Run: `make test-unit`

2. **Integration Tests**: Test service interactions
   - Location: `tests/integration-tests/`
   - Run: `make test-integration`

3. **E2E Tests**: Test full user workflows
   - Location: `tests/e2e/`
   - Run: `make test-e2e`

4. **Contract Tests**: Test API contracts
   - Location: `tests/contract-tests/`

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Examples

```
feat(auth): add SAML SSO support

Implement SAML authentication flow with support for
multiple identity providers.

Closes #123
```

```
fix(api): handle null values in cost data

Prevent crashes when processing cost records with
missing fields.

Fixes #456
```

## Pull Request Process

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new linter warnings
- [ ] Commits follow convention
- [ ] PR description is clear

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code reviewed
- [ ] Tests added
- [ ] Documentation updated
```

### Review Process

1. Maintainers will review your PR
2. Address feedback and push updates
3. Once approved, maintainer will merge
4. Branch will be deleted after merge

## Documentation

### Update Documentation When:

- Adding new features
- Changing APIs
- Modifying configuration
- Adding new services or packages
- Changing architecture

### Documentation Locations

- **Architecture**: `/docs/architecture/`
- **API Docs**: `/docs/api/`
- **Runbooks**: `/docs/runbooks/`
- **Personas**: `/docs/personas/`
- **Code Comments**: Inline in source files

### Writing Style

- Use clear, concise language
- Include code examples
- Add diagrams when helpful
- Keep it up-to-date

## Questions?

- Open an issue with the `question` label
- Check existing documentation
- Ask in discussions

Thank you for contributing! 🎉
