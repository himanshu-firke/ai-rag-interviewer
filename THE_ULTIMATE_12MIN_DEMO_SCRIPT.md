# 🎙️ The Ultimate 12-Minute Demo Script: AI Interview Screener

## 1. The Hook & Introduction (0:00 – 1:30)
**Visual**: Landing Page.
- "Hello everyone. My name is [Your Name], and I'm thrilled to present my final submission for the **PGAGI AI/ML & Backend Intern Assignment**."
- "Think about the last time you were screened for a job. Usually, it's a generic set of questions that might not even touch on your actual skills. I've built a system that changes that."
- "My project is a **Role-Based Candidate Screening System**. It uses **Retrieval-Augmented Generation (RAG)**. In simple terms: instead of guessing, the AI 'reads' a technical textbook and 'reads' your resume to create a unique, fair, and technically accurate interview for you."

---

## 2. System Architecture: The Big Picture (1:30 – 4:00)
**Visual**: Show the **Mermaid Architecture Diagram** from the README.
- "Let's look at how this system is built. I've divided it into clear sections so it's modular and easy to maintain."
- "**The Frontend**: This is the 'face' of the app. It's built with Next.js and handles everything the user sees—from the upload screen to the live interview."
- "**The API Layer**: This is the bridge. We use FastAPI to handle requests and JWT to make sure only authorized users can access their data."
- "**The Service Layer**: This is the 'worker'. It parses your resume, generates the questions, and calculates your scores."
- "**The RAG Core**: This is the 'brain'. It takes raw textbook PDFs, breaks them into small pieces (chunks), and turns them into mathematical vectors so the AI can find the right information instantly."
- "**The Database**: We use SQLite to store your profile and interview history, keeping everything organized and persistent."

---

## 3. Tech Stack: Why I Chose These Tools (4:00 – 6:30)
**Visual**: Scroll through the "Tech Stack" section in your README.
- "I didn't just pick these tools because they are popular; I picked them for specific reasons:"
- "**FastAPI (Python)**: I used this for the backend because it's incredibly fast and supports asynchronous tasks. In an interview, you don't want the user waiting for a question to load—FastAPI keeps it snappy."
- "**ChromaDB**: This is my **Vector Database**. I chose it because it's lightweight and perfect for storing the 'embeddings' or 'math versions' of our technical textbooks. It makes searching for context extremely efficient."
- "**Next.js**: For the frontend, I wanted a modern SaaS look. Next.js gives us the performance and the premium feel that makes the user experience stand out."
- "**Groq & Gemini**: I use a dual-LLM setup. **Groq** provides the Llama 3.3 model, which is arguably the fastest inference engine available today. For embedding the text, I use **Google's Gemini** because of its high accuracy in understanding technical language."
- "**SQLAlchemy & SQLite**: For a screening system, data integrity is key. This stack gives us a reliable way to store scores and feedback without needing a complex server setup."

---

## 4. Onboarding: Getting Started (6:30 – 8:00)
**Visual**: Sign up a new user, then Log in.
- "Let's see it in action. First, I'll sign up. We use secure hashing for passwords to ensure candidate data is safe. Once logged in, you're greeted with a dashboard."
- **Visual**: Show the Upload page.
- "The candidate selects their role. Today, I'll go with **Full Stack Engineer**. Each role has its own dedicated textbook in the backend knowledge base."

---

## 5. The Core Flow: Resume Parsing & RAG (8:00 – 10:30)
**Visual**: Upload a resume.
- "I'm uploading a resume now. Look at the backend logic: the AI is currently reading the PDF. It's not just looking for keywords; it's identifying the candidate's **Experience Level** (Junior, Mid, or Senior) and their specific tech stack."
- **Visual**: Show the first question. **SWITCH TO TERMINAL WINDOW**.
- "**PROMPT**: *'Please look at these terminal logs.'*"
- "This is the most important part of the demo. See these logs? The system just queried **ChromaDB**. It found the most relevant sections from the 'Full Stack' textbook and gave them to the LLM. That's why this first question is so specific and grounded in real technical theory."
- "If I answer well, the system will increase the difficulty for the next question. This is **Adaptive Intelligence**."

---

## 6. Interview Interaction: Coding, Voice & Navigation (10:30 – 12:30)
**Visual**: Show Question 1, then click "Next" to find a coding question.
- "Now, let's look at the actual interview interface. We don't just ask conceptual or theoretical questions"    
- "**Coding Challenges**: For roles like Full Stack or Backend, the system generates actual coding problems. You can see the integrated editor here where I can write, format, and structure my code. It's a real-world environment."
- "**Microphone Support**: If a question is conceptual or scenario-based, I don't have to type. I can just click this microphone icon and use **Speech-to-Text** to answer naturally. This makes the interview feel more like a conversation."
- "**Navigation**: One unique feature is the ability to move back and forth. If I realize I made a mistake in Question 1 while I'm on Question 3, I can simply click 'Previous', edit my answer, and then continue. Nothing is locked until I hit 'Finish'."
- "**Final Processing**: To keep the experience smooth, the complex AI evaluation for all 7 questions happens at the very end. Once I click 'Finish', the system batches all answers and runs the multi-dimensional scoring in one go."

---

## 7. Evaluation & Final Reporting (12:30 – 13:30)
**Visual**: Complete the interview and show the Results page.
- "After the final processing, the system generates this comprehensive report. It's not just a score; it's a deep dive into **Correctness, Depth, and Clarity**."
- "You can see my strengths and weaknesses clearly listed. This report can be downloaded as a **PDF**, making it ready for any hiring committee."

---

## 8. Conclusion & Final Note (13:30 – 14:00)
**Visual**: Landing Page.
- "In summary: we've used RAG to create a grounded, fair, and adaptive screening tool that respects a candidate's background and tests real-world skills."
- "Thank you for joining me for this demo. I'm now open for any questions about the architecture, the AI pipeline, or the tech stack."
