# Rumour Has It! <br><sup>_Your words travels further than you think!_</sup>

## Description
Hello! I hope you are doing well, whoever you are!

I am building a Simulated Information Diffusion Model using Cerebras Cloud SDK API. This project was inspired by the pizza meter, a semi-real form of meta-data that offers insights on when the US is about to declare war, and a specific scene in Avatar: The Last Airbender where Zuko finds out Aang is on Kyoshi island through a series of people gossiping. 

For the sake of simplicity, this simple model relies on a classroom simulation. We first define some set number of students to be in both friendship groups and class groups. These undirected networks are how the information will be spread from one student to another. I then initialize multiple AI agents (acting as the students) with complex, AI-generated backgrounds, and simulate them to be as similar as real people as possible. Then, we have these agents conversate with each other, while tracking the flow of a specific piece of planted information in their conversations. With properly defined conversation networks, we can see how fast information flows between people who are n degrees away from each other, simply through regular, day-to-day word of mouth interactions.

## Key Features
This project is reliant on Cerebras fast inference. 
Larger, more realistic, and more complex models with higher numbers of agents are dependent on the fast inference offered by Cerebras, and other models out on the market simply do not suffice. 
Unfortunately, I cannot run actual benchmarks and tests, as my current Cerebras API plan will limit me for the RPM. 

## Usage
I swear I will come back and document this part better, but I have an algo exam in 11 hours (it's currently 30 minutes past midnight) and I haven't studied for it at all. 

## To-Do List
- [x] Cerebras for back-end
- [x] OpenAI model options
- [ ] Store our data in a better representation
- [ ] GUI (probably gradio or streamlit)
- [ ] Automatic simulation of degrees separation
- [ ] Graph visualization and construction
- [ ] Social media feature
