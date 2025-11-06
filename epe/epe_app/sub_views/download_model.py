from sentence_transformers import SentenceTransformer

# Download the model from Hugging Face
model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

# Save it inside your project
model.save("epe_app/models/multi_qa_MiniLM_L6_cos_v1")

print("✅ Model downloaded and saved successfully!")
