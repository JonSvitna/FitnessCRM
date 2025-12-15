# Contributing to Fitness CRM

Thank you for your interest in contributing to Fitness CRM! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Maintain professional communication

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+
- Git

### Setup Development Environment

1. **Fork and Clone**
```bash
git clone https://github.com/YOUR_USERNAME/FitnessCRM.git
cd FitnessCRM
```

2. **Frontend Setup**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

3. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

4. **Database Setup**
```bash
# Create PostgreSQL database
createdb fitnesscrm

# Initialize with sample data
python init_db.py seed
```

## Development Workflow

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/add-search`)
- `bugfix/` - Bug fixes (e.g., `bugfix/fix-email-validation`)
- `hotfix/` - Urgent production fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example**:
```
feat(trainers): add search functionality

Implemented trainer search with filters for name, email, and specialization.
Added debouncing to improve performance.

Closes #123
```

## Coding Standards

### Frontend (JavaScript)

**Style Guide**:
- Use ES6+ features
- 2 spaces for indentation
- Use semicolons
- Use template literals for string interpolation
- Use arrow functions for callbacks
- Use async/await over promises

**Example**:
```javascript
// Good
const fetchTrainers = async () => {
  try {
    const response = await trainerAPI.getAll();
    return response.data;
  } catch (error) {
    console.error('Error fetching trainers:', error);
  }
};

// Avoid
function fetchTrainers() {
  return trainerAPI.getAll().then(function(response) {
    return response.data;
  }).catch(function(error) {
    console.error('Error fetching trainers:', error);
  });
}
```

### Backend (Python)

**Style Guide**:
- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter)
- Use type hints where appropriate
- Write docstrings for all functions and classes

**Example**:
```python
# Good
def create_trainer(data: dict) -> Trainer:
    """Create a new trainer with the provided data.
    
    Args:
        data: Dictionary containing trainer information
        
    Returns:
        Created Trainer object
        
    Raises:
        ValueError: If required fields are missing
    """
    if not data.get('name') or not data.get('email'):
        raise ValueError('Name and email are required')
    
    trainer = Trainer(**data)
    db.session.add(trainer)
    db.session.commit()
    return trainer
```

### CSS/TailwindCSS

- Use Tailwind utility classes primarily
- Custom CSS only when necessary
- Keep custom classes in `@layer components`
- Use semantic class names

## Testing

### Frontend Testing
```bash
cd frontend
npm test
```

### Backend Testing
```bash
cd backend
pytest
```

### Test Coverage
- Aim for 80%+ code coverage
- Write unit tests for all new features
- Include integration tests for API endpoints

## Pull Request Process

### Before Submitting

1. **Update from main branch**
```bash
git checkout main
git pull origin main
git checkout your-feature-branch
git rebase main
```

2. **Run tests**
```bash
# Frontend
cd frontend && npm test

# Backend
cd backend && pytest
```

3. **Check linting**
```bash
# Frontend
npm run lint

# Backend
flake8 .
```

### Submitting a Pull Request

1. **Push your branch**
```bash
git push origin your-feature-branch
```

2. **Create PR on GitHub**
- Use a clear, descriptive title
- Reference any related issues
- Provide detailed description of changes
- Include screenshots for UI changes
- List any breaking changes

3. **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] Manual testing performed
- [ ] All tests passing

## Screenshots (if applicable)
[Add screenshots here]

## Related Issues
Closes #123
```

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged

## Documentation

- Update README.md for major changes
- Update API_DOCUMENTATION.md for API changes
- Update ROADMAP.md if changing planned features
- Add inline comments for complex logic
- Update deployment docs if needed

## Questions?

- Open an issue for bugs or feature requests
- Tag issues with appropriate labels
- Be as specific as possible in issue descriptions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Project website (future)

Thank you for contributing to Fitness CRM! 🎉
