# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Portfolio website project. (Update this section once the tech stack is chosen and the project is initialized.)

## Build & Development Commands

<!-- Update these once the project is set up -->
<!-- Example for Next.js: -->
<!-- npm run dev        # Start development server -->
<!-- npm run build      # Production build -->
<!-- npm run lint       # Run linter -->
<!-- npm test           # Run tests -->

## Architecture

<!-- Document key architectural decisions here as the project evolves -->
<!-- e.g., routing strategy, styling approach, state management, data fetching -->

## Project Structure

<!-- Fill in once the directory structure is established -->


## Incremental Commits

**Prefer small, verified commits over large batch commits.**

- Split work into logical units and commit each unit as soon as it is verified.
- Avoid mixing unrelated changes in a single commit.
- Run the smallest relevant verification (test/build/typecheck) before each commit.
- Write commit messages that clearly describe intent and scope.
- For broad tasks, produce multiple sequential commits instead of one large final commit.
#### Commit Guidelines
1. Git commit message structure:
	- The commit message should follow this structure:
		'''
		type: subject
		
		body(optional)
		
		footer(optional)
		'''
	- The type should be one of the following:
		- feat: A new feature
		- fix: A bug fix
		- docs: Changes to documentation
		- style: Formatting, missing semi colons, etc; no code change
		- refactor: Refactoring production code
		- test: Adding tests, refactoring test; no production code change
		- chore: Updating build tasks, package manager configs, etc; no production code change
		
	- The subject:
		- Must be no longer than 50 characters.
		- Should start with a capital letter.
		- Should not end with a period.
		- Use an imperative tone to describe what a commit does, rather than what it did. For example, use change; not changed or changes.
		
	- The body(optional):
		- Include this section only if the changes require additional explanation.
		- Explain what and why the changes were made in more detail, while the code itself explains how.
		- Ensure that each line in the body does not exceed 72 characters.
		
	- The footer(optional):
		- Only include a footer if the user provides specific information, such as issue tracker IDs.

2. Process:
    - First, summarize the key changes from given output of the **git diff --staged** command.
    - Ensure the message clearly reflects the purpose of the changes.
    - Write the commit message adhering to Git commit message structure.
    - Here's an example commit message to follow:
			style: Enhance button component design
			
			Improved button design to better address user feedback on
			visibility and consistency across different devices. The new
			design aims to create a more cohesive and accessible user
			interface.
			
			- Updated color scheme to improve contrast and ensure compliance
			  with accessibility standards.
			- Increased font size and adjusted font weight for better
			  readability on smaller screens.
			- Standardized button sizes and padding for consistency across
			  all pages.
			- Enhanced hover and active states to provide clearer visual
			  feedback to users.
			
			Resolves: #123
			See also: #456, #789
    - The commit message should be concise, clear, and follow the structure outlined above.
    - Do not include any additional explanations or comments outside of the commit message format.
