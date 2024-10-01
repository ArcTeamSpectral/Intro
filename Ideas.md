

Compression based schemes:

LZ78-based schemes work by entering phrases into a *dictionary* and then, when a repeat occurrence of that particular phrase is found, outputting the dictionary index instead of the phrase.

We can use this idea to build a DSL.


Inspired by M.Hodel's work on creating the Arc DSL.
First, he constructed some basic notions. Then, he tried to solve ARC using the DSL.
Very similar to DreamCoder.
There's a "sleep" phase of consolidation.

Another related idea is to have a "skill library" that converts inputs and outputs.
After seeing a certain input-output pair, the skill library adds a new skill to the DSL, or adds the trace to the library.
The generator will generate new problems, and the solver will try to solve them, adding to the skill library.

This way, when the agent is presented with a new problem, it can see if it matches any of the skills in the library. If not, 
it can solve it by ActiveLearning.


## Active Learning

When the agent is presented with a new problem that it can't immediately solve, it'll try to use a tree-based expansion.

1. From the current nodes, explore and find interesting information, and new states. Kind of like A* search, where it's guided
 by a heuristic about how close the solution is to the outcome.
2. At every node it'll ask itself: how do I reach the outcome from here? What is mismatched? What could be potential plan, and what information
 would I need to evaluate them?
3. When it finishes, it'll recognize that this was the solution. Develop more of an association between the right solutions, and 
 reduce the likelihood of the wrong solutions!
