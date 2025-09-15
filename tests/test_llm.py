from tools.llm import call_llm, email_to_tasks_prompt

if __name__ == "__main__":
    sample_email = "Hi Kavya, can you prepare the slides by Friday and confirm the venue?"
    prompt = email_to_tasks_prompt(sample_email)
    print("Prompt:\n", prompt)
    print("\nResponse:\n", call_llm(prompt))
