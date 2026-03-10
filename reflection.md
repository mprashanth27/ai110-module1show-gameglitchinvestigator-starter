# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
bug-1: The hints are not accurate. 
For instance, in Normal difficulty the secret was 89, I submitted 6 as my initial guess and kept on decrementing the guess by 2 till 0 as per the hint which said to go lower.

bug-2: Unable to change Difficulty after a game session
After a playing a game in normal difficulty, I wasn't able to change it to easy or hard until I refreshed the page.

bug-3: New Game button Doesn't work 
After the attempts are exhausted the console says "Game over. Start a new game to try again.". After clicking the New Game button, the secret changes, attempts reset but score & history remain unchanged do not know if that is the intended behaviour but the console doesn't take new guesses.

bug-4: The secret's range doesn't correspond with Difficulty
In Easy Difficulty, the secret should be in the range of 1 - 20 but it was 46.
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
