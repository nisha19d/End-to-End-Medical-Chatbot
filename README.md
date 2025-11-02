# End-to-End-Medical-Chatbot

# How to run?
### STEP 01- Create a conda environment after opening the repository

```bash
conda create -n medibot python=3.10 -y
```

```bash
conda activate medibot
```

### STEP 02- install the requirements
```bash
pip install -r requirements.txt

```

### Create a '.env' file in the root directory and add your Pinecone & gemini 
credentials as follows:

```ini

PINECONE_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
GEMINI_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

```bash

# run the following command to store embeddings to pinecone
python store_index.py
```

```bash
# Finally run the following command
python app.py 
```



Now,
```bash
open up localhost:
```


### Techstack Used:

-Python
-LangChain
-Flask
-GPT
-Pinecone