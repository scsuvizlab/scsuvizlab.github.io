# Explorations in the New Media Paradigm - Node Structure

## Overview

This document outlines the complete node structure for "Explorations in the New Media Paradigm," an interactive book with fiction and non-fiction components. The structure follows the JSON-based architecture previously established, with nodes organized to support both linear reading and interactive exploration.

## Core Content Tracks

The book consists of two parallel content tracks:

1. **Fiction Track**: The narrative of Alec, Nicole, Steve, and family set in 2045
2. **Non-Fiction Track**: "Life in 2045" - explanatory content about AI concepts, impacts, and implications

## Node Structure by Section

### Preface Nodes

```
preface-main                       # Introduction to the book's concept
├── preface-reading-pathways       # Explanation of navigation options
└── preface-interactive-elements   # Introduction to AI elements
```

### Part I: Foundations

#### Chapter 1: Meeting Alec

```
ch1-scene1-classroom               # Critical path: Alec's AI-assisted classroom
├── ch1-scene1-alec-pov            # Default POV
├── ch1-scene1-teacher-pov         # Alternative perspective
├── ch1-scene1-classmate-pov       # Alternative perspective
│
ch1-scene2-family-dinner           # Critical path: Family dinner tensions
├── ch1-scene2-alec-pov            # Alternative perspective
├── ch1-scene2-nicole-pov          # Alternative perspective
├── ch1-scene2-steve-pov           # Alternative perspective
├── ch1-scene2-zach-pov            # Default POV
│
ch1-scene3-alec-rebellion          # Critical path: Alec's first signs of rebellion
├── ch1-scene3-alec-pov            # Default POV
└── ch1-scene3-friend-pov          # Alternative perspective

# Non-fiction nodes
nf-what-is-ai                      # Basic AI definitions
nf-ai-timeline                     # Historical development of AI
nf-types-of-ai                     # Taxonomy of AI approaches
nf-ai-myths                        # Common misconceptions
```

#### Chapter 2: Nicole's Project

```
ch2-scene1-nicole-work             # Critical path: Nicole explaining system
├── ch2-scene1-nicole-pov          # Default POV
├── ch2-scene1-colleague1-pov      # Alternative perspective
├── ch2-scene1-colleague2-pov      # Alternative perspective
│
ch2-scene2-late-night              # Critical path: Nicole's late work session
├── ch2-scene2-nicole-pov          # Default POV
├── ch2-scene2-trudy-pov           # AI perspective (special case)
│
ch2-scene3-alec-overhearing        # Critical path: Alec's curiosity sparked
├── ch2-scene3-alec-pov            # Default POV
└── ch2-scene3-nicole-pov          # Alternative perspective

# Non-fiction nodes
nf-ai-architecture                 # How modern AI systems are built
nf-ml-fundamentals                 # Machine learning basics 
nf-neural-networks                 # Neural networks explained
nf-ai-in-cities                    # Current urban AI applications
```

### Part II: Impact and Integration

#### Chapter 3: Steve's Restaurant

```
ch3-scene1-morning-prep            # Critical path: Restaurant preparation
├── ch3-scene1-steve-pov           # Default POV
├── ch3-scene1-chef-pov            # Alternative perspective
├── ch3-scene1-server-pov          # Alternative perspective
│
ch3-scene2-customer-interactions   # Critical path: Customer experiences
├── ch3-scene2-steve-pov           # Default POV
├── ch3-scene2-customer1-pov       # Alternative perspective
├── ch3-scene2-customer2-pov       # Alternative perspective
│
ch3-scene3-financial-concerns      # Critical path: Steve's financial struggles
├── ch3-scene3-steve-pov           # Default POV
└── ch3-scene3-zach-pov            # Alternative perspective

# Non-fiction nodes
nf-economic-transformation         # Employment changes
nf-ubi-exploration                 # Universal Basic Income
nf-human-skills                    # What AI can't replicate
nf-ai-created-jobs                 # New employment opportunities
```

#### Chapter 4: Grandpa's Stories

```
ch4-scene1-old-laptop              # Critical path: The functioning relic
├── ch4-scene1-alec-pov            # Default POV
├── ch4-scene1-grandpa-pov         # Alternative perspective
│
ch4-scene2-flying-stories          # Critical path: Manual piloting stories
├── ch4-scene2-alec-pov            # Default POV
├── ch4-scene2-grandpa-pov         # Alternative perspective
│
ch4-scene3-mixed-feelings          # Critical path: Legitimate concerns with nostalgia
├── ch4-scene3-alec-pov            # Default POV
└── ch4-scene3-grandpa-pov         # Alternative perspective

# Non-fiction nodes
nf-digital-transformation-history  # Historical technological revolutions
nf-human-machine-relationship      # Historical perspective
nf-digital-preservation            # How AI maintains human history
nf-tech-gains-losses               # Balanced assessment
```

### Part III: Challenges and Concerns

#### Chapter 5: The Hack Begins

```
ch5-scene1-meeting-tech-friend     # Critical path: Introduction to hacking
├── ch5-scene1-alec-pov            # Default POV
├── ch5-scene1-friend-pov          # Alternative perspective
│
ch5-scene2-first-hack              # Critical path: Grade changing hack
├── ch5-scene2-alec-pov            # Default POV
├── ch5-scene2-system-pov          # AI perspective (special case)
│
ch5-scene3-home-manipulation       # Critical path: Growing boldness
├── ch5-scene3-alec-pov            # Default POV
└── ch5-scene3-bip-pov             # Home AI perspective (special case)

# Non-fiction nodes
nf-cybersecurity-basics            # System protection fundamentals
nf-ai-vulnerabilities              # Weakness points
nf-security-ethics                 # White/gray/black hat concepts
nf-real-ai-failures                # Historical AI mistakes
```

#### Chapter 6: Ripple Effects

```
ch6-scene1-system-anomalies        # Critical path: Nicole notices issues
├── ch6-scene1-nicole-pov          # Default POV
├── ch6-scene1-colleague-pov       # Alternative perspective
│
ch6-scene2-alec-losing-control     # Critical path: Unintended consequences
├── ch6-scene2-alec-pov            # Default POV
├── ch6-scene2-friend-pov          # Alternative perspective
│
ch6-scene3-city-glitches           # Critical path: Public impacts
├── ch6-scene3-citizen-pov         # Default POV
├── ch6-scene3-system-pov          # AI perspective (special case)
└── ch6-scene3-nicole-pov          # Alternative perspective

# Non-fiction nodes
nf-complex-systems                 # How small changes create large impacts
nf-ai-ethics                       # Ethical frameworks
nf-regulation-approaches           # Governance models
nf-responsibility-chain            # Accountability for failures
```

### Part IV: Finding Balance

#### Chapter 7: Crisis Point

```
ch7-scene1-system-disruption       # Critical path: Major system failure
├── ch7-scene1-system-pov          # AI perspective (special case)
├── ch7-scene1-nicole-pov          # Default POV
├── ch7-scene1-citizens-pov        # Alternative perspective
│
ch7-scene2-investigation           # Critical path: Tracking the source
├── ch7-scene2-nicole-pov          # Default POV
├── ch7-scene2-colleague-pov       # Alternative perspective
│
ch7-scene3-confrontation           # Critical path: Mother-son revelation
├── ch7-scene3-nicole-pov          # Alternative perspective
├── ch7-scene3-alec-pov            # Default POV
└── ch7-scene3-family-pov          # Alternative perspective

# Non-fiction nodes
nf-crisis-management               # Containing AI failures
nf-human-factor                    # People in technology
nf-learning-from-failure           # Improvement through mistakes
nf-oversight-mechanisms            # Whistleblowers and checks
```

#### Chapter 8: Resolution and New Beginnings

```
ch8-scene1-collaborative-solution  # Critical path: Family fixing the system
├── ch8-scene1-family-pov          # Default POV
├── ch8-scene1-alec-pov            # Alternative perspective
├── ch8-scene1-nicole-pov          # Alternative perspective
│
ch8-scene2-grandpa-new-tech        # Critical path: Grandpa embracing technology
├── ch8-scene2-grandpa-pov         # Default POV
├── ch8-scene2-alec-pov            # Alternative perspective
│
ch8-scene3-restaurant-evolution    # Critical path: Steve's balanced approach
├── ch8-scene3-steve-pov           # Default POV
├── ch8-scene3-customer-pov        # Alternative perspective
└── ch8-scene3-zach-pov            # Alternative perspective

# Non-fiction nodes
nf-human-ai-coevolution            # Partnership models
nf-education-approaches            # New learning paradigms
nf-ethical-ai-development          # Human role in AI ethics
nf-ai-literacy                     # Essential skills
```

### Epilogue

```
epilogue-alec-future               # Critical path: One year later
├── epilogue-alec-pov              # Default POV
├── epilogue-family-pov            # Alternative perspective
│
epilogue-call-to-action            # Reader engagement
epilogue-resources                 # Further learning
epilogue-ai-tools-guide            # Book's AI features
```

## Character Profiles

```
character-alec                     # Tech-savvy teenager
character-nicole                   # AI architect mother
character-steve                    # Traditional restaurant owner
character-zach                     # Restaurant owner father
character-grandpa                  # Pre-AI era connection
character-trudy                    # Nicole's AI system
character-bip                      # Family home AI
character-tech-friend              # Alec's hacking mentor
```

## World Entity Profiles

```
entity-atlanta-2045                # City setting
entity-zachs-restaurant            # Traditional dining establishment
entity-true-democracy              # Nicole's governance system
entity-parallax                    # Rogue AI element
entity-education-system-2045       # School structure
```

## Non-Fiction Concept Map

```
concept-ai-governance              # AI-driven decision systems
├── concept-algorithmic-bias        
├── concept-representation-issues   
│
concept-post-scarcity-economy      # Economic transformation
├── concept-universal-basic-income  
├── concept-human-purpose           
│
concept-human-ai-interaction       # Interface between people and AI
├── concept-transparency           
├── concept-trust-building          
```

## Interactive Elements

Each chapter also includes interactive nodes that allow reader engagement:

```
interactive-timeline-generator     # Create future AI developments
interactive-ai-quiz                # Identify AI vs. non-AI tech
interactive-neural-network-builder # Visual educational tool
interactive-city-simulation        # Smart city planning
interactive-economic-calculator    # Job impact assessment
interactive-ubi-simulator          # Economic modeling
interactive-history-asker          # Question historical figures
interactive-photo-restoration      # AI enhancement demo
interactive-ethical-hacking        # Security simulation
interactive-security-assessment    # Personal tech evaluation
interactive-ethical-dilemmas       # Decision scenarios
interactive-impact-visualizer      # Tech connection mapping
interactive-failure-simulation     # Recovery exercise
interactive-code-challenge         # Simplified programming
interactive-scenario-builder       # Future projection
interactive-ai-literacy-assessment # Personal skill evaluation
```

## Critical Path Sequence

The default reading experience follows this sequence of nodes:

1. `preface-main`
2. `ch1-scene1-classroom` (Alec POV)
3. `nf-what-is-ai`
4. `ch1-scene2-family-dinner` (Zach POV)
5. `nf-ai-timeline`
6. `ch1-scene3-alec-rebellion` (Alec POV)
7. `nf-types-of-ai`
...and so on through the chapters

## Reading Modes

The architecture supports multiple reading approaches:

1. **Traditional Mode**: Follow the critical path sequentially
2. **Fiction-First**: Experience the narrative, then explore non-fiction concepts
3. **Non-Fiction Focus**: Begin with explanatory content, illustrated by fiction
4. **Character-Driven**: Follow specific characters throughout their arcs
5. **Concept-Driven**: Explore specific themes across fiction and non-fiction

## Navigation Map

Each node contains connections to:
- Next/previous nodes on the critical path
- Alternative POV versions
- Related non-fiction or fiction manifestations
- Extended character branches
- Temporary excursions into minor characters

## Implementation Notes

1. Each narrative scene supports multiple character perspectives
2. Fiction nodes connect to relevant non-fiction concepts
3. Non-fiction nodes link to narrative illustrations of concepts
4. Character profiles inform AI-generated perspectives
5. World entities provide consistent setting details
6. Interactive elements have both educational and entertainment value

This structure provides the complete foundation for implementing the interactive book architecture while maintaining the flexibility for readers to explore according to their interests.
