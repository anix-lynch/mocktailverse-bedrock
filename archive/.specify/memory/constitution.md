# Mocktailverse Project Constitution

## Code Quality Principles
- Maintain test coverage above 80%
- Use meaningful variable names
- Document complex algorithms
- Keep functions under 50 lines
- Use direct AWS SDK calls without unnecessary abstractions

## Architecture Guidelines
- Prefer composition over inheritance
- Separate business logic from infrastructure
- Use AWS native tools directly (S3, Lambda, DynamoDB)
- CLI-first, reproducible with AWS CLI
- Maximum 3 projects/components for initial implementation
- No future-proofing or over-engineering

## Testing Standards
- Write unit tests before implementation (TDD)
- Integration tests for all Lambda functions
- End-to-end tests for complete data flow
- Use realistic AWS environments over mocks
- Contract tests mandatory before implementation

## AWS Fundamentals
- Emphasize serverless architecture patterns
- Use S3 for raw and processed data layers
- Lambda for transformation layer
- DynamoDB for refined data layer
- Error handling for missing creds or network issues

## Performance Requirements
- Maintain <50ms response time for all user interactions
- Lambda functions should complete within 15 minutes
- Optimize for cold start performance

## Simplicity Rules (Article VII)
- [ ] Using ≤3 projects?
- [ ] No future-proofing?
- [ ] Direct framework usage?

## Anti-Abstraction Rules (Article VIII)
- [ ] Using AWS SDK directly?
- [ ] Single model representation?
- [ ] No unnecessary wrapper layers?

## Integration-First Rules (Article IX)
- [ ] Contracts defined?
- [ ] Contract tests written?
- [ ] Real AWS services for testing?