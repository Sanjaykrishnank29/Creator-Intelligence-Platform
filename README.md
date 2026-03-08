# Creator Intelligence Platform

**AI-Driven Predictive Content Strategy System for Digital Creators**

<p>
  <a href="https://dqkouk8ltf860.cloudfront.net" target="_blank">
    <img src="https://img.shields.io/badge/Live_Demo-Online-2ea44f?style=for-the-badge&logo=amazon-aws" alt="Live Demo" />
  </a>
  <img src="https://img.shields.io/badge/AWS-Serverless-FF9900?style=for-the-badge&logo=amazonaws" alt="AWS Serverless" />
  <img src="https://img.shields.io/badge/Amazon-Bedrock-00A4A6?style=for-the-badge&logo=amazonaws" alt="Amazon Bedrock" />
</p>

## 🚀 Overview

The Creator Intelligence Platform is an AI-powered decision support system designed to help digital content creators plan, optimize, and evaluate content before publishing.

Instead of relying on guesswork, the platform analyzes:
- Creator historical performance
- Real-time trend signals
- Platform-specific engagement patterns

Using this data, the system generates predictive engagement scores, personalized content ideas, and platform-optimized scripts. Unlike generic text generation tools, this system combines creator-specific data, trend signals, and predictive scoring to generate personalized content strategies.

## 🎯 Problem Statement

Digital creators often struggle with:
- Choosing the right content ideas
- Understanding changing platform algorithms
- Adapting content across multiple platforms
- Predicting content performance before publishing

Most AI tools generate generic content but do not analyze creator-specific data or trends. This project solves that problem by combining creator analytics + trend intelligence + AI reasoning.

## � Key Features

### 1️⃣ Predictive Content Scoring
Analyzes creator content topics, historical engagement patterns, and current trend signals to generate an out-of-100 predicted engagement score before publishing. This helps creators evaluate content potential early.

### 2️⃣ AI Content Ideation Engine
The system generates personalized content ideas using global trends, creator niche, and past successful content.

### 3️⃣ Platform-Optimized Content Generation
One content idea can be automatically transformed into YouTube video scripts, Instagram captions, LinkedIn posts, and X/Twitter threads. Each version adapts to platform-specific formats.

### 4️⃣ Trend Intelligence Pipeline
The system continuously collects trending signals from News APIs, social media discussions, and topic popularity signals. These signals influence the idea generation engine.

### 5️⃣ Creator Performance Dashboard
Creators can monitor view velocity, engagement patterns, trend alignment, and content success history.

### 6️⃣ Creator Engine (Canvas)
A visual content workflow interface that allows creators to transform raw ideas into structured scripts and adapt them across multiple platforms.

## 🏗️ System Architecture

The platform is built using a serverless AWS architecture designed for scalability and low operational cost.

### Frontend Layer
- **Amazon S3** – static web hosting
- **Amazon CloudFront** – global content delivery

### API Layer
- **Amazon API Gateway** – API routing

### Compute Layer
- **AWS Lambda** – serverless business logic
- Multiple AWS Lambda functions handling independent tasks such as ideation, prediction, content enhancement, and trend ingestion.
  - `idea_generator`
  - `prediction_api`
  - `trend_collector`
  - `feedback_ingest`
  - `content_enhancer`

### Database Layer
- **Amazon DynamoDB**
- Tables used:
  - `CreatorProfiles`
  - `CreatorContentHistory`
  - `TrendSignals`
  - `PredictionCache`

### AI Layer
- **Amazon Bedrock**
- Models used: **Amazon Nova Lite**
- The model is used for: idea generation, engagement prediction reasoning, script creation.
> *Nova Lite was selected due to its low latency and cost efficiency for text synthesis tasks such as idea generation and script structuring.*

## 📊 Data Pipeline

### Trend Intelligence Pipeline
**Data sources:** News API, Google Trends, Social media signals
**Pipeline flow:**
`Trend Sources → Lambda Collector → S3 Raw Trend Storage → Processing (SageMaker) → DynamoDB TrendSignals`

### Creator History Pipeline
**Pipeline flow:**
`Creator APIs → Lambda Sync → DynamoDB CreatorContent → S3 Dataset`

This historical data is used for personalized AI predictions.
> *Note: For the hackathon prototype, historical synchronization currently uses seed data from the TechWithTim channel to ensure stable API quotas during evaluation.*

## ⚙️ AI Workflow

Content generation workflow:
> `Creator Input → Idea Generator (Bedrock) → Content Enhancer → Prediction Engine → Trend Alignment → Final Recommendation`

The AI layer performs real reasoning tasks instead of simple text generation.

## � Cost Optimization Strategy

The system includes multiple safeguards to reduce LLM cost.

### DynamoDB Response Cache
LLM responses are cached using SHA-256 input hashing.

**Workflow:**
`Request → Check DynamoDB Cache → If Hit → return cached response | If Miss → call Bedrock`

**Benefits:** reduces repeated model calls, reduces Bedrock cost, improves response speed.

### Lightweight Heuristic Matching
To reduce cost during the hackathon prototype phase, semantic similarity matching was implemented using a lightweight keyword overlap heuristic instead of embedding-based vector search.

## ☁️ AWS Services Used

| Service | Purpose |
| :--- | :--- |
| **Amazon S3** | Static hosting & dataset storage |
| **CloudFront** | CDN for frontend |
| **Amazon API Gateway** | API management |
| **AWS Lambda** | Serverless compute |
| **Amazon DynamoDB** | NoSQL database |
| **Amazon Bedrock** | AI model inference |
| **Amazon SageMaker** | Trend signal processing |
| **Amazon EventBridge** | Scheduled pipelines |

## 🧪 Prototype Scope

The prototype demonstrates the core user flow of the Creator Intelligence system:
1. Creator provides a content idea
2. AI generates a structured script
3. AI predicts engagement score
4. Trend signals are incorporated
5. Content is adapted for multiple platforms

## 🌐 Live Prototype

**Live demo:** [https://dqkouk8ltf860.cloudfront.net](https://dqkouk8ltf860.cloudfront.net)

## 🧑‍💻 Running the Project

**1️⃣ Clone the repository**
```bash
git clone https://github.com/Sanjaykrishnank29/Creator-Intelligence-Platform.git
cd Creator-Intelligence-Platform
```

**2️⃣ Configure AWS credentials**
```bash
aws configure
```

**3️⃣ Deploy infrastructure**
```bash
cd infra
terraform init
terraform apply
```

**4️⃣ Start frontend locally**
```bash
cd ..
npm install
npm run dev
```
*(Optionally deploy static files to S3 and enable CloudFront distribution).*

## 🔮 Future Roadmap

Future improvements include:
- Real-time algorithm change detection
- Deeper creator behavior modeling
- Multi-agent AI strategy engine
- Automated publishing recommendations

## ❤️ Built For

**AI for Bharat Hackathon**  
**Track:** AI for Media, Content & Digital Experiences  

*The repository is structured to simplify evaluation and demonstrate architectural clarity for the hackathon judges.*
