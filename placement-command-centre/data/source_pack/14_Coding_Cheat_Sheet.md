# Coding Cheat Sheet

Import this Markdown file into Notion as a page.


## Understand the problem
**Plain-English mental model:** Input → processing → output. Restate the task in one sentence.
**Questions to ask before coding:** What exactly comes in? What exactly must be returned? What are constraints?
**Tiny template / pseudocode:** Read input; normalize if needed; solve; output exactly as requested.
**Common bug:** Coding before understanding output format.
**Practice drill:** Explain 3 prompts aloud before coding.

## Dry run
**Plain-English mental model:** Act like the computer and track every variable.
**Questions to ask before coding:** What changes after each line? What is each variable now?
**Tiny template / pseudocode:** Write a table: step | variable values | condition | output.
**Common bug:** Guessing what code does.
**Practice drill:** Trace a loop with 3 values.

## Variables & types
**Plain-English mental model:** A named box holding a value; input may arrive as text.
**Questions to ask before coding:** Is this int, float, string, list or boolean?
**Tiny template / pseudocode:** x = int(input())  # Python example
**Common bug:** Using string input in numeric arithmetic.
**Practice drill:** Read two values and print sum/product.

## If / elif / else
**Plain-English mental model:** Choose one path based on a true/false condition.
**Questions to ask before coding:** Are boundaries inclusive? Can two branches both run?
**Tiny template / pseudocode:** if condition: ... elif other: ... else: ...
**Common bug:** < vs <=; incorrect and/or.
**Practice drill:** Test boundary values.

## For loop
**Plain-English mental model:** Repeat for a known sequence/range.
**Questions to ask before coding:** How many iterations? Is stop inclusive?
**Tiny template / pseudocode:** for i in range(n): ...
**Common bug:** Off-by-one; Python range(n) stops before n.
**Practice drill:** Print indices and values.

## While loop
**Plain-English mental model:** Repeat until a condition changes.
**Questions to ask before coding:** What makes the condition eventually false?
**Tiny template / pseudocode:** while condition: ...; update state
**Common bug:** Infinite loop from missing update.
**Practice drill:** Trace a countdown.

## Accumulator
**Plain-English mental model:** Keep a running answer: sum, count, product or best.
**Questions to ask before coding:** What should it start as? When is it updated?
**Tiny template / pseudocode:** total=0; for x in items: total += x
**Common bug:** Product starting at 0; max initialized to 0 when all values can be negative.
**Practice drill:** Sum/count/max/min.

## Function
**Plain-English mental model:** A named mini-program with inputs and a returned result.
**Questions to ask before coding:** What are parameters? What should be returned?
**Tiny template / pseudocode:** def solve(data): ...; return answer
**Common bug:** Printing when caller expects a return value.
**Practice drill:** Write and test 3 small functions.

## Array/list scan
**Plain-English mental model:** Visit each element once and update a result.
**Questions to ask before coding:** What if empty? One item? Duplicates? Negative values?
**Tiny template / pseudocode:** best = items[0]; for x in items[1:]: ...
**Common bug:** Assuming first value is positive; invalid index.
**Practice drill:** Max, min, search, count.

## Frequency map
**Plain-English mental model:** A dictionary counts or records things by key.
**Questions to ask before coding:** What is the key? What happens on repeats?
**Tiny template / pseudocode:** freq[x] = freq.get(x, 0) + 1
**Common bug:** Assuming key exists; wrong character normalization.
**Practice drill:** Character count / anagram.

## Two pointers
**Plain-English mental model:** Two positions move according to a rule.
**Questions to ask before coding:** What invariant stays true? Which pointer moves and why?
**Tiny template / pseudocode:** left=0; right=n-1; while left<right: ...
**Common bug:** Moving both pointers without justification.
**Practice drill:** Reverse array / palindrome.

## Sliding window
**Plain-English mental model:** Maintain a moving contiguous range instead of recomputing it.
**Questions to ask before coding:** What does the window represent? When should it expand/shrink?
**Tiny template / pseudocode:** right advances; while invalid: left advances; update answer.
**Common bug:** Updating answer before restoring valid window.
**Practice drill:** Fixed-size window sum then unique substring.

## Prefix sum
**Plain-English mental model:** Precompute cumulative totals to answer range-sum questions quickly.
**Questions to ask before coding:** What does prefix[i] mean? How do endpoints translate?
**Tiny template / pseudocode:** prefix[0]=0; prefix[i+1]=prefix[i]+a[i]
**Common bug:** Off-by-one range formula.
**Practice drill:** Range sum queries.

## Binary search
**Plain-English mental model:** Sorted input lets each comparison discard half the search space.
**Questions to ask before coding:** Is input sorted? How do low/high move? What if target absent?
**Tiny template / pseudocode:** while low<=high: mid=(low+high)//2; ...
**Common bug:** Wrong boundary update or infinite loop.
**Practice drill:** Find first/last/missing target.

## Sorting
**Plain-English mental model:** Reorder data to make comparisons easier.
**Questions to ask before coding:** Is original order important? Need stable sort?
**Tiny template / pseudocode:** Sort then scan / compare neighbours.
**Common bug:** Sorting when task requires original indices/order.
**Practice drill:** Duplicate detection / two-sum after sort.

## Recursion
**Plain-English mental model:** Solve a smaller version until a base case.
**Questions to ask before coding:** What is base case? Does input shrink every call?
**Tiny template / pseudocode:** if base: return ...; return solve(smaller)
**Common bug:** Missing base case; not shrinking.
**Practice drill:** Factorial, sum of list.

## Stack / queue
**Plain-English mental model:** Stack: last in first out. Queue: first in first out.
**Questions to ask before coding:** Which item is removed first? What operations are required?
**Tiny template / pseudocode:** stack.append(x); stack.pop(); queue append/popleft
**Common bug:** Using inefficient front-removal repeatedly from a list.
**Practice drill:** Balanced brackets / simple queue.

## Linked list
**Plain-English mental model:** Nodes connect through references, not adjacent indices.
**Questions to ask before coding:** What do prev/current/next point to? What if empty/head?
**Tiny template / pseudocode:** save next; redirect current.next; advance pointers
**Common bug:** Overwriting next before saving it.
**Practice drill:** Draw and reverse 3 nodes.

## Trees
**Plain-English mental model:** Recursive branching structure; traversal defines visit order.
**Questions to ask before coding:** What is empty-tree behavior? What order is requested?
**Tiny template / pseudocode:** DFS: visit node and recurse left/right; BFS uses queue.
**Common bug:** Mixing traversal orders; wrong height definition.
**Practice drill:** Draw a 3-level tree.

## Time complexity
**Plain-English mental model:** How work grows as input size grows.
**Questions to ask before coding:** One loop? Nested loops? Halving? Sorting?
**Tiny template / pseudocode:** Single scan O(n); nested full scans O(n²); binary search O(log n).
**Common bug:** Calling every loop O(n) without counting nesting.
**Practice drill:** Classify 10 snippets.

## Debugging
**Plain-English mental model:** Make a small failure reproducible, isolate it, fix one cause, retest.
**Questions to ask before coding:** Expected vs actual? Smallest failing input? Which line first diverges?
**Tiny template / pseudocode:** Reproduce → inspect → hypothesize → change one thing → retest.
**Common bug:** Changing many things at once.
**Practice drill:** Keep a bug journal.

## Test cases
**Plain-English mental model:** Normal, boundary, duplicate, empty/invalid and large cases.
**Questions to ask before coding:** What is the smallest input? Is there no solution? Are values tied?
**Tiny template / pseudocode:** Test expected output against actual output.
**Common bug:** Only testing the sample.
**Practice drill:** Write 5 tests per problem.

## Interview explanation
**Plain-English mental model:** Communicate approach, correctness, complexity and trade-offs.
**Questions to ask before coding:** Why does it work? Can I improve it? What assumptions did I make?
**Tiny template / pseudocode:** Clarify → brute force → optimize → code → test → complexity.
**Common bug:** Memorizing code but not reasoning.
**Practice drill:** Explain one solution in 60 seconds.
