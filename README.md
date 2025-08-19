
# InfraOrchestrator (MVP)

InfraOrchestrator is a lightweight tool that demonstrates **infrastructure as code automation** using Terraform and AWS.  
It provisions a simple serverless stack with:

- **AWS Lambda** – backend function written in Python  
- **Amazon API Gateway (HTTP API)** – public API endpoint to invoke Lambda  
- **Amazon DynamoDB** – NoSQL database for storing items  

This is an MVP (minimum viable product) to showcase how natural-language infra prompts can be turned into Terraform configurations.

---

## 🚀 Features
- Deploy AWS Lambda automatically with Terraform  
- Connect Lambda to DynamoDB for CRUD operations  
- Expose a public API via API Gateway  
- Supports simple GET (fetch all items) and POST (insert new item) requests  

---

## 📦 Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/infraorchestrator.git
   cd infraorchestrator
````

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Deploy with Terraform:

   ```bash
   python deploy.py
   ```

---

## 🔑 Usage

Insert data into DynamoDB:

```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/ \
  -H "Content-Type: application/json" \
  -d '{"pk": "123", "name": "Test Item"}'
```

Fetch all data:

```bash
curl https://<api-id>.execute-api.us-east-1.amazonaws.com/
```

Expected response:

```json
[
  {
    "pk": "123",
    "name": "Test Item"
  }
]
```

---

## ⚠️ Notes

* This project is for **demo/learning purposes** only.
* Make sure your AWS credentials have sufficient IAM permissions.
* Clean up resources after testing to avoid unnecessary costs:

  ```bash
  terraform destroy
  ```

---

## 📌 Roadmap

* Natural language prompt → Terraform generator
* Policy & cost analysis before deployment
* Multi-cloud support (Azure, GCP)

---

✍️ Built as a starter project to showcase **autonomous infra orchestration**.

---

