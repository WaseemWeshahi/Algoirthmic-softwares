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

num_nodes = 1

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
    for m in self.machines:
      types_set = set([j.t for j in m])
      if len(types_set) > 3:
        return False
    return True

  def finishing_times(self):
    return self.machine_sums

  def finishing_time(self):
    return max(self.finishing_times())

  def __repr__(self):
    return '\n'.join(['m%d : %s' % (ind+1, sorted(jobs_list)) for ind, jobs_list in enumerate(self.machines)])

  def __str__(self):
    return '\n'.join(['m%d : %s \t sum: %d, types: %s' % (ind+1, format_list(sorted(jobs_list)), self.machine_sums[ind], format_list(self.machine_types[ind])) for ind, jobs_list in enumerate(self.machines)])

class Node:
  def __init__(self, jobs_list, layer=0):
    self.jobs_list = jobs_list
    self.layer = layer

  def create_children(self):
    if self.layer >= num_jobs - 1:
      return []

    children = []
    for m in range(num_machines):
      new_jobs_list = deep_copy_job_list(self.jobs_list)
      new_jobs_list[self.layer+1].mach = m
      if Solution(new_jobs_list).is_valid():
        children.append(Node(new_jobs_list, self.layer+1))
    return children

  def handle_node(self, V):
    '''
    returns: should terminate?
    '''
    global num_nodes
    num_nodes += 1
    self.upper, self.possible_sol = upper_bound(self.jobs_list)
    self.lower = lower_bound(self.jobs_list)
    print(self)

    if self.lower >= V:
      return True
    if self.upper < V:
      return False
    if self.upper == V:
      return True

  def __repr__(self):
    return 'Layer:%d, Upper bound:%r, Lower bound:%r\nAssignment:%r' \
      % (self.layer, getattr(self, 'upper', float('inf')), getattr(self, 'lower', -1), self.jobs_list)

  def __str__(self):
    return self.__repr__()

def format_list(list):
  return ', '.join([str(x) for x in list])

def get_index(jobs, ind):
  for index, job in enumerate(jobs):
    if job.ind == ind:
      return index
  return -1

def global_lower_bound(jobs):
  proc_times = [j.proc_time for j in jobs]
  times_sum = sum(proc_times)
  return max(proc_times + [math.ceil(times_sum/num_machines)])

def lower_bound(jobs):
  '''
  Give a lower bound given jobs that may be partially assigned
  '''
  proc_times = [j.proc_time for j in jobs]
  times_sum = sum(proc_times)
  return max(proc_times + [math.ceil(times_sum/num_machines)] + Solution(jobs).finishing_times())

def upper_bound(jobs):
  '''
  Give an upper bound given jobs that may be partially assigned
  '''
  possible_assignment = deep_copy_job_list(jobs)
  for ind, j in enumerate(jobs):
    if j.mach == '?':
      possible_assignment[ind].mach = 0

  sol = Solution(possible_assignment)

  proc_times = [j.proc_time for j in jobs]
  times_sum = sum(proc_times)

  up = max([sol.finishing_time()] + [times_sum])
  return sol.finishing_time(), sol

def get_diff(old_assignment, new_assignment):
  diff_indices = [ind for ind in range(num_jobs) if old_assignment[ind].mach != new_assignment[ind].mach]

  diff_str = ', '.join(['%s: %d->%d' % (new_assignment[ind], old_assignment[ind].mach+1, new_assignment[ind].mach+1) for ind in diff_indices])
  return 'Obtained a new solution by moving: ' + diff_str + '\nNew machine finishing times: {%s}\n' % format_list(Solution(new_assignment).finishing_times())

def create_naive_solution(jobs):
  '''
  produce a naive solution, which is assigning jobs with type t to machine t%m
  '''
  naive_assignment = deep_copy_job_list(jobs)
  for i, job in enumerate(jobs):
    naive_assignment[i].mach = job.t % num_machines

  return naive_assignment, Solution(naive_assignment)

def cart_squared(list):
  return [(i,j) for i in list for j in list]

def cart_cubed(list):
  return [(i,j,k) for i in list for j in list for k in list]

def cart_quart(list):
  return [(i,j,k,l) for i in list for j in list for k in list for l in list]

def branch_and_bound(jobs):
  '''
  peform a branch and bound approach to find the optimal solution.
  '''
  assert jobs, 'No jobs to be scheduled..'
  global log
  try:
    jobs[0].mach = 0
    active_queue = [Node(jobs)]
    best_sol = None
    best_time = float('inf')
    while active_queue:
      cur_node = active_queue.pop()
      should_terminate = cur_node.handle_node(best_time)
      if not should_terminate:
        log += '*****************************************\nExtending the node: %s\n' % (cur_node)
        log += 'Current best solution:\n%s\n' % cur_node.possible_sol
        log += 'Machine finishing_times: {%s}\n' % format_list(cur_node.possible_sol.finishing_times())
        children = cur_node.create_children()
        active_queue.extend(children)
        best_sol = cur_node.possible_sol
        best_time = cur_node.upper

    return best_sol

  except KeyboardInterrupt:
    log += '\n\nProcess was terminated upon Keyboard interrupt, here is the latest solution:\n'
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
  output += 'Overall number of nodes visited: %d\n' % num_nodes
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
  sol = branch_and_bound(jobs)
  print("%d seconds elapsed" % (time.time()-start))
  output = output_solution(sol, time.time()-start)
  out = open(output_file, 'w', encoding="utf8")
  out.write(output)
  out.close()
