from tools.llm import call_llm, email_to_tasks_prompt

email_text = "Hi Kavya, can you prepare the slides by Friday and confirm the venue for next week's meeting?"
prompt = email_to_tasks_prompt(email_text)

print("Prompt being sent:\n", prompt)
print("\n--- LLM Output ---")
print(call_llm(prompt))
