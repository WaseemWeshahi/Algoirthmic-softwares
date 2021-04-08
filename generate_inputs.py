import sys
import os
from random import randint
import math
# "Main" is found at end of file..
# The output directory name
output_dir = sys.argv[1]

MAX_TYPE = 5

MAX_TIME = 20

num_examples = 12

# Input looks like: (m, (p0, t0), (p1, t1), ... , (pN, tN))
def generate_tuples(n = 40, m = 3):
  inp = [m, n]

  for _ in range(n):
    inp.append((randint(1, MAX_TIME), randint(1, MAX_TYPE)))

  return inp

def process_tuples(input):
  out_str = ""

  out_str += "# number of machines\n%d\n" % inp[0]

  out_str += "# Jobs as pairs of processing time and type\n# %d jobs\n" % inp[1]

  for tup in inp[2:]:
     out_str += "%d, %d\n" % (tup[0], tup[1])

  return out_str

def write_files(strings_list, directory):
  for i, string in enumerate(strings_list):
    out = open('/'.join([directory, 'randomized%d.txt' % i]), 'w', encoding="utf8")
    out.write(string)
    out.close()
    

if __name__ == '__main__':

  rand_inputs = []
  for _ in range(num_examples):
    rand_inputs.append(generate_tuples())

  strings_to_write = []
  for inp in rand_inputs:
    strings_to_write.append(process_tuples(inp))

  write_files(strings_to_write, output_dir)

