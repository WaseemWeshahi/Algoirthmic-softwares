The algorithm behind the attached program works the following:

We maintain a stack, that we initially insert a node corresponding to the solution where the first job is assigned to the first machine.

At every iteration, we pop an element from the stack, and we "handle the node", when after we handle it, we get two "flags" that indicate
whether we should update the current best solution (which starts as a solution with infinite time) and whether should we terminate this node
or cut it off, in case we decide we want to check the node's children, then we create "m" new nodes, each assigning the node's next unassigned job to another machine and add the children to the stack.

The way we handle a node is as follows:

- Calculate upper bound (returns a possible solution as well)

- Calculate lower bound.

* mark upper bound as U, lower bound as L, and current best time as V.

	1. if L>=V, we should cut this node off, no need to update best solution, we return.
	2. if U<V, we mark that we should update (we do not return yet)
	3. if U==V, then we should cut this node off, and return. (if we've marked that we should update the current solution, we do just that and return)
	4. else, we do not cut the node off and we return whatever we marked in terms of should we update the best solution or not.

We calculate the lower bound rather simply, we take the maximum between jobs' process times, sum of those times divided (Cieled) by num of machines, and the machines times on the partial solution of the node.

Upper bound is calculated as follows:
	We move over unassigned jobs (longer to shorter) and for each job, we move over the machines in ascending order according to their finishing times, and we assign the job to the first machine that we can assign it to, as in, it does not conflict with the types constraint.
	We can however reach a state of a "deadlock", so if we finish this LPT approach and there are still unassigned jobs, then we "undo" the assignments that we've just performed, and then for each unassigned job, we assign them to the first machine (again, ascending in finishing times) that already contains its type, if none is found, we assign it to the machine that assigning the job to it does not conflict with the types constraint.
	If after all this we reach a deadlock, we assign all the unassigned jobs to arbitrary machine, and we return the solution and mark its finishing time as "infinity".


* We sort the jobs in descending fashion in respect to their process times when we first get the jobs and before activating the algorithm.
