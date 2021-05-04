The algorithm behind the attached program works the following:

Initial solution: We send every job of type _t to the machine _t%m (modulo)

At every iteration, we look for a better (not necessarily best!) neighbour, then we view it as our main solution,
and we keep looking for better and better neighbours until we either reach the lower bound** or when we stop finding "better" neighbours.

The way we look for a neighbour* is as follows:

	1. We run over each job, and try to move it to every possible machine.

	2. We run over each pair of jobs, and try to move them to every possible pair of machines (m^2 possibilities).

	3. We run over each triplet of jobs, and try to move them to every possible triplet of machines.

	4. We run over every pair of (type, machine) pair (so we have ((t1,m1),(t2,m2)) ), and decide to send each job with the attributes (type, machine)
	   to another specific machine.

The moment we find a "better" solution, we return it.

The way we determine if a solution is "better" or not, is by looking at the maximum value of finishing times but only on the machines involved in the swithcing.

* We only consider "valid neighbours", as in, solutions that do not have more than 3 different distinct types.

** We can change this condition so that we keep looking for new placements and neighbours until we get a more balanced solution,
   but it is costly so it was only applied for smaller inputs.