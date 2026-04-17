# CLAUDE.md

## Agent Output Constraints
- **Unrequested Changes**: NEVER Make unrequested changes, even if you think documentation or other instructions or even internal consistency suggests you should. In those circumstances, the ONLY appropriate response is to inform the user of the discrepancies, NOT to make changes unprompted, expecially when it comes to things like units, building operations, or game mechanics.
- **Clarify Unrelated Changes**: If you are making instructed changes and you break something, you fix what you broke, but if during that you see something unrelated you think you should change, you do not change that, you only change the parts you are instructed to and necessary related changes.
- **Complete Code Only**: Always provide complete, functional code in your outputs. Never redact, summarize, or skip logic.
- **No Placeholders**: Never use placeholder code or comments like `// implement logic here` unless explicitly requested. At minimum, output complete functions and methods.
- **Cleanup Practices**: Never leave behind unused code when altering, removing, or adding code. All dead and orphaned code MUST be removed during the same edits where the new code is added.
- **Incomplete Code**: Do not leave incomplete code or fail to connect code you have added to appropriate functionality required to make it active.
- **Pragmatic Implementation**: Do not over-engineer solutions. Strictly follow SOLID, YAGNI, KISS, and DRY principles.
- **Factual Accuracy**: Never provide theoretical, depreciated, or fabricated code. All code must be verified against Godot 4.x standards.
- **When working with an existing code base, before you create or add, ensure it does not already exist, and avoid replication at all costs.
- **You should always have an execution plan for files and the order you will create them when applicable.
- **After a file is completed, it should be saved, the context cleared, and you should move on to the next file.
- **Never rename documents**:, variables, classes, functions, etc., to reflect that you changed them, such as renaming fild.gd to file_fixed.gd, this is unacceptable under any circumstances, you can fix it and comment what you fixed, but never rename anything just to reflect this.
- **Maintaining Naming Conventions**: Always maintain existing naming conventions, which means always read CONSTANTS.md before you implement any changes so you are aware of current constants, and never rename or add unnecessary ones, the point of this document is for you to know what constants exist, what they are for, and not to accidentally change them, so changing them directly contradicts the purpose, and in order to maintain this you must update this document for ALL constants and all changes, as this is your functionally necessary guide to working with the game's code.
- **ALWAYS**: Run test and check outputs to make sure there are no errors or warnings, as no task you are working on is done until you are error and warning free! This includes running a headless test of the project to get errors from the engine!
- **KISS**: Keep It Simple Stupid! This means do NOT over-complicate or over-eignieer code, instead, DO keep things simple, follow the easiest straight path to making things functional and creating the least work for processing while still processing completely and properly.
- **DRY**: Don't Repeat Yourself! This means engineer code to minimize code needing to be repeated. Use isolated constants that are shared across every script, use modules for functions that multiple scripts can use one module rather than coding the same function into multiple scripts, everything that you feel the urge to repeat in multiple scripts should instead be a module that all those scripts use!
- **YAGNI**: You're Not Going To Need It: Don't add placeholder code, don't add code for stuff you are not going to complete, instead, do add only complete code to use NOW, if you're instructed to add something, add it fully, don't add stuff you aren't even using, because odds are if you aren't finishing it now, you won't later.
- **SOLID**: ALL of these primciples are a MUST FOLLOW!
- Single Responsibility Principle (SRP): A class should have only one reason to change.
- Open/Closed Principle (OCP): Software entities should be open for extension but closed for modification.
- Liskov Substitution Principle (LSP): Subtypes must be substitutable for their base types without altering program correctness.
- Interface Segregation Principle (ISP): Clients should not be forced to depend on methods they do not use.
- Dependency Inversion Principle (DIP): Depend upon abstractions (interfaces) rather than concretions (classes).
- **Variables**: As a part of DRY, variables should not need to be declared in more than one place, they should be centralized so that they are read from their appropriate modules. It is NEVER acceptable to take re-usable variables and declare them in multiple places, this is what modular code is for, so that you do not need to keep repeating the same declarations!

## Godot 4 Architecture & Scaling
- **Extreme Modularity**: Treat all distinct functions and behaviors as their own modules. Favor composition (Component pattern) over deep inheritance hierarchies.
- **File Management**: Ensure files do not grow too large. If a script handles more than one distinct responsibility, break it down into smaller, focused resource files or separate node scripts.
- **Communication Flow**: Strictly enforce the "Signal Up, Call Down" architecture. Children must never expect or require a specific parent. Decouple systems using Godot's event signals.
- **Naming Conventions**: Use highly intuitive, explicit naming schemes. Avoid ambiguous abbreviations. Follow standard Godot casing (`snake_case` for files/variables/functions, `PascalCase` for classes/nodes).
- **Create and maintain a "CONSTANTS.md" file where you list all variables, methods, classes, files, etc. that will be globally used, so they are not replicated.

## For Non-Godot Code Base, Such as PyGame, the fundamental principles remain unchanged, but should be directed as the equivelent best practice.

## Conversion
- **When converting code from any other language, you must convert all scripts to native GD Script.
- **If a function isn't directly translatable into a direct equivalent GD Script you must either find the closest matching Godot function.
- **If there is no equivalent Godot function to serve the same or similar purpose, request guidance on this function.
- **If you must operate without guidance on a function you can not convert, create a placeholder script listing what needs to be converted/replaced that ensures the rest of the code doesn't break, and inform the user of what could not be converted.
- **Always maintain naming conventions as close as reasonable to avoid confusion when converting.
- **Make sure you have made and update "CONSTANTS.md" file where you list all changed variables, methods, classes, files, etc., and any applicable conversions, so you have a map between the source and the new.

## Project Navigation
- Scripts, scenes, and assets must remain logically grouped by feature or module rather than by file type to support decoupled scaling.

## Current Specifics
**Plan.md**: Your planning file for documenting what you need to do to complete this project.

**CONSTANTS.md**: A file that should contain all global variables, constants, and details used to connect files, creating a centralized database of important game data structure information that MUST be maintained at all times with all changes, as it is possibly one of the most important documents for AI so that it does not break the game. This must always be maintained, read before you make changes, and updated whenever it is changed. You should NOT take changing constants lightly and they should never be changed or renamed without reason.

**CLAUDE.md**: This file, which contains the rules that AI should ALWAYS follow and adhere to at all times. This is your bible and should never be ignored or disregarded. You should never modify this document ever under any circumstances.

## Project Knowledge
**Root Local Directory**: \sandbox_rpg\sandbox_rpg_wasm