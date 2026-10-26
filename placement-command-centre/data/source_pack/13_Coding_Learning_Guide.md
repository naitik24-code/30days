# Coding Learning Guide

Import this Markdown file into Notion as a page.


## Problem reading
**Simple explanation / tip:** Read the prompt twice. Rewrite it as: input → task → output. Circle constraints and keywords.
**Ask yourself these questions:** What exactly is given? What must I return/print? Is indexing 0-based?
**Common mistake to avoid:** Coding before understanding the output format.
**Practice method:** Explain the problem aloud in one sentence before coding.

## Examples first
**Simple explanation / tip:** Manually solve one normal example and one edge case before writing code.
**Ask yourself these questions:** What happens for 0, 1 item, duplicates, negative numbers or empty input?
**Common mistake to avoid:** Testing only the sample example.
**Practice method:** Make a tiny table of input, steps and output.

## Variables and types
**Simple explanation / tip:** A variable stores a value; the type controls which operations make sense.
**Ask yourself these questions:** What is the value after each line? Is input text or numeric?
**Common mistake to avoid:** Forgetting to convert input strings to integers/floats.
**Practice method:** Predict the value before running the program.

## Conditions
**Simple explanation / tip:** Use if/elif/else for decisions; combine conditions carefully with and/or/not.
**Ask yourself these questions:** Are the conditions mutually exclusive? What if values are equal?
**Common mistake to avoid:** Wrong boundary operators (< vs <=) and overlapping branches.
**Practice method:** Test just below, exactly at and just above each boundary.

## Loops
**Simple explanation / tip:** A loop repeats work. Know initialization, stopping condition and update.
**Ask yourself these questions:** Where does the loop start/end? Does it stop? How many iterations occur?
**Common mistake to avoid:** Off-by-one errors and infinite loops.
**Practice method:** Trace a loop with a 3-element input on paper.

## Accumulator patterns
**Simple explanation / tip:** Use a running total, count, product or best-so-far value.
**Ask yourself these questions:** What value should the accumulator start at? When is it updated?
**Common mistake to avoid:** Starting sum/product with the wrong identity (0 vs 1).
**Practice method:** Implement sum, count, max and factorial separately.

## Functions
**Simple explanation / tip:** A function names a reusable task. Parameters are inputs; return sends a result back.
**Ask yourself these questions:** What does the function receive and return? Is printing different from returning?
**Common mistake to avoid:** Printing inside a function when the caller needs a returned value.
**Practice method:** Write one function, test it with three inputs.

## Lists / arrays
**Simple explanation / tip:** A sequence stores multiple values. Indexing often begins at 0.
**Ask yourself these questions:** What is the first/last valid index? Can the list be empty?
**Common mistake to avoid:** Accessing index n in a list of length n.
**Practice method:** Trace indices and test one-element and duplicate arrays.

## Strings
**Simple explanation / tip:** Strings are sequences of characters. Normalize when the problem says ignore case/spaces.
**Ask yourself these questions:** Should spaces, punctuation or case matter? Are strings immutable in this language?
**Common mistake to avoid:** Comparing raw text when normalization is required.
**Practice method:** Try empty string, one character, repeated characters and spaces.

## Dictionaries / maps
**Simple explanation / tip:** Store a value under a key; useful for counts and fast membership checks.
**Ask yourself these questions:** What should be the key? What value changes when a key repeats?
**Common mistake to avoid:** Assuming a key exists before checking it.
**Practice method:** Build a character-frequency map by hand.

## Two pointers
**Simple explanation / tip:** Move two indices based on a clear condition, often from opposite ends.
**Ask yourself these questions:** What invariant should remain true as pointers move?
**Common mistake to avoid:** Moving the wrong pointer or skipping a valid pair.
**Practice method:** Draw pointer positions for every iteration.

## Binary search
**Simple explanation / tip:** Only use it on sorted data. Each step discards half the search range.
**Ask yourself these questions:** Why is the data sorted? How are low, high and mid updated?
**Common mistake to avoid:** Infinite loop from incorrect boundary updates.
**Practice method:** Trace target present, absent, first and last positions.

## Recursion
**Simple explanation / tip:** A function calls itself on a smaller problem and must have a base case.
**Ask yourself these questions:** What is the base case? Does every call move toward it?
**Common mistake to avoid:** Missing base case or not reducing the problem.
**Practice method:** Draw a call stack for factorial(4).

## Data structures
**Simple explanation / tip:** Stack = last in, first out; queue = first in, first out; linked list uses references/pointers.
**Ask yourself these questions:** Which operations are needed and what is their cost?
**Common mistake to avoid:** Memorizing names without understanding operations.
**Practice method:** Use cards/boxes to simulate push/pop and enqueue/dequeue.

## Complexity
**Simple explanation / tip:** Big-O describes how work grows as input grows, not exact seconds.
**Ask yourself these questions:** How many times does each loop run? Are loops nested?
**Common mistake to avoid:** Calling everything O(n) without counting operations.
**Practice method:** Compare one loop, nested loops and binary search.

## Debugging
**Simple explanation / tip:** Reproduce the bug, isolate the smallest failing case, inspect variables, fix and retest.
**Ask yourself these questions:** What exact input fails? What did I expect vs get?
**Common mistake to avoid:** Changing multiple things at once or not retesting.
**Practice method:** Keep a bug log with cause, fix and prevention.

## Test cases
**Simple explanation / tip:** Test normal, boundary, repeated, invalid and large inputs as appropriate.
**Ask yourself these questions:** What is the smallest input? What if no answer exists?
**Common mistake to avoid:** Only testing the happy path.
**Practice method:** For every solution, write at least 5 test cases.

## Interview explanation
**Simple explanation / tip:** State brute force, improve if needed, explain correctness, complexity and trade-offs.
**Ask yourself these questions:** Why does it work? What is time/space complexity?
**Common mistake to avoid:** Memorizing code without being able to defend it.
**Practice method:** Explain the solution in 60 seconds before coding.

## Daily learning rule
**Simple explanation / tip:** Try independently for 15–20 minutes, then request a hint, then study a solution and re-code from memory.
**Ask yourself these questions:** Can I reproduce it tomorrow without looking?
**Common mistake to avoid:** Copying a solution and marking it learned.
**Practice method:** Use statuses: Tried → Hint → Solved → Re-solved next day.

## Python-specific
**Simple explanation / tip:** Use input(), int()/float(), range(), len(), list, dict and clear function names.
**Ask yourself these questions:** What does range's stop value mean? Is the list modified in place?
**Common mistake to avoid:** Confusing = with ==, indentation errors and mutable side effects.
**Practice method:** Predict output and run small snippets.

## Java/C++ note
**Simple explanation / tip:** If using Java/C++, map the same logic to types, loops, methods/functions and collections; practise the chosen language consistently.
**Ask yourself these questions:** What are input/output syntax, array bounds and collection operations in my language?
**Common mistake to avoid:** Switching languages during the same learning block.
**Practice method:** Choose one main interview language for the month.
