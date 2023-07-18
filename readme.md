## Optimization algorithm implementation
### Problem description
#### [Problem Number 5](/problems_4_projects_2021.pdf)

Scheduling with types to minimize the makespan.
Input: An integer number of (identical) machines m ≥ 2. A set of n jobs J =
{1, 2, . . . , n}, where every job j has an integer processing time p_j > 0 and a positive
integer type t_j ∈ {1, 2, 3, . . . , 7}.
Goal: Find a partition of the jobs of to the machines, J_1, J_2, . . . , J_m, such that every
subset has jobs of at most three types (for any i there are three values k_i_1
, k_i_2
, k_i_3 ∈
{1, 2, 3, . . . , 7}, such that if j ∈ J_i
, then t_j ∈ {k_i_1
, k_i_2
, k_i_3
}).
Objective: Minimize max_{1≤i≤m} \sum{j∈J_i} p_j


The algorithm behind the attached program works the following:

For the initial generation we use LPT and a "simple" method (J_i goes to i%m machine) to create first chromosomes, and generate the rest of the population randomly.

At every iteration, we calculate the competence of the generation we have in hand, then we create the next generation as follows:

- We choose round(probabilty_mutation * #of_chromosmes) chromsomes randomly (weighted according to competence, with repition) and perform mutations on them and
  send them to the next generation, the way we do mutations is by choosing a random job/index in the chromosome and change to which machine it is assigned to.
- We then keep choosing two chromsomes (weighted, with repition) and performing a crossover between them at a random index and sending their children to the next generation, until
  reaching the required number of chromsomes.

We also check the best solution at each generation and save it if it's better than the solution we already have saved.

Generations are made until we reach the lower bound or exceed the number of allowed generations.

#of_chromosomes: 150
Competence functions that led to the best results:
- 1/(Y-X+1)^2
- max{2*X-Y+1,1}
  where X is the objective function's value and Y is the sum of all jobs' process times divided by number of machines
  
probability of mutation: 0.02

* For this algorithm, we ditched the "types" constraint.

Other variations:
I've tried using 72, 100 and 128 chromosomes and it seemed that the more the chromosomes the better (as long as it didnt take too long to process each generation)
So I ended up using 150 chromosomes.

With the competence function 1/(Y-X+1)^2, we notice that it converges rather rapidly while reaching a good solution, while the function max{2*X-Y+1,1} converges at a steady rate
but sadly does not reach better results, other competence functions had the same case, they either converge quickly to an acceptable solution, or converge "correctly" at a less
impressive solution.



