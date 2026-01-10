# 🎨 AI Fashion Design Generator 👗✨

## 🧩 Problem Overview
Many aspiring fashion designers (especially students) want to explore creative clothing ideas but often run into challenges:

-  Lack of artistic or technical drawing skills  
-  Professional tools are expensive & time-consuming  
-  Limited access to resources or industry expertise  

This project introduces an accessible solution using **Generative AI**, enabling users to **create clothing concepts from text prompts** and explore real-world, budget-friendly alternatives online.

---

## 🚀 Project Goal
To democratize fashion experimentation by enabling anyone to:

- ✏️ Describe an idea in natural language  
- 🤖 Generate unique fashion designs via AI models  
- 🔎 Discover similar affordable items available online  
- 💡 Learn and get inspired by design concepts  

---

## 🧠 Features & Capabilities

### 🎨 AI Design Generation
Enter prompts such as:
> *"A futuristic neon streetwear jacket with cyberpunk aesthetics"*

The system returns generated visuals matching the concept.

### 🛍️ Real Product Recommendations
Automatically suggests similar items from online retailers — with filters for price, style, and category.

### 🧰 Customization Tools
- Color palettes  
- Style preference (streetwear, high fashion, minimal, vintage…)  
- Gender options  
- Seasonal wear  

### 💾 Save & Share
- Export generated designs  
- Save favorite styles  
- Share with peers or social platforms  

---

## 🏗️ System Architecture (Concept)
1. 🧾 User provides text prompt  
2. 🤖 AI model generates fashion design image  
3. 🛒 Product matching engine finds similar real-world items  
4. 🌐 UI displays designs + suggestions  

---

## 👥 Target Users
- 👩‍🎓 Students exploring fashion design  
- 🎨 Hobbyists & creatives  
- 👗 Small clothing brands & boutiques  
- 📚 Fashion coursework & education programs  

---



## 📦 Tech & Tools (Potential Stack)
- **AI Model** → Stable Diffusion / Midjourney / Custom GenAI  
- **Backend** → Python / Node.js  
- **Frontend** → React / Next.js / Flutter  
- **Product Matching** → Web scraping / e-commerce APIs  
- **Storage** → Cloud bucket for design outputs  


#### Setup

1. **Clone** 
    ```bash
    git clone https://github.com/AasthathecoderX/Paridhana
    cd Paridhana
    ```

2. **Optional** Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate

   ```
3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt

    ```

4. **Add Gemini API and Hugging Face API key in a .env file in the project root:**

    ```bash
    GEMINI_API_KEY=YOUR_REAL_GEMINI_API_KEY
    

    ```
5. **Make sure your background image file (e.g. bg.png) is in the same folder as app.py.**


### How to Run

1. Open a terminal in the project folder (where app.py is located).

2. Activate the virtual environment (if you created one):

    ```bash
    # Windows
    venv\Scripts\activate

    # macOS / Linux
    source venv/bin/activate
    ```
3. Install all the requirements:
    ```bash
    pip install -r requirements.txt
    ```

3. Start the Streamlit app:
    ```bash
    streamlit run app.py
    ```

4. After a few seconds you’ll see a message like:

- Local URL: http://localhost:8501

5. Open that URL in your browser.

6. To stop the app, go back to the terminal and press Ctrl + C.



## 📬 Output Screenshots
<img width="1881" height="733" alt="image" src="https://github.com/user-attachments/assets/ddcb54e6-8eb3-4325-884c-3b5a3efdfca6" />

