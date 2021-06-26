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
# The log file
log_file = output_file.replace('.txt', '_log.txt')
# competence function to be used
comp_cmd = int(sys.argv[3]) if len(sys.argv) >= 4 else 8
# num of chromes per generation
num_chrom = int(sys.argv[4]) if len(sys.argv) >= 5 else 100
# Number of machines
num_machines = 0
# Number of maximum types
num_types = 5
# Original copy
orig_jobs = []

num_jobs = 0

log = ''

out = ''

num_gen = 1


prop_mutation = 0.02

max_sum = 0

print_freq = 20

MAX_GEN = 5000

def get_id():
  global num_jobs
  num_jobs += 1
  return num_jobs

class Job:
  def __init__(self, proc_time, _type, is_new=False):
    if is_new:
      self.ind = get_id()
    self.proc_time = proc_time
    self.t = 1 # NOTE: for the genetic algorithm, we ditch the types constraint!
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

def print_chrom(chrom):
  return format_list([x+1 for x in chrom])

def print_chrom_comp(chrom):
  return ''.join([str(x+1) for x in chrom])

def print_generation_comp(generation, competence):
  return '\n'.join([('OFV: %d, competence: %r\t' % (chrom_to_sol(x).finishing_time() ,competence[ind])) + print_chrom_comp(x) for ind, x in enumerate(generation)])

def return_stat(generation, competence, format='compact'):
  stat_log = ''
  if format == 'compact':
    _, best_val, best_index = get_best_sol(generation)
    stat_log += 'Best chromosome in current generation:\nOFV: %d, competence: %r\t%s\n' % (best_val, competence[best_index], print_chrom_comp(generation[best_index]))
    stat_log += 'Number of unique chromosomes (out of %d chromosomes in total): %d\n' % (num_chrom, len(set([print_chrom(x) for x in generation])))
  else:
    _, best_val, best_index = get_best_sol(generation)
    stat_log += 'Best chromosome in current generation with value: %d, competence: %r:\n%s\n' % \
    (best_val, competence[best_index], print_chrom_comp(generation[best_index]))
    stat_log += 'Number of unique chromosomes (out of %d chromosomes in total): %d\n' % (num_chrom, len(set([print_chrom(x) for x in generation])))
    stat_log += 'Entire generation:\n'
    stat_log += print_generation_comp(generation, competence) + '\n'

  return stat_log

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
  changed_val = random.choice(range(1, num_machines))

  mutated_chrom[changed_index] = (mutated_chrom[changed_index] + changed_val) % num_machines # Do machines start with 0 or 1?
  
  return mutated_chrom

def reproduce(current_generation, competence):
  '''
  return a new chromosome as a result of merging two chromosomes.
  '''
  parent_index_1 = random.choices(range(num_chrom), weights=competence)[0]
  parent_index_2 = random.choices(range(num_chrom), weights=competence)[0]
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
  for _ in range(round(num_chrom*prop_mutation)):
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
  Y = chrom_to_sol(chrom).finishing_time()
  X = max_sum / num_machines
  # Option A:
  #comp = max_sum - x
  return {
    1 : 1/Y,
    2 : 1/(Y**2),
    3 : 1/(Y)**0.5,
    4 : 1/Y**3,
    5 : 1/(2*Y-X),
    6 : 1/(Y-X+1),
    7 : 1/(3*Y-2*X),
    8 : 1/(Y-X+1)**2,
    9 : 1/(Y-X+1)**3,
    10 : 1/(Y-X+1)**0.5,
    11 : max([2*X-Y+1, 1]),
  }.get(comp_cmd, 1)

def get_best_sol(generation):
  '''
  Obtains the best solution in the given generation
  '''
  sols = [chrom_to_sol(chrom) for chrom in generation]
  best_val, best_index = min([(j, i) for i, j in enumerate([sol.finishing_time() for sol in sols])])

  return sols[best_index], best_val, best_index

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
  global log, max_sum, num_gen, out
  max_sum = sum([j.proc_time for j in jobs])
  try:
    current_generation = create_init_generation(jobs)
    best_sol, best_time, _ = get_best_sol(current_generation)
    lp = global_lower_bound(jobs)
    log += '**********************************************************************'*3 + '\n'
    log += 'printing Initial generation:\n'
    log += return_stat(current_generation, [calc_competence(x) for x in current_generation], format='full')
    out += '**********************************************************************'*3 + '\n'
    out += 'printing Initial generation:\n'
    out += return_stat(current_generation, [calc_competence(x) for x in current_generation], format='compact')
    while best_time > lp and num_gen < MAX_GEN:
      to_print = not(num_gen % print_freq)
      new_best = False

      print('Creating a new generation')
      competence = [calc_competence(x) for x in current_generation]
      current_generation = create_next_generation(current_generation, competence)
      best_sol_in_gen, best_time_in_gen, _ = get_best_sol(current_generation)
      if best_time_in_gen < best_time:
        new_best = True
        best_time = best_time_in_gen
        best_sol = best_sol_in_gen
        print('Found a better solution with finishing time %d:' % best_time)
        print(best_sol)
      if to_print or new_best:
        if new_best:
          out += '**********************************************************************'*3 + '\n'
          out += 'New best solution found in generation: %d\n' % num_gen
          out += return_stat(current_generation, competence, format='compact')
        log += '**********************************************************************'*3 + '\n'
        log += 'Printing generation: %d\n' % num_gen
        log += return_stat(current_generation, competence, format='full')

      num_gen = num_gen + 1 if best_time > lp else num_gen 


    return best_sol

  except KeyboardInterrupt:
    out += '\n\nProcess was terminated upon Keyboard interrupt, here is the latest solution:\n'
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
  global out
  output = ''
  if not sol:
    output = 'There is no solution for such input!'
    return output

  output += 'The problem had %d jobs that needed to be scheduled on %d machines.\n' % (num_jobs, num_machines)
  output += out
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
  out_file = open(output_file, 'w', encoding="utf8")
  out_file.write(output)
  out_file.close()

  log_file = open(log_file, 'w', encoding="utf8")
  log_file.write(log)
  log_file.close()
