from src.god import God
from datetime import timedelta, datetime
import random
import copy
from openai import OpenAI

def randomize_class_groups(student_list, classes, size_class_groups):
    class_groups = {}
    for curr_class in classes:
        class_group = {}
        duplicate_students = copy.deepcopy(student_list)
        # print(duplicate_students)
        # randomly select n names from students
        counter = 0
        while len(duplicate_students) > size_class_groups:
            class_group[counter] = random.sample(duplicate_students, size_class_groups)

            # remove just previously sampled from duplicate_students
            for student in class_group[counter]:
                duplicate_students.remove(student)
            counter += 1

        if len(duplicate_students) == 1:
            class_group[counter - 1].append(duplicate_students[0])
        elif len(duplicate_students) > 1:
            class_group[counter] = duplicate_students

        class_groups[curr_class] = class_group

    return class_groups

if __name__ == '__main__':
    student_list = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
    classes = ['Math', 'Science', 'History', 'Lunch', 'English', 'Art']

    # friends should be able to be represented as an undirected graph. For the sake of simplicity within this model,
    # each friend group is disjoint.
    friends = {"Alice": ["Bob", "Charlie"], "Bob": ["Alice", "Charlie"], "Charlie": ["Alice", "Bob"], "David": ["Eve"], "Eve": ["David"]}
    friend_groups = {"Alice": 0, "Bob": 0, "Charlie": 0, "David": 1, "Eve": 1}

    grade = 6
    rumor = "Nick has a crush on Elena"

    ## where does the rumor start?
    initial_aware_student = "Alice"

    ## who do we not want to know?
    target_student = "Eve"

    # friends = [["Alice", "Bob", "Charlie"], ["David", "Eve"]] # should we do a list of lists?
    model = "gpt-3.5-turbo"
    # model = "llama3.1-8b"

    # randomize class groups. For each class, have a dictionary containing a group # and a list of all the people in
    # that group.
    size_class_groups = 2
    class_groups = randomize_class_groups(student_list, classes, size_class_groups)

    n_conversations_class = 1
    n_conversations_friend = 3

    max_days = 5

    class_start_time = datetime(100, 1, 1, 8, 0) # with a dummy date
    class_length = timedelta(hours=1, minutes=10)

    god = God(student_list, friends, friend_groups, class_groups, grade, classes, max_days, n_conversations_class,
              n_conversations_friend, initial_aware_student=initial_aware_student, target_student=target_student,
              rumor=rumor,model=model)
    god.generate_all_students(friends, aware_student=initial_aware_student, rumor=rumor)

    god.run_simulation(max_days)


