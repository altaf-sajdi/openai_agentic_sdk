import os
from dotenv import load_dotenv
from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel


# this statment use for other api key in .env file, of i have openai api key i can use it in .env file
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

provider = AsyncOpenAI(
    api_key=google_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",

    )

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=provider,
    )

# strat agent code

agent = Agent(
    name="story_writer",
    instructions="you are a islamic story writer for man and woman and children, when sameone say asslam o alikum you should say asslam o alikum, you ask for name and age and gender and language one by one and then you write a story for them, you should write a story in the language that they speak, if sameine say by then say allah hafiz.",
    model=model,
)


result = Runner.run_sync(
    agent,
    input("Enter your name: "),
    )

print(result.final_output)

