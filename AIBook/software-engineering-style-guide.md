# Personal Software Engineering Style Guide
## For Prototype and Experimental Code

### Overall Philosophy
- This guide is designed for prototype and experimental code
- Focus on functionality and exploration over production-ready features
- Prioritize rapid development and iteration
- Error handling should be minimal until debugging requires it
- Always look to see if the project contains code that can be modified to achieve a goal instead of writing new code.
- Implement one feature at a time, allowing for testing between each.

### Code Organization


#### File Structure
- One class per file
- Main script imports all necessary functionality
- Use meaningful filenames that reflect class purpose
- Group related files in subdirectories when projects grow

#### Class Design
- Each class should have a single responsibility
- Classes should be self-contained with all necessary data and methods
- Avoid inheritance for prototypes unless absolutely necessary
- Favor composition over inheritance
- If a file goes over 500 lines of code, consider refactoring.

### Coding Style

#### Naming Conventions
- Use descriptive variable and function names
- Class names should be CamelCase
- Function and variable names should be snake_case
- Constants should be ALL_CAPS

#### Comments
- Comment intent rather than implementation
- Use docstrings to explain class and function purpose
- TODO comments are acceptable for future improvements
- Leave brief comments for non-obvious code sections

#### Function Design
- Functions should do one thing well
- Keep functions reasonably short (under 50 lines preferred)
- Limit function arguments to what's necessary
- Return values are preferred over modifying parameters

### Testing Approach
- Manual testing is acceptable for early prototypes
- Consider adding basic unit tests for core functionality
- Test edge cases only when they become relevant
- Document known limitations rather than handling every edge case

### Error Handling
- Minimal error handling during initial development
- Add targeted error handling when debugging specific issues
- Use print statements liberally for debugging
- Consider adding logging for more complex debugging scenarios

### Performance Considerations
- Focus on correct functionality first, performance second
- Avoid premature optimization
- Document performance bottlenecks when discovered
- Optimize only critical paths as needed

### Version Control
- Commit frequently with descriptive messages
- Branch when exploring significantly different approaches
- Don't worry about perfect commit history for prototypes
- Tag major milestones for easy reference

### Dependencies
- Minimize external dependencies when possible
- Document all required dependencies clearly
- Consider using virtual environments for dependency isolation
- Prefer standard library solutions when reasonable

### Documentation
- README should outline the purpose and basic usage
- Document assumptions and limitations
- Include basic examples of how to use the code
- Update documentation when major changes occur

### Refactoring Guidelines
- Refactor when code clarity becomes an issue
- Extract repeated code into functions
- Move shared functionality to utility classes
- Consider refactoring before adding new features to problematic areas

### Code Review (Self)
- Review your own code after stepping away from it
- Ask: "Would this make sense to me in a month?"
- Check for obvious bugs and edge cases
- Ensure the code meets its intended purpose

### Experimental Features
- Isolate experimental features in separate modules when possible
- Comment experimental code sections clearly
- Consider feature flags for enabling/disabling experimental features
- Document the status and stability of experimental features
