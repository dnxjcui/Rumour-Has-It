from cerebras.cloud.sdk import Cerebras
from openai import OpenAI
import os

init_prompt = """You are a student named {name} in grade {grade}. You're taking the following classes: {classes}, 
and you're friends with {friends}. You don't necessarily dislike or like your other classmates. Speech patterns: 
Every single response you give should be in complete character. ALWAYS SPEAK IN THE FIRST PERSON, using your 
experiences to guide your responses, your tone, and your vocabulary. Only speak as if you were truly living in this 
world in the first-person, and make sure to express your unique personality traits, flaws, and quirks.

Your backstory is as follows: {backstory}

Again, always speak in the first person, DO NOT add any labels in the beginning. Just talk and response like a 
person. You are to never break character, you are only you. You are {name}, refer to yourself in the first person."""


class Student:
    def __init__(self,
                 name: str,
                 grade: int,
                 friends: list,
                 classes: list,
                 backstory: str,
                 aware: bool = False,
                 model: str = "llama3.1-8b"):
        self.name = name
        self.grade = grade
        self.friends = friends
        self.aware = aware
        self.model = model

        if model == "llama3.1-8b" or model == "llama3.1-70b":
            self.client = Cerebras(api_key=os.environ.get('CEREBRAS_API_KEY'))
        elif model == "gpt-3.5-turbo":
            self.client = OpenAI()

        self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"{init_prompt.format(name=self.name, grade=self.grade, classes=classes, friends=friends, backstory=backstory)}"
                }
            ],
            model=self.model
        )
