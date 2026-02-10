# Contributing to Fintek

Thank you for your interest in contributing to Fintek! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker and Docker Compose

### Local Setup

```bash
# Clone the repository
git clone https://github.com/sivaatluri/fintek.git
cd fintek

# Start infrastructure
docker-compose up -d postgres redis kafka trino minio

# Install dependencies for a service
cd services/gateway
pip install -e ".[dev]"

# Run tests
pytest

# Run the service
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

## Project Structure

- `services/` - Microservices (FastAPI)
- `packages/` - Shared Python packages
- `apps/` - Frontend applications
- `connectors/` - Cloud provider connectors
- `infra/` - Infrastructure configuration
- `scripts/` - Utility scripts
- `docs/` - Documentation

## Coding Standards

### Python
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Keep functions small and focused

### TypeScript/React
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and reusable

### General
- Write clear commit messages
- Add tests for new features
- Update documentation
- Keep changes focused and atomic

## Testing

### Backend Tests
```bash
cd services/<service-name>
pytest
```

### Frontend Tests
```bash
cd apps/web
npm test
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update the README if needed
5. Create a pull request with a clear description
6. Wait for review and address feedback

## Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Write clear PR descriptions
- Reference related issues
- Include screenshots for UI changes
- Ensure CI passes

## Code Review Process

- PRs require at least one approval
- Address all review comments
- Keep discussions professional and constructive

## Reporting Bugs

Create an issue with:
- Clear bug description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots if applicable

## Requesting Features

Create an issue with:
- Feature description
- Use case and motivation
- Proposed implementation (optional)
- Examples or mockups (if applicable)

## Documentation

- Update README for significant changes
- Add docstrings to code
- Update API documentation
- Add examples where helpful

## Release Process

1. Update version numbers
2. Update CHANGELOG
3. Create release tag
4. Deploy to production

## Questions?

Feel free to open an issue for any questions or concerns.

Thank you for contributing to Fintek!
