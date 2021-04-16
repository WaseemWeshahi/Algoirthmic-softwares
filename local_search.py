import sys
import os
import random
import math
# "Main" is found at end of file..
# The input file name
input_file = sys.argv[1]
# The output file
output_file = sys.argv[2]
# Number of machines
num_machines = 0
# Original copy
orig_jobs = []

num_jobs = 0

def get_id():
  global num_jobs
  num_jobs += 1
  return num_jobs

class Job:
  def __init__(self, proc_time, _type, is_new=False):
    if is_new:
      self.ind = get_id()
    self.proc_time = proc_time
    self.t = _type
    self.mach = 0

  def __repr__(self):
    return 'J%d(%d, %d, %d)' % (self.ind, self.proc_time, self.t, self.mach)

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

  def __copy__(self):
    newone = Job(self.proc_time, self.t)
    newone.__dict__.update(self.__dict__)
    return newone

def deep_copy_job_list(job_list):
  return [x.__copy__() for x in job_list]

class Solution:
  def __init__(self, jobs):
    self.machines = [[] for i in range(num_machines)]

    for j in jobs:
      self.machines[j.mach].append(j)

    self.machine_sums = [sum([j.proc_time for j in m]) for m in self.machines]
    self.machine_types = [set([j.t for j in m]) for m in self.machines]

  def is_valid(self):
    for m in self.machines:
      types_set = set([j.t for j in m])
      if len(types_set) > 3:
        return False
    return True

  def finishing_times(self):
    return [sum([j.proc_time for j in m]) for m in self.machines]

  def finishing_time(self):
    return max(self.finishing_times())

  def __repr__(self):
    return '\n'.join(['m%d : %s' % (ind+1, sorted(jobs_list)) for ind, jobs_list in enumerate(self.machines)])

  def __str__(self):
    return '\n'.join(['m%d : %s \t sum: %d, types: %s' % (ind+1, format_list(sorted(jobs_list)), self.machine_sums[ind], format_list(self.machine_types[ind])) for ind, jobs_list in enumerate(self.machines)])

def format_list(list):
  return ', '.join([str(x) for x in list])

def get_index(jobs, ind):
  for index, job in enumerate(jobs):
    if job.ind == ind:
      return index
  return -1

def lower_bound(jobs):
  proc_times = [j.proc_time for j in jobs]
  times_sum = sum(proc_times)
  return max(proc_times + [math.ceil(times_sum/num_machines)])

def create_naive_solution(jobs):
  '''
  produce a naive solution, which is assigning jobs with type t to machine t%m
  '''
  naive_assignment = deep_copy_job_list(jobs)
  for i, job in enumerate(jobs):
    naive_assignment[i].mach = job.t % num_machines

  return naive_assignment, Solution(naive_assignment)

def create_greedy_solution(jobs):
  '''
  DEPRECATED - No need to delve too much into finding a good initial solution.
  '''
  return None
  naive_assignment = deep_copy_job_list(jobs)
  #types_2_machines = {1 : 0, 2 : 0, 3 : 1, 4 : 1, 5 : 0}
  types_2_machines = {1 : 1, 2 : 2, 3 : 0, 4 : 1, 5 : 0}
  lengths = [sum([j.proc_time if j.t == _type else 0 for j in jobs]) for _type in [1, 2, 3, 4, 5]]
  types_2_lengths = dict(zip([1, 2, 3, 4, 5], lengths))
  #import pdb;pdb.set_trace()
  for i, job in enumerate(jobs):
    naive_assignment[i].mach = types_2_machines[job.t]

  return naive_assignment, Solution(naive_assignment)

def cart_squared(list):
  return [(i,j) for i in list for j in list]

def get_best_neighbour(assigned_jobs):
  '''
  not necessarily best!?
  '''
  best_assignment = deep_copy_job_list(assigned_jobs)
  best_time = Solution(assigned_jobs).finishing_time()
  print('finding best neighbour for the assignment:')
  print(Solution(assigned_jobs))

  # Replacements
  for i in range(len(assigned_jobs)):
    print('altering J%d' % (i+1))
    for machine_ind in range(num_machines):
      possible_assignment = deep_copy_job_list(best_assignment)
      orig_mach = possible_assignment[i].mach
      possible_assignment[i].mach = machine_ind
      possible_sol = Solution(possible_assignment)
      print('checking solution:')
      print(possible_sol)
      print('Value: %d, valid? %r' % (possible_sol.finishing_time(), possible_sol.is_valid()))

      #if possible_sol.is_valid() and (max(possible_sol.machines[orig_mach], possible_sol.machines[machine_ind]) \
      # < max(Solution(best_assignment).machines[orig_mach], Solution(best_assignment).machines[machine_ind])):
      if possible_sol.is_valid() and possible_sol.finishing_time() < best_time:
        print('found better solution with %d time' % best_time)
        best_assignment = deep_copy_job_list(possible_assignment)
        best_time = possible_sol.finishing_time()
        return best_assignment, best_time

  #import pdb;pdb.set_trace()
  # Switches
  for i, j in cart_squared(range(len(assigned_jobs))):
    print('look J%d with J%d' % ((i+1),(j+1)))
    for machine_ind1, machine_ind2 in cart_squared(range(num_machines)):
      possible_assignment = deep_copy_job_list(best_assignment)
      orig_mach1 = possible_assignment[i].mach
      orig_mach2 = possible_assignment[j].mach
      possible_assignment[i].mach = machine_ind1
      possible_assignment[j].mach = machine_ind2

      involved_machines = [orig_mach1, orig_mach2, machine_ind1, machine_ind2]

      possible_sol = Solution(possible_assignment)
      print('checking solution:')
      print(possible_sol)
      print('Value: %d, valid? %r' % (possible_sol.finishing_time(), possible_sol.is_valid()))

      new_val = max([possible_sol.machines[mach] for mach in involved_machines])
      old_val = max([Solution(best_assignment).machines[mach] for mach in involved_machines])
      #if possible_sol.is_valid() and new_val < old_val:
      if possible_sol.is_valid() and possible_sol.finishing_time() < best_time:
        print('found better solution with %d time' % best_time)
        best_assignment = deep_copy_job_list(possible_assignment)
        best_time = possible_sol.finishing_time()
        return best_assignment, best_time

  return best_assignment, best_time

def hill_climb(jobs):
  '''
  do the hill climb algorithm for finding optimal/near optimal solution:
  start with an arbitrary solution, then try to check the neighbouring solutions and
  iteratively head towards the best neighbour.
  '''
  init_jobs, init_sol = create_naive_solution(jobs)
  #init_jobs, init_sol = create_greedy_solution(jobs)

  if not init_sol.is_valid():
    return None

  best_assignment = init_jobs
  best_time = init_sol.finishing_time()
  print('Initial time: %d' % best_time)

  lp = lower_bound(jobs)
  changed = True
  while changed and best_time > lp:
    changed = False
    best_neighbout_assignment, best_neighbour_time = \
      get_best_neighbour(best_assignment)

    if best_neighbour_time < best_time:
      best_assignment = best_neighbout_assignment
      best_time = best_neighbour_time
      print('found better assignment with time: %d' % best_time)
      changed = True

  return Solution(best_assignment)



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

def output_solution(solution):
  '''
  Output the solution to the specified file
  '''
  output = ''
  if not sol:
    output = 'There is no solution for such input!'
    return output

  output += 'The problem had %d jobs that needed to be scheduled on %d machines.\n' % (num_jobs, num_machines)
  output += 'The found solution:\n'
  output += '%s' % sol
  output += '\n'
  output += '\nObjective function\'s value: max{%s} = %d\n' % (format_list(sol.finishing_times()), sol.finishing_time())
  output += '*Lower bound (not necessarily tight): %d\n' % lower_bound(orig_jobs)
  output += '\n'
  output += '**output format:\n\tm_k is the k\'th machine.\n\tJ_i(P, T) is the i\'th job with P processing time and is of type T.'

  return output

if __name__ == '__main__':
  orig_jobs = handle_file(input_file)
  jobs = deep_copy_job_list(orig_jobs)

  sol = hill_climb(jobs)

  output = output_solution(sol)
  out = open(output_file, 'w', encoding="utf8")
  out.write(output)
  out.close()
  #import pdb;pdb.set_trace()