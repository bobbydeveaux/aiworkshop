# Contributing to F1 Analytics Workshop

Thank you for your interest in contributing to the F1 Analytics Workshop! This document provides guidelines for contributing to the project.

## How to Contribute

### Types of Contributions
- **Data Analysis**: New statistical analyses and insights
- **Visualizations**: Charts, graphs, and interactive visualizations
- **API Enhancements**: Improved API wrapper functions
- **Documentation**: Better documentation and examples
- **Bug Fixes**: Corrections to existing code
- **Performance Improvements**: Code optimization and efficiency

### Getting Started
1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment and install dependencies
4. Create a new branch for your feature/fix
5. Make your changes
6. Test your changes
7. Submit a pull request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/aiworkshop.git
cd aiworkshop

# Create virtual environment
python -m venv f1_analytics
source f1_analytics/bin/activate  # Windows: f1_analytics\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 isort
```

### Code Style Guidelines
- Follow PEP 8 for Python code
- Use meaningful variable names related to F1 terminology
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Keep functions focused and single-purpose

### Testing
- Write tests for new functions using pytest
- Ensure existing tests pass before submitting
- Include edge case testing
- Test with different data scenarios

### API Usage Guidelines
- Respect the Ergast API rate limits (200 requests/hour)
- Cache API responses when possible
- Handle API errors gracefully
- Include appropriate delays between requests

### Documentation
- Update README.md for significant changes
- Add docstrings to new functions
- Include examples in documentation
- Update the getting started guide if needed

### Data Analysis Standards
- Document data sources and collection methods
- Include confidence intervals for estimates
- Validate statistical assumptions
- Consider F1 domain knowledge in analysis
- Provide clear interpretation of results

### Submitting Changes
1. Ensure your code follows the style guidelines
2. Add tests for new functionality
3. Update documentation as needed
4. Create a clear commit message
5. Submit a pull request with:
   - Clear description of changes
   - Rationale for the changes
   - Testing information
   - Screenshots for visualizations

### Pull Request Review Process
- All pull requests require review
- Address reviewer feedback promptly
- Ensure CI checks pass
- Maintain focus on F1 analytics goals

### Issue Reporting
When reporting issues:
- Use clear, descriptive titles
- Provide steps to reproduce
- Include error messages and logs
- Specify your environment details
- Tag with appropriate labels

### Feature Requests
For new features:
- Describe the F1 analysis need
- Explain the expected benefit
- Provide examples if possible
- Consider implementation complexity

## Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers to F1 analytics
- Share knowledge and insights
- Maintain professional communication

## Questions?
- Open an issue for questions
- Tag maintainers for urgent matters
- Join discussions in existing issues
- Propose improvements through issues

Thank you for contributing to F1 analytics! 🏎️