# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Rules
- Keep it very concise, don't propose over complicated solutions
- Do not add any speculative features, we don't need it for now
- When completed, remember to mark task as completed in @tasks.md, e.g. `[x]`
- Execute ONE task at a time! Not all tasks in a section at one step!
- NEVER auto-generate daily status updates without explicit user request
- NEVER auto-commit or auto-push to git without explicit user confirmation - always ask first
- Update documentation promptly
- When updating CLI commands, always update @docs/cli_usage.md documentation to reflect the changes
- Use venv when test python script in this code base, e.g. `source venv/bin/activate && python some_code.py`

## Project Overview

See ./requirements.md for more detail about this running project

## Development Commands

Since this appears to be an early-stage project without established build tools, development commands will need to be established as the implementation progresses. Update this section once package management and build systems are in place.

## Key Implementation Notes

- The system uses AI agents for dynamic field creation and information extraction
- Hybrid search combining semantic (RAG) and structured field-based queries
- Version management preserves memory history during updates
- Security and privacy features planned for M2 and later milestones

