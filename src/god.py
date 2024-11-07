import copy
import os
from datetime import timedelta, datetime
from src.student import Student

from cerebras.cloud.sdk import Cerebras
from openai import OpenAI
from functools import partial
import shutil

#### THIS IS THE PROMPT FOR THE SYSTEM "GOD" ####
background_prompt = """
You are the god of a fictional world. 
You are looking to craft a very realistic, detailed, and immersive world for your inhabitants, of which you also create.
This world specifically has the following characteristics:
- The setting is a classroom.
- The inhabitants are students, named {student_names}.
- The students are in grade {grade}.
- The students are taking the following classes: {classes}. 
Do not simulate anything yet. Acknowledge that you will create meticulously detailed simulated students in the future.
"""

# we could standardize this more by either
# a. passing in a strict set of factors to generate,
# or b. using another AI instance to generate a strict set of factors
simulation_prompt = """Craft a highly meticulous and verbose background for an imaginary student named {name} in 
grade {grade}. This student is taking the following classes: {classes}, and is friends with {friends}. Describe this 
student in the third person. Make sure to include details about their family, hobbies, extra-curriculars, interests, 
how studious they are, and any other relevant information. Also include any unique personality traits, quirks, 
or flaws that this normal student may possess."""

### THIS IS THE PROMPT FOR FRIEND GROUPS BEFORE SCHOOL ###
friend_prompt_pre = """The time is roughly {time}. You just got to school, and you're mingling with your friend 
group: {friends}, chatting with them, having a day-to-day conversation that friends usually have at school. Your next 
class is {curr_class}. Respond in the first person, no need to specify who you are."""

### THIS IS THE PROMPT FOR FRIEND GROUPS AFTER SCHOOL ###
friend_prompt_post = """The time is roughly {time}. You just got out of your last class, and you're mingling with 
your friend group {friends}, chatting with them, having a day-to-day conversation that friends usually have at 
school. You're about to leave school and resume life outside of it! Respond in the first person, no need to specify 
who you are."""

### THIS IS THE PROMPT FOR FRIEND GROUPS BETWEEN CLASSES ###
friend_prompt = """The time is roughly {time}. You just got out of {pre_class}, and you're about to go to your next 
period, which is {post_class}. You're chatting with your friends: {friends}, still having a day-to-day conversation 
that friends usually have at school. Respond in the first person, no need to specify who you are."""

### THIS IS THE PROMPT FOR STUDENTS DURING CLASSES ###
class_prompt = """The time is roughly {time}. You're at {curr_class} class right now, sitting in assigned seats. 
You're chatting with {classmates} about the class, the teacher, and the homework. You're having a casual 
conversation, having a normal conversation that students normally have during class. Respond in the first person, 
no need to specify who you are."""

### THIS IS THE PROMPT FOR STUDENTS DURING LUNCH ###
lunch_prompt = """The time is roughly {time}. You're at lunch right now, sitting with your friends {friends} and 
maybe others, talking about your food, your morning classes, and anything else going on in your life. Respond in the 
first person."""


class God:
    def __init__(self,
                 student_names: list,
                 friends: dict,
                 friend_groups: dict,
                 class_groups: dict,
                 grade: int,
                 classes: list,
                 max_days: int = 5,
                 n_conversations_class: int = 3,
                 n_conversations_friend: int = 2,
                 initial_aware_student: str = None,
                 target_student: str = None,
                 rumor: str = None,
                 class_start_time: datetime = datetime(100, 1, 1, 8, 0),
                 class_length: timedelta = timedelta(hours=1, minutes=10),
                 model : str = "llama3.1-8b"):
        self.student_names = student_names
        self.friends = friends
        self.friend_groups = friend_groups
        self.class_groups = class_groups
        self.grade = grade
        self.classes = classes
        self.students = {}
        self.max_days = max_days
        self.n_conversations_friend = n_conversations_friend
        self.n_conversations_class = n_conversations_class
        self.initial_aware_student = initial_aware_student
        self.target_student = target_student
        self.rumor = rumor
        self.class_start_time = class_start_time
        self.class_length = class_length
        self.model = model

        self.aware_students = {initial_aware_student}

        if model == "llama3.1-8b" or model == "llama3.1-70b":
            self.client = Cerebras(api_key=os.environ.get('CEREBRAS_API_KEY'))
        elif model == "gpt-3.5-turbo":
            self.client = OpenAI()
        self.day = 0

        self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": background_prompt.format(student_names=student_names, grade=grade, classes=classes)
                }
            ],
            model=self.model
        )

        # removes text logs
        if os.path.exists("text_logs"):
            shutil.rmtree("text_logs")

        os.mkdir("text_logs")

    def _generate_student(self,
                          name: str,
                          friends: list,
                          aware: bool = False,
                          rumor: str = "They are a simulation"):
        text_prompt = simulation_prompt.format(name=name, grade=self.grade, friends=friends, classes=self.classes)

        if aware:
            text_prompt += f" The student is aware of the following rumor: {rumor}"

        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": text_prompt
                }
            ],
            model=self.model
        )
        backstory = response.choices[0].message.content

        with open(os.path.join("text_logs", "backstories.txt"), "a") as f:
            f.write(f'{backstory}\n############################\n')

        return Student(name, self.grade, friends, self.classes, backstory, aware, self.model)

    def generate_all_students(self, friends: dict, aware_student: str, rumor: str = "They are a simulation"):
        for student in self.student_names:
            if student == aware_student:
                self.students[student] = self._generate_student(student, friends[student], True, rumor)
            else:
                self.students[student] = self._generate_student(student, friends[student])

    def _analyze_conversations(self, contexts: dict, convo_setting: str, curr_class: str = None):
        """
        Analyze all the contexts/conversations. If the rumor is brought up, then we set all the students in that
        conversation as aware.
        :param contexts:
        :param convo_setting: If with friends, "friend". Otherwise, "class". This is used to determine the prompt.
        :return:
        """
        for group, context in contexts.items():
            found = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"""You're analyzing the conversation to see if the rumor: "{self.rumor}" was
                        brought up. If mentioned, answer "Yes". If not, answer "No". You cannot respond with I don't
                        know, or any other answer. Again, ONLY respond with "Yes" or "No"."""
                    }
                ],
                model=self.model
            ).choices[0].message.content

            found = "yes" in found.lower()

            # for text in context:
            #     if "Elena" in text.lower() and "Nick" in text.lower():
            #         found = True
            #         break

            if found:
                # We will have to move some students to the aware list
                if convo_setting == "friend":
                    for student, friend_group in self.friend_groups.items():
                        if friend_group == group:
                            self.aware_students.add(student)
                            if student == self.target_student:
                                return True  # return true to end everything
                elif convo_setting == "class":
                    class_group = self.class_groups[curr_class]
                    for group_id, students in class_group.items():
                        if group_id == group:
                            for student in students:
                                self.aware_students.add(student)
                                if student == self.target_student:
                                    return True
            else:
                pass  # do nothing

        return False

    def _simulate_friend_conversations(self, prompt: type(partial)):
        """
        Simulate conversations between friends, using n_conversations_friend as the number of conversations to simulate.
        For the sake of simplicity, each friend will be able to say n_conversations_friend things.
        :return:
        """
        contexts = {}
        for i in range(self.n_conversations_friend):
            for student in self.students:
                if self.friend_groups[student] not in contexts.keys():
                    context = "You're starting the conversation with your friends!"
                else:
                    context = contexts[self.friend_groups[student]]

                pr = prompt(friends=self.friends[student])

                response = self.students[student].client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": prompt(friends=self.friends[student])
                        },
                        {
                            "role": "user",
                            "content": f"{context}"
                        }
                    ],
                    model=self.model,
                    max_completion_tokens=100
                )
                response = response.choices[0].message.content

                if self.friend_groups[student] not in contexts.keys():
                    contexts[self.friend_groups[student]] = [f"{student}: {response}"]
                else:
                    contexts[self.friend_groups[student]].append(f"{student}: {response}")

        return contexts

    def _simulate_class_conversations(self, prompt: type(partial), curr_class: str):
        curr_class_group = self.class_groups[curr_class]
        contexts = {}
        for i in range(self.n_conversations_class):
            for group_id in curr_class_group.keys():
                for student in curr_class_group[group_id]:
                    classmates = copy.deepcopy(curr_class_group[group_id])
                    classmates = classmates.remove(student)
                    if group_id not in contexts.keys():
                        context = f"You're starting the conversation with your classmates {classmates}!"
                    else:
                        context = contexts[group_id]

                    response = self.students[student].client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": prompt(classmates=classmates)
                            },
                            {
                                "role": "user",
                                "content": f"{context}"
                            }
                        ],
                        model=self.model,
                        max_completion_tokens=50
                    ).choices[0].message.content

                    if group_id not in contexts.keys():
                        contexts[group_id] = [f"{student}: {response}"]
                    else:
                        contexts[group_id].append(f"{student}: {response}")

        return contexts

    def simulate_day(self):
        time = self.class_start_time

        with open(os.path.join("text_logs", "inter_class.txt"), "a") as f:
            f.write("Day: {:3d}\n".format(self.day))
        with open(os.path.join("text_logs", "class.txt"), "a") as f:
            f.write("Day: {:3d}\n".format(self.day))


        for i in range(len(self.classes)):
            curr_class = self.classes[i]

            ## simulate friend convos
            if i == 0:
                pre_friend_prompt = partial(friend_prompt_pre.format, time=time.time(), curr_class=self.classes[i])
            else:
                pre_friend_prompt = partial(friend_prompt.format, time=time.time(), pre_class=self.classes[i - 1],
                                            post_class=self.classes[i])

            contexts = self._simulate_friend_conversations(pre_friend_prompt)

            with open(os.path.join("text_logs", "inter_class.txt"), "a") as f:
                f.write(f"Class: {curr_class}\n")
                for group, context in contexts.items():
                    f.write(f"Group {group}: \n")
                    for convo in context:
                        f.write(f"{convo}\n")
                f.write("############################\n")

            if self._analyze_conversations(contexts, "friend"):
                return (i, "friend")  # returns the class and the setting that ended it

            ## simulate class convos
            if curr_class == "Lunch":
                class_convo_prompt = partial(lunch_prompt.format, time=time.time())
                contexts = self._simulate_friend_conversations(class_convo_prompt)

                with open(os.path.join("text_logs", "class.txt"), "a") as f:
                    f.write(f"Class: {curr_class}\n")
                    for group, context in contexts.items():
                        f.write(f"Group {group}: \n")
                        for convo in context:
                            f.write(f"{convo}\n")
                    f.write("############################\n")

                if self._analyze_conversations(contexts, "friend"):
                    return (i, "friend")  # returns the class and the setting that ended it
            else:
                class_convo_prompt = partial(class_prompt.format, time=time.time(), curr_class=curr_class)
                contexts = self._simulate_class_conversations(class_convo_prompt, curr_class)

                with open(os.path.join("text_logs", "class.txt"), "a") as f:
                    f.write(f"Class: {curr_class}\n")
                    for group, context in contexts.items():
                        f.write(f"Group {group}: \n")
                        for convo in context:
                            f.write(f"{convo}\n")
                    f.write("############################\n")

                if self._analyze_conversations(contexts, "class"):
                    return (i, "class")  # returns the class and the setting that ended it

            time += self.class_length

        ## simulate friend convos after school
        post_friend_prompt = partial(friend_prompt_post.format, time=time.time())
        contexts = self._simulate_friend_conversations(post_friend_prompt)
        if self._analyze_conversations(contexts, "friend"):
            return (len(self.classes), "friend")  # returns the class and the setting that ended it

        self.day += 1
        return None

    def _run_condition(self, days: int):
        if days == 0:
            return True
        else:
            return self.day <= days

    def run_simulation(self, days: int):
        """Runs the whole simulation. If days = 0, then it runs until the rumor is found."""

        while self._run_condition(days):
            print("Day {:3d}: Students in the know: {aware_students}".format(self.day,
                                                                             aware_students=self.aware_students))
            result = self.simulate_day()

            if result is not None:
                print(f"Rumor found on day {self.day} at {result[0]} in a {result[1]} setting.")
                print("Students in the know: {aware_students}".format(self.day, aware_students=self.aware_students))
                break
