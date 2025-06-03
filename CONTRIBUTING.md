# Contributing to Talisik Short URL

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/qkeluna/talisik-short-url.git
cd talisik-short-url

# Set up development environment
make setup
source venv/bin/activate
```

### 2. Making Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test your changes: `make test`
4. Check code quality: `make lint`
5. Format code: `make format`

### 3. Submitting Changes

1. Push your branch: `git push origin feature/your-feature-name`
2. Create a Pull Request on GitHub
3. Fill out the PR template completely
4. Wait for automated checks to pass
5. Request review from maintainers

## Code Quality Standards

- All code must pass linting (`make lint`)
- All tests must pass (`make test`)
- Code coverage should not decrease
- Follow existing code style and patterns

## Testing

- Write tests for new features
- Ensure all existing tests still pass
- Test both Python SDK and API endpoints
- Use `make test-api` for API testing

## Questions?

Open an issue or ask in the PR discussion!
