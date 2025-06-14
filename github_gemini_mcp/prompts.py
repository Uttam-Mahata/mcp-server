from typing import List
from mcp.types import Prompt

def get_available_prompts() -> List[Prompt]:
    """Get all available MCP prompts"""
    
    return [
        Prompt(
            name="code_review_prompt",
            description="Comprehensive code review prompt with customizable focus areas",
            arguments=[
                {
                    "name": "context",
                    "description": "Additional context about the code or project",
                    "required": False
                },
                {
                    "name": "language",
                    "description": "Programming language being reviewed",
                    "required": False
                },
                {
                    "name": "level",
                    "description": "Review thoroughness level (quick/standard/thorough/exhaustive)",
                    "required": False
                },
                {
                    "name": "focus_areas",
                    "description": "Specific areas to focus on (security, performance, maintainability, etc.)",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="documentation_prompt",
            description="Intelligent documentation generation prompt for code and APIs",
            arguments=[
                {
                    "name": "format",
                    "description": "Documentation format (markdown, rst, html, plain)",
                    "required": False
                },
                {
                    "name": "audience",
                    "description": "Target audience (developers, users, contributors)",
                    "required": False
                },
                {
                    "name": "detail_level",
                    "description": "Level of detail (brief, standard, comprehensive)",
                    "required": False
                },
                {
                    "name": "include_examples",
                    "description": "Whether to include usage examples",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="architecture_analysis_prompt",
            description="Repository architecture and design pattern analysis prompt",
            arguments=[
                {
                    "name": "focus_areas",
                    "description": "Areas to focus on (scalability, maintainability, security, performance)",
                    "required": False
                },
                {
                    "name": "project_type",
                    "description": "Type of project (web app, library, microservice, etc.)",
                    "required": False
                },
                {
                    "name": "team_size",
                    "description": "Development team size for context",
                    "required": False
                },
                {
                    "name": "requirements",
                    "description": "Specific requirements or constraints",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="bug_analysis_prompt",
            description="Bug identification and root cause analysis prompt",
            arguments=[
                {
                    "name": "error_message",
                    "description": "Error message or symptom description",
                    "required": False
                },
                {
                    "name": "environment",
                    "description": "Environment where the bug occurs",
                    "required": False
                },
                {
                    "name": "steps_to_reproduce",
                    "description": "Steps to reproduce the issue",
                    "required": False
                },
                {
                    "name": "recent_changes",
                    "description": "Recent changes that might be related",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="optimization_prompt",
            description="Code and architecture optimization suggestions prompt",
            arguments=[
                {
                    "name": "performance_goals",
                    "description": "Specific performance goals or metrics",
                    "required": False
                },
                {
                    "name": "constraints",
                    "description": "Resource or technical constraints",
                    "required": False
                },
                {
                    "name": "current_bottlenecks",
                    "description": "Known performance bottlenecks",
                    "required": False
                },
                {
                    "name": "optimization_scope",
                    "description": "Scope of optimization (local/module/system-wide)",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="security_audit_prompt",
            description="Security vulnerability assessment and audit prompt",
            arguments=[
                {
                    "name": "security_level",
                    "description": "Required security level (basic/standard/high/critical)",
                    "required": False
                },
                {
                    "name": "compliance_requirements",
                    "description": "Compliance standards to check against",
                    "required": False
                },
                {
                    "name": "threat_model",
                    "description": "Specific threats or attack vectors to consider",
                    "required": False
                },
                {
                    "name": "data_sensitivity",
                    "description": "Sensitivity of data being processed",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="test_generation_prompt",
            description="Comprehensive test case generation prompt",
            arguments=[
                {
                    "name": "test_framework",
                    "description": "Testing framework to use",
                    "required": False
                },
                {
                    "name": "coverage_level",
                    "description": "Test coverage level (basic/standard/comprehensive)",
                    "required": False
                },
                {
                    "name": "test_types",
                    "description": "Types of tests to generate (unit/integration/e2e)",
                    "required": False
                },
                {
                    "name": "edge_cases",
                    "description": "Specific edge cases to test",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="refactoring_prompt",
            description="Code refactoring and improvement suggestions prompt",
            arguments=[
                {
                    "name": "refactoring_goals",
                    "description": "Goals for refactoring (readability, performance, maintainability)",
                    "required": False
                },
                {
                    "name": "constraints",
                    "description": "Constraints or limitations for refactoring",
                    "required": False
                },
                {
                    "name": "design_patterns",
                    "description": "Design patterns to apply or avoid",
                    "required": False
                },
                {
                    "name": "backward_compatibility",
                    "description": "Backward compatibility requirements",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="migration_planning_prompt",
            description="Technology migration and upgrade planning prompt",
            arguments=[
                {
                    "name": "source_technology",
                    "description": "Current technology stack",
                    "required": False
                },
                {
                    "name": "target_technology",
                    "description": "Target technology stack",
                    "required": False
                },
                {
                    "name": "migration_scope",
                    "description": "Scope of migration (partial/full/gradual)",
                    "required": False
                },
                {
                    "name": "timeline",
                    "description": "Available timeline for migration",
                    "required": False
                }
            ]
        ),
        
        Prompt(
            name="feature_analysis_prompt",
            description="New feature design and implementation analysis prompt",
            arguments=[
                {
                    "name": "feature_requirements",
                    "description": "Feature requirements and specifications",
                    "required": False
                },
                {
                    "name": "user_stories",
                    "description": "User stories or use cases",
                    "required": False
                },
                {
                    "name": "technical_constraints",
                    "description": "Technical constraints or limitations",
                    "required": False
                },
                {
                    "name": "integration_points",
                    "description": "System integration points",
                    "required": False
                }
            ]
        )
    ]
