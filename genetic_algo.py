import sys
import os
import random
import math
import time
from numpy import argsort
# "Main" is found at end of file..
# The input file name
input_file = sys.argv[1]
# The output file
output_file = sys.argv[2]
# Number of machines
num_machines = 0
# Number of maximum types
num_types = 5
# Original copy
orig_jobs = []

num_jobs = 0

log = ''

num_gen = 1

num_chrom = 100

prop_mutation = 0.02

max_sum = 0

def get_id():
  global num_jobs
  num_jobs += 1
  return num_jobs

class Job:
  def __init__(self, proc_time, _type, is_new=False):
    if is_new:
      self.ind = get_id()
    self.proc_time = proc_time
    self.t = 1 # NOTE: for the genetic algorithm, we ditvh the types constraint!
    self.mach = '?'

  def __repr__(self):
    return 'J%d(%d, %d, %r)' % (self.ind, self.proc_time, self.t, self.mach+1 if type(self.mach) is int else self.mach)

  def __str__(self):
    return 'J%d(%d, %d)' % (self.ind, self.proc_time, self.t)

  def __lt__(self, other):
    ''' Needed  for sorting the jobs
    '''
    if self.t < other.t:
      return True
    if self.t > other.t:
      return False

    return self.proc_time < other.proc_time

  def __eq__(self, other):
    return self.ind == other.ind

  def __len__(self):
    return self.proc_time

  def __copy__(self):
    newone = Job(self.proc_time, self.t)
    newone.__dict__.update(self.__dict__)
    return newone

def deep_copy_job_list(job_list):
  return [x.__copy__() for x in job_list]

class Solution:
  def __init__(self, jobs):
    self.machines = [[] for i in range(num_machines)]
    if not jobs:
      self.machine_sums = [0]*num_machines
      self.machine_types = [set()]*num_machines
      return

    for j in jobs:
      if j.mach == '?':
        continue
      self.machines[j.mach].append(j)

    self.machine_sums = [sum([j.proc_time for j in m]) for m in self.machines]
    self.machine_types = [set([j.t for j in m]) for m in self.machines]

  def is_valid(self):
    '''
    for i in range(num_machines):
      if len(self.machine_types[i]) > 3:
        return False
    '''
    return True

  def finishing_times(self):
    return self.machine_sums

  def finishing_time(self):
    return max(self.finishing_times())

  def machine_types(self):
    return self.machine_types

  def __repr__(self):
    return '\n'.join(['m%d : %s' % (ind+1, sorted(jobs_list)) for ind, jobs_list in enumerate(self.machines)])

  def __str__(self):
    return '\n'.join(['m%d : %s \t sum: %d, types: %s' % (ind+1, format_list(sorted(jobs_list)), self.machine_sums[ind], format_list(self.machine_types[ind])) for ind, jobs_list in enumerate(self.machines)])

def format_list(list):
  return ', '.join([str(x) for x in list])

def global_lower_bound(jobs):
  proc_times = [j.proc_time for j in jobs]
  return max(proc_times + [math.ceil(max_sum/num_machines)])

def job_len(tup):
  return len(tup[1])

def return_stat(generation):
  #TODO
  pass
def mutate(current_generation, competence):
  '''
  Perform mutations
  '''
  try:
    mutated_index = random.choices(range(num_chrom), weights=competence)[0]
  except ValueError:
    import pdb;pdb.set_trace()
  mutated_chrom = current_generation[mutated_index]

  # Replacement or??
  changed_index = random.choice(range(num_jobs))
  changed_val = random.choice(range(1, num_jobs))

  mutated_chrom[changed_index] = (mutated_chrom[changed_index] + changed_val) % num_machines # Do machines start with 0 or 1?
  
  return mutated_chrom

def reproduce(current_generation, competence):
  '''
  return a new chromosome as a result of merging two chromosomes.
  '''
  parent_index_1, parent_index_2 = random.choices(range(num_chrom), weights=competence, k=2)
  parent1 = current_generation[parent_index_1]
  parent2 = current_generation[parent_index_2]

  cutoff_index = random.choice(range(num_jobs+1)) # Maybe lose the +1

  new_chrom1 = parent1[:cutoff_index] + parent2[cutoff_index:]
  new_chrom2 = parent2[:cutoff_index] + parent1[cutoff_index:]

  return new_chrom1, new_chrom2

def chrom_is_valid(chrom):
  '''
  Return true if the solution this chromosome is representing is valid
  '''
  return True

def create_next_generation(current_generation, competence):
  new_generation = []

  # Pass mutations
  new_generation.append(mutate(current_generation, competence))
  new_generation.append(mutate(current_generation, competence))

  while len(new_generation) < num_chrom:
    new_chrom1, new_chrom2 = reproduce(current_generation, competence)
    new_generation.append(new_chrom1)
    new_generation.append(new_chrom2)

  return new_generation[:num_chrom]

def chrom_to_sol(chrom):
  jobs = deep_copy_job_list(orig_jobs)
  for i in range(num_jobs):
    jobs[i].mach = chrom[i]

  return Solution(jobs)

def assignment_to_chrom(assignment):
  return [x.mach for x in assignment]

def calc_competence(chrom):
  '''
  return the competence value of a given chromosome.
  '''
  x = chrom_to_sol(chrom).finishing_time()
  # Option A:
  comp = max_sum - x
  # Option B:
  # comp = 1 / (x**2)
  return comp

def get_best_sol(generation):
  '''
  Obtains the best solution in the given generation
  '''
  sols = [chrom_to_sol(chrom) for chrom in generation]
  best_index, best_val = min([(i, j) for i, j in enumerate([sol.finishing_time() for sol in sols])])

  return sols[best_index], best_val

def create_LPT_chrom(jobs):
  '''
  Give an upper bound given jobs that may be partially assigned
  '''
  for i in range(num_jobs):
    jobs[i].mach = '?'
  possible_assignment = deep_copy_job_list(jobs)
  alt_assignment = deep_copy_job_list(possible_assignment)
  partial_solution = Solution(possible_assignment)
  mach_meta_data = list(zip(partial_solution.finishing_times(), partial_solution.machine_types))

  mach_dict = dict(zip(range(num_machines), mach_meta_data))

  #unassigned_jobs = sorted([(ind,j) for ind,j in enumerate(jobs) if j.mach == '?'], key=lambda x: len(x[1]), reverse=True)
  unassigned_jobs = [(ind,j) for ind,j in enumerate(jobs) if j.mach == '?']
  for (ind, j) in unassigned_jobs:
    mach_dict = dict(sorted(mach_dict.items(), key=lambda x: x[1][0]))
    for m in mach_dict:
      if len(set([j.t]) | mach_dict[m][1]) <=3:
        possible_assignment[ind].mach = m
        mach_dict[m] = (mach_dict[m][0] + j.proc_time, mach_dict[m][1] | set([j.t])) # finishing time, types
        break

  # If LPT fails..
  # LPT Never fails now!
  '''
  if not all([j.mach != '?' for j in possible_assignment]):
    mach_meta_data = list(zip(partial_solution.finishing_times(), partial_solution.machine_types))
    mach_dict = dict(zip(range(num_machines), mach_meta_data))
    for (ind, j) in unassigned_jobs:
      for m in range(num_machines):
        if j.t in mach_dict[m][1]: # Wherever is available.
          alt_assignment[ind].mach = m
          mach_dict[m] = (mach_dict[m][0] + j.proc_time, mach_dict[m][1] | set([j.t])) # finishing time, types
          break
      for m in range(num_machines):
        if len(set([j.t]) | mach_dict[m][1]) <=3: # Wherever is valid.
          alt_assignment[ind].mach = m
          mach_dict[m] = (mach_dict[m][0] + j.proc_time, mach_dict[m][1] | set([j.t])) # finishing time, types
          break
    possible_assignment = deep_copy_job_list(alt_assignment)

  if not all([j.mach != '?' for j in possible_assignment]):
    for ind, j in enumerate(possible_assignment):
      if j.mach == '?':
        possible_assignment[ind].mach = 0
  '''
  return assignment_to_chrom(possible_assignment)

def create_naive_chrom(jobs):
  chrom = [i % num_machines for i in range(len(jobs))]
  return chrom

def create_random_chrom(jobs):
  chrom = [random.randrange(num_machines) for x in jobs]
  return chrom

def create_a_chrom(jobs, opcode):
  '''
  produce a chromosome using the method specified in opcode
  '''
  if opcode == "naive":
    chrom = create_naive_chrom(jobs)
  if opcode == "random":
    chrom = create_random_chrom(jobs)
  if opcode == "lpt":
    chrom = create_LPT_chrom(jobs)
  return chrom

def create_init_generation(jobs):
  '''
  produce the first generation
  '''
  first_gen = []

  first_gen.append(create_a_chrom(jobs, "naive"))
  first_gen.append(create_a_chrom(jobs, "lpt"))
  while len(first_gen) < num_chrom:
    chrom = create_a_chrom(jobs, "random")
    first_gen.append(chrom)

  return first_gen


def genetic_algorithm(jobs):
  '''
  peform a genetic algorithm approach to find the optimal solution.
  '''
  assert jobs, 'No jobs to be scheduled..'
  global log, max_sum, num_gen
  max_sum = sum([j.proc_time for j in jobs])
  try:
    current_generation = create_init_generation(jobs)
    best_sol, best_time = get_best_sol(current_generation)
    lp = global_lower_bound(jobs)
    while best_time > lp:
      print('Creating a new generation')
      competence = [calc_competence(x) for x in current_generation]
      current_generation = create_next_generation(current_generation, competence)
      best_sol_in_gen, best_time_in_gen = get_best_sol(current_generation)
      num_gen += 1
      if best_time_in_gen < best_time:
        best_time = best_time_in_gen
        best_sol = best_sol_in_gen
        print('Found a better solution with finishing time %d:' % best_time)
        print(best_sol)

    return best_sol

  except KeyboardInterrupt:
    log += '\n\nProcess was terminated upon Keyboard interrupt, here is the latest solution:\n'
    return best_sol

def handle_file(filepath):
  '''
  Gets a path for an input file, in which the first line should specify the number of machines,
  and each line is a tuple (processing time, type)
  '''
  def assert_inputs(data):
    assert len(data) == 2, 'Invalid job syntax: %r' % data
    assert data[1] <= 5, 'Types are ranged from 1 to 5! you gave %d' % data[1]
    assert data[0] > 0, 'Processing times should be nonzero! you gave %d' % data[0]

  file = open(filepath, encoding="utf8")
  file_lines = [line.strip() for line in file.readlines() if not line.startswith('#')]

  global num_machines
  num_machines = int(file_lines[0])
  assert num_machines >=2, 'Number of machines should be m>=2'

  current_jobs = []
  for line in file_lines[1:]:
    data = [int(x.strip()) for x in line.split(',')]
    assert_inputs(data)
    current_jobs.append(Job(data[0], data[1], is_new=True))

  return current_jobs

def output_solution(sol, tiempo):
  '''
  Output the solution to the specified file
  '''
  global log
  output = ''
  if not sol:
    output = 'There is no solution for such input!'
    return output

  output += 'The problem had %d jobs that needed to be scheduled on %d machines.\n' % (num_jobs, num_machines)
  output += log
  output += '-----------------------------------------\n'
  output += 'Overall number of generations created: %d\n' % num_gen
  output += 'Number of seconds elapsed: %.3f\n' % tiempo
  output += 'The final solution:\n'
  output += '%s' % sol
  output += '\n'
  output += '\nObjective function\'s value: max{%s} = %d\n' % (format_list(sol.finishing_times()), sol.finishing_time())
  output += '*Lower bound (not necessarily tight): %d\n' % global_lower_bound(orig_jobs)
  output += '\n'
  output += '**output format:\n\tm_k is the k\'th machine.\n\tJ_i(P, T, M) is the i\'th job with processing time P, of type T, and is assigned to machine M (marked as \'?\' when unassigned).'

  return output

if __name__ == '__main__':
  orig_jobs = handle_file(input_file)
  jobs = deep_copy_job_list(orig_jobs)

  start = time.time()
  #jobs = sorted(jobs, key=lambda x: x.proc_time, reverse=True)
  sol = genetic_algorithm(jobs)
  print("%d seconds elapsed" % (time.time()-start))
  output = output_solution(sol, time.time()-start)
  out = open(output_file, 'w', encoding="utf8")
  out.write(output)
  out.close()
