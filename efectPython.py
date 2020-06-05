import sys
import os
import json
import datetime
import time
from urllib.parse import parse_qs


print(sys.version_info, sys.version)

def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value= bytes_or_str.decode('utf-8')
    return value

def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value= bytes_or_str.encode('utf-8')
    return value

with open('random.bin', 'wb') as f:
    f.write(os.urandom(10))

my_values= parse_qs('red=5&blue=0&gree=', keep_blank_values=True)    
print(repr(my_values))
print('Red: ', my_values.get('red'))
print('Green: ', my_values.get('green'))
print('Opacity: ', my_values.get('opacity'))

red = my_values.get('red', [""])[0] or 0
green = my_values.get('green', [""])[0] or 0
opacity = my_values.get('opacity', [""])[0] or 0

print('Red:  %r' % red)
print('Green:  %r' % green)
print('Opacity: %r' % opacity)

a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
print('First four:', a[:4])
print('Last four: ', a[-4:])
print('Middle two:', a[3:-3])

b = a[4:]
print('Before:', b)
b[1] = 99
print('After: ', b)
print('No change:', a)

b = a[:]
assert b == a and b is not a

b = a
print('Before', a)
a[:] = [101, 102, 103]
assert a is b
print('After ', a)

a = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
odds = a[::2]
evens = a[1::2]
print(odds)
print(evens)

a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares= [x**2 for x in a]
print(squares)
squares = map(lambda x: x ** 2, a)
print(squares)
even_squares = [x**2 for x in a if x % 2 == 0]
print(even_squares)
alt = map(lambda x: x**2, filter(lambda x: x % 2 == 0, a))
assert even_squares == list(alt)

chile_ranks = {'ghost': 1, 'habanero': 2, 'cayenne': 3}
rank_dict = {rank: name for name, rank in chile_ranks.items()}
chile_len_set = {len(name) for name in rank_dict.values()}
print(rank_dict)
print(chile_len_set)

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [x for row in matrix for x in row]
print(flat)

squared = [[x**2 for x in row] for row in matrix]
print(squared)

a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
b = [x for x in a if x > 4 if x % 2 == 0]
c = [x for x in a if x > 4 and x % 2 == 0]

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
filtered = [[x for x in row if x % 3 == 0]
for row in matrix if sum(row) >= 10]
print(filtered)

flavor_list = ['vanilla', 'chocolate', 'pecan', 'strawberry']
for flavor in flavor_list:
    print('%s is delicious' % flavor)

for i in range(len(flavor_list)):
    flavor = flavor_list[i]
    print('%d: %s' % (i + 1, flavor))  
for i, flavor in enumerate(flavor_list):
    print('%d: %s' % (i, flavor))      

names = ['Cecilia', 'Lise', 'Marie']
letters = [len(n) for n in names]

longest_name = None
max_letters = 0
for i in range(len(names)):
    count = letters[i]
    if count > max_letters:
        longest_name = names[i]
        max_letters = count
print(longest_name)

for i, name in enumerate(names):
    count = len(names)
    if count > max_letters:
        longest_name = name
        max_letters = count
print(longest_name)        

for i in range(10):
    print('Loop: %d' % i)
else:
    print('Else block!')

a = 4
b = 9
for i in range(2, min(a, b) + 1):
    print('Testing: ', i)
    if a % i == 0 and b % i == 0:
        print('Not coprime')
        break
else:
    print('Coprime')    

def load_json_key(data, key):
    try:
        result_dict = json.loads(data)
    except ValueError as e:
        raise KeyError from e
    else:
        return result_dict[key]    


UNDEFINED = object()
def divide_json(path):
    handle = open(path, 'r+')
    try:
        data = handle.read()
        op = json.loads(data)
        value = (op['numerator'] / op['denominator'])
    except ZeroDivisionError as e:
        return UNDEFINED
    else:
        op['result'] = value
        result = json.dumps(op)
        handle.seek(0)
        handle.write(result)
        return value
    finally:
        handle.close()

def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        
        print('Invalid inputs')
        return False, None        


print(divide(2,0))

def sort_priority(values, group):
    def helper(x):
        if x in group:
            return (0, x)   
        return (1, x)
    values.sort(key=helper)

def sort_priority2(numbers, group):
    found = False
    def helper(x):
        if x in group:
            found = True # Seems simple
            return (0, x)
        return (1, x)
    numbers.sort(key=helper)
    return found

def sort_priority3(numbers, group):
    found = False
    def helper(x):
        nonlocal found
        if x in group:
            found = True
            return (0, x)
        return (1, x)
    numbers.sort(key=helper)
    return found    

numbers = [8, 3, 1, 2, 5, 4, 7, 6]
group = {2, 3, 5, 7}
sort_priority3(numbers, group)
print(numbers)        

class Sorter(object):
    def __init__(self, group):
        self.group = group
        self.found = False
    
    def __call__(self, x):
        if x in self.group:
            self.found = True
            return (0, x)
        return (1, x)

sorter = Sorter(group)
numbers.sort(key=sorter)
assert sorter.found is True

def index_words(text):
    result = []
    if text:
        result.append(0)
    for index, letter in enumerate(text):
        if letter == ' ' :
            result.append(index + 1)
    return result

address = 'Four score and seven years ago...'
result = index_words(address)
print(result[:])
    
def index_words_iter(text):
    if text:
        yield 0
    for index, letter in enumerate(text):
        if letter == ' ' :
            yield index + 1

resultTemp = list(index_words_iter(address))     
print(resultTemp)    

def normalize(numbers):
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result

visits = [15, 35, 80]
percentages = normalize(visits)
print(percentages)  

class ReadVisits(object):
    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        with open(self.data_path) as f:
            for line in f:
                yield int(line)

visits = ReadVisits('my_numbers.txt')
percentages = normalize(visits)
print(percentages)

def log(sequence, message, *values):
    if not values:
        print(sequence, message)
    else:
        values_str = ', '.join(str(x) for x in values)
        print('%s: %s: %s' % (sequence, message, values_str))

log('My numbers are', [1, 2])
log('Hi there', [])
favorites = [7, 33, 99]
log(1, 'Favorite colors', *favorites)

def my_generator():
    for i in range(10):
        yield i

def my_func(*args):
    print(args)


it = my_generator()
my_func(*it)

def logNew(message, when=None):
    
    """Log a message with a timestamp.
    Args:
    message: Message to print.
    when: datetime of when the message occurred.
    Defaults to the present time.
    """

    when = datetime.datetime.now() if when is None else when
    print('%s: %s' % (when, message))

logNew('Hi there!')
time.sleep(1)
logNew('Hi again!')

def decode(data, default=None):
    """Load JSON data from a string.
    Args:
    data: JSON data to decode.
    default: Value to return if decoding fails.
    Defaults to an empty dictionary.
    """
    if default is None:
        default = {}
    try:
        return json.loads(data)
    except ValueError:
        return default

foo = decode('bad data')
foo['stuff'] = 5
bar = decode('also bad')
bar['meep'] = 1
print('Foo:', foo)
print('Bar:', bar)    

def safe_division(number, divisor, ignore_overflow=False, ignore_zero_division=False):

    try:
        return number / divisor
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float('inf')
        else:
            raise
result = safe_division(1, 10**500, ignore_overflow=True, ignore_zero_division=False)
print(result)
result = safe_division(1, 0, ignore_overflow=False, ignore_zero_division=True)
print(result)

class SimpleGradebook(object):
    def __init__(self):
        self._grades = {}
    
    def add_student(self, name):
        self._grades[name] = []
    
    def report_grade(self, name, score):
        self._grades[name].append(score)
    
    def average_grade(self, name):
        grades = self._grades[name]
        return sum(grades) / len(grades)

book = SimpleGradebook()
book.add_student('Isaac Newton')
book.report_grade('Isaac Newton', 90)
print(book.average_grade('Isaac Newton'))

class BySubjectGradebook(object):
    def __init__(self):
        self._grades = {}
    
    def add_student(self, name):
        self._grades[name] = {}

    def report_grade(self, name, subject, grade):
        by_subject = self._grades[name]
        grade_list = by_subject.setdefault(subject, [])
        grade_list.append(grade)

    def average_grade(self, name):
        by_subject = self._grades[name]
        total, count = 0, 0
        for grades in by_subject.values():
            total += sum(grades)
            count += len(grades)

        return total / count


book = BySubjectGradebook()
book.add_student('Albert Einstein')
book.report_grade('Albert Einstein', 'Math', 75)
book.report_grade('Albert Einstein', 'Math', 65)
book.report_grade('Albert Einstein', 'Gym', 90)
book.report_grade('Albert Einstein', 'Gym', 95)

print(book.average_grade('Albert Einstein'))


import collections
Grade = collections.namedtuple('Grade', ('score', 'weight'))

class Subject(object):
    def __init__(self):
        self._grades = []
    
    def report_grade(self, score, weight):  
        self._grades.append(Grade(score, weight))
    
    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
            total_weight += grade.weight
        return total / total_weight


class Student(object):
    def __init__(self):
        self._subjects = {}
    
    def subject(self, name):
        if name not in self._subjects:
            self._subjects[name] = Subject()
        return self._subjects[name]
    
    def average_grade(self):
        total, count = 0, 0
        for subject in self._subjects.values():
            total += subject.average_grade()
            count += 1
        return total / count

class Gradebook(object):
    def __init__(self):
        self._students = {}
    
    def student(self, name):
        if name not in self._students:
            self._students[name] = Student()
        return self._students[name]        

book = Gradebook()
albert = book.student('Albert Einstein')
math = albert.subject('Math')
math.report_grade(80, 0.10)
# ...
print(albert.average_grade())

names = ['Socrates', 'Archimedes', 'Plato', 'Aristotle']
names.sort(key=lambda x: len(x))
print(names)

class BetterCountMissing(object):
    def __init__(self):
        self.added = 0
    
    def __call__(self):
        self.added += 1
        return 0

counter = BetterCountMissing()
counter()
assert callable(counter)

class MyBaseClass(object):
    def __init__(self, value):
        self.value = value

class MyChildClass(MyBaseClass):
    def __init__(self):
        MyBaseClass.__init__(self, 5)

class TimesTwo(object):
    def __init__(self):
        self.value *= 2

class PlusFive(object):
    def __init__(self):
        self.value += 5        

class OneWay(MyBaseClass, TimesTwo, PlusFive):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)

foo = OneWay(5)
print('First ordering is (5 * 2) + 5 =', foo.value)        

class Explicit(MyBaseClass):
    def __init__(self, value):
        super(__class__, self).__init__(value * 2)

class Implicit(MyBaseClass):
    def __init__(self, value):
        super().__init__(value * 2)

assert Explicit(10).value == Implicit(10).value

class ToDictMixin(object):
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output    

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, '__dict__'):
            return self._traverse_dict(value.__dict__)
        else:
            return value    

class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right        

class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None, right=None, parent=None):
        super().__init__(value, left=left, right=right)
        self.parent = parent     

    def _traverse(self, key, value):
        if (isinstance(value, BinaryTreeWithParent) and key == 'parent'):
            return value.value # Prevent cycles
        else:
            return super()._traverse(key, value)     

class NamedSubTree(ToDictMixin):
    def __init__(self, name, tree_with_parent):
        self.name = name
        self.tree_with_parent = tree_with_parent              

tree = BinaryTree(10,
left=BinaryTree(7, right=BinaryTree(9)),
right=BinaryTree(13, left=BinaryTree(11)))
print(tree.to_dict())

root = BinaryTreeWithParent(10)
root.left = BinaryTreeWithParent(7, parent=root)
root.left.right = BinaryTreeWithParent(9, parent=root.left)
print(root.to_dict())

my_tree = NamedSubTree('foobar', root.left.right)
print(my_tree.to_dict()) # No infinite loop
