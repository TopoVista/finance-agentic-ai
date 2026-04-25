# Finora — Full Stack Migration Report
## MERN → FastAPI + Next.js + LangChain + LangGraph + RAG

**Project:** Advanced-MERN-AI-Financial-SaaS-Platform (Finora)  
**Source Repo:** https://github.com/TechWithEmmaYT/Advanced-MERN-AI-Financial-SaaS-Platform  
**Target Stack:** FastAPI (Python) · Next.js 14 App Router · LangChain · LangGraph · RAG (Retrieval-Augmented Generation)  
**Report Date:** April 2026

---

## Table of Contents

1. [Project Overview & Current Stack Audit](#1-project-overview--current-stack-audit)
2. [Target Stack Architecture](#2-target-stack-architecture)
3. [Directory Structure Transformation](#3-directory-structure-transformation)
4. [Conversion 1 — Backend Runtime (Node/Express → FastAPI)](#4-conversion-1--backend-runtime-nodejsexpress--fastapi)
5. [Conversion 2 — Authentication (Passport.js + JWT → FastAPI + python-jose)](#5-conversion-2--authentication-passportjs--jwt--fastapi--python-jose)
6. [Conversion 3 — Database Layer (Mongoose → Motor + Beanie ODM)](#6-conversion-3--database-layer-mongoose--motor--beanie-odm)
7. [Conversion 4 — Frontend Runtime (Vite React SPA → Next.js 14 App Router)](#7-conversion-4--frontend-runtime-vite-react-spa--nextjs-14-app-router)
8. [Conversion 5 — API Communication (Axios REST → Next.js Server Actions + fetch)](#8-conversion-5--api-communication-axios-rest--nextjs-server-actions--fetch)
9. [Conversion 6 — AI Receipt Scanning (Google Gemini Direct → LangChain Vision Chain)](#9-conversion-6--ai-receipt-scanning-google-gemini-direct--langchain-vision-chain)
10. [Conversion 7 — AI Monthly Report (Nodemailer + Gemini → LangGraph Report Agent)](#10-conversion-7--ai-monthly-report-nodemailer--gemini--langgraph-report-agent)
11. [Conversion 8 — RAG Layer (New — Financial Knowledge Base)](#11-conversion-8--rag-layer-new--financial-knowledge-base)
12. [Conversion 9 — Analytics Pipeline (MongoDB Aggregate → FastAPI + Pandas + LangChain)](#12-conversion-9--analytics-pipeline-mongodb-aggregate--fastapi--pandas--langchain)
13. [Conversion 10 — Cron Jobs (node-cron → APScheduler / Celery Beat)](#13-conversion-10--cron-jobs-node-cron--apscheduler--celery-beat)
14. [Conversion 11 — CSV Import (multer + papaparse → FastAPI UploadFile + pandas)](#14-conversion-11--csv-import-multer--papaparse--fastapi-uploadfile--pandas)
15. [Conversion 12 — File & Profile Photo Upload (Cloudinary SDK → Cloudinary Python SDK)](#15-conversion-12--file--profile-photo-upload-cloudinary-sdk--cloudinary-python-sdk)
16. [Conversion 13 — Email Service (Nodemailer → FastAPI-Mail / SendGrid)](#16-conversion-13--email-service-nodemailer--fastapi-mail--sendgrid)
17. [Conversion 14 — Environment & Config (dotenv/Node → pydantic-settings)](#17-conversion-14--environment--config-dotenvnode--pydantic-settings)
18. [Conversion 15 — Routing & Middleware (Express Router → FastAPI APIRouter)](#18-conversion-15--routing--middleware-express-router--fastapi-apirouter)
19. [Conversion 16 — TypeScript Types → Python Pydantic Models](#19-conversion-16--typescript-types--python-pydantic-models)
20. [Conversion 17 — State Management (React Query + Zustand → TanStack Query + Zustand in Next.js)](#20-conversion-17--state-management-react-query--zustand--tanstack-query--zustand-in-nextjs)
21. [New LangGraph Agent Workflows](#21-new-langgraph-agent-workflows)
22. [Dependency Mapping — Complete Before/After](#22-dependency-mapping--complete-beforeafter)
23. [Environment Variables — Complete Before/After](#23-environment-variables--complete-beforeafter)
24. [Migration Execution Checklist](#24-migration-execution-checklist)
25. [Risk & Gotchas](#25-risk--gotchas)

---

## 1. Project Overview & Current Stack Audit

### What Finora Does

Finora is a full-featured AI-powered personal finance SaaS with:

- JWT-based email/password authentication
- Transaction CRUD (create, edit, bulk delete, duplicate)
- AI receipt scanning via Google Gemini Vision
- Advanced analytics (MongoDB aggregate pipelines) — line charts, pie charts
- Date-range filtering (last 30 days, etc.)
- Recurring transactions managed by cron jobs
- Auto-generated monthly financial reports emailed to users
- CSV transaction import
- Cloudinary profile photo upload
- Pagination, search, filter

### Current Stack (MERN)

| Layer | Technology |
|---|---|
| Runtime | Node.js 20 |
| Backend Framework | Express.js |
| Language | TypeScript (both ends) |
| Database | MongoDB + Mongoose ODM |
| Auth | Passport.js local strategy + JWT (jsonwebtoken) |
| AI | Google Gemini 1.5 Flash (direct SDK call) |
| Frontend | React 18 + Vite |
| Routing | React Router v6 |
| Data Fetching | Axios + TanStack React Query |
| State | Zustand |
| Styling | Tailwind CSS + shadcn/ui |
| Charts | Recharts |
| Scheduling | node-cron |
| Email | Nodemailer |
| File Upload | multer (server) + Cloudinary SDK |
| CSV | papaparse |

### Backend Source Tree (inferred from repo)

```
backend/
  src/
    @types/
      index.d.ts          # Express.User augmentation
      analytics.type.ts   # analytics shapes
    config/
      database.ts         # mongoose.connect()
      passport.ts         # Passport local strategy
    controllers/
      auth.controller.ts
      transaction.controller.ts
      analytics.controller.ts
      report.controller.ts
    middlewares/
      auth.middleware.ts  # JWT verify middleware
      upload.middleware.ts # multer config
    models/
      user.model.ts
      transaction.model.ts
    routes/
      auth.route.ts
      transaction.route.ts
      analytics.route.ts
    services/
      ai.service.ts       # Gemini receipt scanning
      report.service.ts   # monthly report generation
      email.service.ts    # Nodemailer
      cron.service.ts     # node-cron recurring transactions
    utils/
      helper.ts
    index.ts              # Express app entry
  package.json
  tsconfig.json
```

### Frontend Source Tree (inferred from repo)

```
client/
  src/
    pages/
      auth/
        _component/signin-form.tsx
        _component/signup-form.tsx
      dashboard/
      transactions/
      analytics/
    components/         # shadcn/ui + custom components
    hooks/              # React Query hooks
    store/              # Zustand stores
    lib/                # axios instance, utils
    types/
  package.json (Vite)
  tailwind.config.ts
```

---

## 2. Target Stack Architecture

### New Stack Summary

| Layer | Old | New |
|---|---|---|
| Backend Framework | Express.js (Node) | **FastAPI** (Python 3.11) |
| ODM/ORM | Mongoose | **Motor (async) + Beanie** |
| Auth | Passport.js + jsonwebtoken | **python-jose + passlib** |
| AI Orchestration | Direct Gemini SDK call | **LangChain** (chains + tools) |
| AI Agents / Workflows | None | **LangGraph** stateful agents |
| Knowledge Retrieval | None | **LangChain RAG** (Chroma or MongoDB Atlas Vector Search) |
| Frontend | Vite React SPA | **Next.js 14 App Router** |
| Data Fetching | Axios | **Next.js Server Actions + fetch** |
| Scheduling | node-cron | **APScheduler** (in-process) or Celery Beat |
| Email | Nodemailer | **FastAPI-Mail** (async) |
| Config | dotenv | **pydantic-settings** |
| CSV Parsing | papaparse | **pandas** |
| Task Queue (optional) | — | **Redis + Celery** (for report generation) |

### High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    Next.js 14 (App Router)               │
│   /app/dashboard   /app/transactions   /app/analytics    │
│   Server Components + Server Actions + Client Components │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP / Server Actions
┌────────────────────▼─────────────────────────────────────┐
│                  FastAPI  (Python 3.11)                   │
│  /api/auth   /api/transactions   /api/analytics          │
│  /api/ai     /api/reports        /api/rag/chat           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │            LangChain + LangGraph Layer           │    │
│  │  ReceiptChain  │  ReportAgent  │  FinanceRAG     │    │
│  └──────────────────────────────────────────────────┘    │
└────────┬──────────────────┬────────────────┬─────────────┘
         │                  │                │
    ┌────▼────┐       ┌──────▼──────┐  ┌────▼──────────┐
    │ MongoDB │       │  Chroma /   │  │  Cloudinary   │
    │  Atlas  │       │ Atlas Vec.  │  │  (files/imgs) │
    └─────────┘       └─────────────┘  └───────────────┘
```

---

## 3. Directory Structure Transformation

### Old Structure → New Structure

```
Old (MERN)                          New (FastAPI + Next.js)
─────────────────────────────────   ──────────────────────────────────────
root/
  backend/                          api/                        ← FastAPI app
    src/
      config/database.ts              core/database.py
      config/passport.ts              core/security.py
      models/user.model.ts            models/user.py
      models/transaction.model.ts     models/transaction.py
      controllers/auth.*              routers/auth.py
      controllers/transaction.*       routers/transactions.py
      controllers/analytics.*         routers/analytics.py
      services/ai.service.ts          services/ai/receipt_chain.py
      services/report.service.ts      services/ai/report_agent.py
      services/email.service.ts       services/email.py
      services/cron.service.ts        services/scheduler.py
      middlewares/auth.*              dependencies/auth.py
      middlewares/upload.*            dependencies/upload.py
      index.ts                        main.py
      package.json                    requirements.txt
                                      
                                    rag/                        ← NEW
                                      ingest.py
                                      retriever.py
                                      chains/finance_qa.py
                                      
  client/                           web/                        ← Next.js 14
    src/
      pages/auth/                     app/(auth)/login/page.tsx
                                      app/(auth)/register/page.tsx
      pages/dashboard/                app/(dashboard)/page.tsx
      pages/transactions/             app/(dashboard)/transactions/page.tsx
      pages/analytics/                app/(dashboard)/analytics/page.tsx
      components/                     components/
      hooks/                          hooks/
      store/                          store/
      lib/axios.ts                    lib/api.ts (server actions)
      package.json (Vite)             package.json (Next.js)
      vite.config.ts                  next.config.ts
```

---

## 4. Conversion 1 — Backend Runtime (Node.js/Express → FastAPI)

### What Changes

The entire `backend/src/index.ts` Express application entry point is replaced by a FastAPI `main.py`.

### Old: `backend/src/index.ts`

```typescript
import express from "express";
import cors from "cors";
import passport from "passport";
import cookieParser from "cookie-parser";
import "./config/passport";
import connectDatabase from "./config/database";
import authRoutes from "./routes/auth.route";
import transactionRoutes from "./routes/transaction.route";
import analyticsRoutes from "./routes/analytics.route";

const app = express();
app.use(cors({ origin: process.env.CLIENT_URL, credentials: true }));
app.use(express.json());
app.use(cookieParser());
app.use(passport.initialize());

app.use("/api/auth", authRoutes);
app.use("/api/transactions", transactionRoutes);
app.use("/api/analytics", analyticsRoutes);

connectDatabase().then(() => {
  app.listen(5000, () => console.log("Server running on port 5000"));
});
```

### New: `api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import connect_db, disconnect_db
from routers import auth, transactions, analytics, ai, reports, rag

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()

app = FastAPI(title="Finora API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
```

### Key Differences

- FastAPI uses Python type hints and Pydantic for automatic request validation (replaces Zod/express-validator).
- Lifespan context manager replaces manual `connectDatabase().then(app.listen())`.
- All route handlers become `async def` with automatic OpenAPI docs at `/docs`.
- CORS middleware is built-in — no separate `cors` npm package.

---

## 5. Conversion 2 — Authentication (Passport.js + JWT → FastAPI + python-jose)

### Old Pattern

Express uses Passport.js local strategy. JWT is signed with `jsonwebtoken` and sent back in a cookie.

**`backend/src/config/passport.ts`** (inferred):
```typescript
passport.use(new LocalStrategy({ usernameField: "email" }, async (email, password, done) => {
  const user = await UserModel.findOne({ email });
  if (!user || !bcrypt.compareSync(password, user.password)) return done(null, false);
  return done(null, user);
}));
```

**`backend/src/middlewares/auth.middleware.ts`** (inferred):
```typescript
export const protect = (req, res, next) => {
  const token = req.cookies.token || req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ message: "Unauthorized" });
  const decoded = jwt.verify(token, process.env.JWT_SECRET!);
  req.user = decoded;
  next();
};
```

### New: `api/core/security.py`

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Cookie
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(days=7)
    return jwt.encode({**data, "exp": expire}, settings.JWT_SECRET, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserDocument:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await UserDocument.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### New: `api/routers/auth.py`

```python
from fastapi import APIRouter, HTTPException, Response
from schemas.auth import LoginInput, RegisterInput
from core.security import verify_password, hash_password, create_access_token
from models.user import UserDocument

router = APIRouter()

@router.post("/register")
async def register(data: RegisterInput, response: Response):
    if await UserDocument.find_one(UserDocument.email == data.email):
        raise HTTPException(400, "Email already in use")
    user = UserDocument(email=data.email, password=hash_password(data.password), name=data.name)
    await user.insert()
    token = create_access_token({"sub": str(user.id)})
    response.set_cookie("token", token, httponly=True, samesite="lax")
    return {"user": user.model_dump(exclude={"password"})}

@router.post("/login")
async def login(data: LoginInput, response: Response):
    user = await UserDocument.find_one(UserDocument.email == data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    response.set_cookie("token", token, httponly=True, samesite="lax")
    return {"user": user.model_dump(exclude={"password"})}
```

---

## 6. Conversion 3 — Database Layer (Mongoose → Motor + Beanie ODM)

### Old: Mongoose Model

```typescript
// backend/src/models/transaction.model.ts
import mongoose, { Schema, Document } from "mongoose";

export interface ITransaction extends Document {
  userId: mongoose.Types.ObjectId;
  type: "income" | "expense";
  amount: number;
  category: string;
  description: string;
  date: Date;
  isRecurring: boolean;
  recurringInterval?: "daily" | "weekly" | "monthly";
  receiptUrl?: string;
}

const TransactionSchema = new Schema<ITransaction>({
  userId: { type: Schema.Types.ObjectId, ref: "User", required: true },
  type: { type: String, enum: ["income", "expense"], required: true },
  amount: { type: Number, required: true },
  category: { type: String, required: true },
  description: String,
  date: { type: Date, default: Date.now },
  isRecurring: { type: Boolean, default: false },
  recurringInterval: String,
  receiptUrl: String,
}, { timestamps: true });

export const Transaction = mongoose.model<ITransaction>("Transaction", TransactionSchema);
```

### New: Beanie Document

```python
# api/models/transaction.py
from beanie import Document, Indexed, Link
from pydantic import Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

class Transaction(Document):
    user_id: Indexed(str)
    type: Literal["income", "expense"]
    amount: float
    category: str
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    is_recurring: bool = False
    recurring_interval: Optional[Literal["daily", "weekly", "monthly"]] = None
    receipt_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "transactions"
        indexes = ["user_id", "date", "type", "category"]
```

### Database Connection

```python
# api/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.user import User
from models.transaction import Transaction

async def connect_db():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[User, Transaction]
    )

async def disconnect_db():
    # Motor client cleanup handled by GC; optionally close explicitly
    pass
```

---

## 7. Conversion 4 — Frontend Runtime (Vite React SPA → Next.js 14 App Router)

### Old: `client/vite.config.ts`

Vite builds a pure SPA. All routing is client-side via React Router v6. All pages are loaded from a single `index.html`. There is no SSR.

### New: Next.js 14 App Router

All pages inside `web/app/` become Server Components by default. Client interactivity uses the `"use client"` directive.

#### Route Mapping

| Old React Router Route | New Next.js App Router Path |
|---|---|
| `/` (redirect) | `app/page.tsx` → redirect to `/dashboard` |
| `/auth/sign-in` | `app/(auth)/login/page.tsx` |
| `/auth/sign-up` | `app/(auth)/register/page.tsx` |
| `/dashboard` | `app/(dashboard)/page.tsx` |
| `/transactions` | `app/(dashboard)/transactions/page.tsx` |
| `/analytics` | `app/(dashboard)/analytics/page.tsx` |
| `/settings` | `app/(dashboard)/settings/page.tsx` |

#### Old: `client/src/App.tsx` (inferred)

```tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/auth/sign-in" element={<SignIn />} />
        <Route path="/auth/sign-up" element={<SignUp />} />
        <Route element={<ProtectedLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/analytics" element={<Analytics />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

#### New: `web/app/layout.tsx`

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/components/providers";

export const metadata: Metadata = { title: "Finora", description: "AI Finance SaaS" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

#### New: `web/app/(auth)/login/page.tsx`

```tsx
import { SignInForm } from "@/components/auth/signin-form";

// This is a Server Component — no "use client" needed at this level
export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <SignInForm />
    </main>
  );
}
```

The `SignInForm` itself uses `"use client"` because it handles form state.

#### Protected Layout via Middleware

```typescript
// web/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("token");
  const isAuth = !!token;
  const isAuthPage = request.nextUrl.pathname.startsWith("/login") || 
                     request.nextUrl.pathname.startsWith("/register");

  if (!isAuth && !isAuthPage) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  if (isAuth && isAuthPage) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }
  return NextResponse.next();
}

export const config = { matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"] };
```

---

## 8. Conversion 5 — API Communication (Axios REST → Next.js Server Actions + fetch)

### Old Pattern

The client uses a configured Axios instance pointing at `http://localhost:5000`.

```typescript
// client/src/lib/axios.ts
import axios from "axios";
export const api = axios.create({
  baseURL: process.env.VITE_API_URL,
  withCredentials: true,
});
```

React Query hooks wrap these calls:
```typescript
// client/src/hooks/use-transactions.ts
export const useTransactions = (params) =>
  useQuery({ queryKey: ["transactions", params], queryFn: () => api.get("/api/transactions", { params }) });
```

### New Pattern — Two Approaches

#### Option A: Server Actions (for mutations)

```typescript
// web/app/(dashboard)/transactions/actions.ts
"use server";
import { cookies } from "next/headers";

export async function createTransaction(formData: FormData) {
  const token = cookies().get("token")?.value;
  const res = await fetch(`${process.env.FASTAPI_URL}/api/transactions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(Object.fromEntries(formData)),
  });
  return res.json();
}
```

#### Option B: TanStack Query + client-side fetch (for lists/reads)

```typescript
// web/hooks/use-transactions.ts
"use client";
import { useQuery } from "@tanstack/react-query";
import { fetchTransactions } from "@/lib/api";

export const useTransactions = (params: TransactionParams) =>
  useQuery({
    queryKey: ["transactions", params],
    queryFn: () => fetchTransactions(params),
  });
```

```typescript
// web/lib/api.ts
export async function fetchTransactions(params: TransactionParams) {
  const qs = new URLSearchParams(params as any).toString();
  const res = await fetch(`/api/proxy/transactions?${qs}`, { credentials: "include" });
  if (!res.ok) throw new Error("Failed to fetch transactions");
  return res.json();
}
```

A Next.js route handler at `web/app/api/proxy/[...path]/route.ts` proxies requests to FastAPI with cookie forwarding — so the browser never directly calls FastAPI (better security posture).

---

## 9. Conversion 6 — AI Receipt Scanning (Google Gemini Direct → LangChain Vision Chain)

### Old: Direct Gemini SDK Call

```typescript
// backend/src/services/ai.service.ts (inferred)
import { GoogleGenerativeAI } from "@google/generative-ai";
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

export async function scanReceipt(imageBase64: string) {
  const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
  const result = await model.generateContent([
    "Extract the following from this receipt: amount, date, category, merchant. Return as JSON.",
    { inlineData: { data: imageBase64, mimeType: "image/jpeg" } }
  ]);
  return JSON.parse(result.response.text());
}
```

### New: LangChain Vision Chain

```python
# api/services/ai/receipt_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Optional

class ReceiptData(BaseModel):
    amount: float
    date: str
    category: str
    merchant: str
    description: Optional[str] = None
    currency: str = "USD"

RECEIPT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a financial receipt analyzer. Extract structured data and return ONLY valid JSON."),
    ("human", [
        {"type": "text", "text": "Extract: amount, date, category, merchant, description, currency from this receipt."},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,{image_base64}"}},
    ]),
])

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
parser = JsonOutputParser(pydantic_object=ReceiptData)

receipt_chain = RECEIPT_PROMPT | llm | parser

async def scan_receipt(image_base64: str) -> ReceiptData:
    return await receipt_chain.ainvoke({"image_base64": image_base64})
```

### New: FastAPI Route

```python
# api/routers/ai.py
from fastapi import APIRouter, UploadFile, File, Depends
from services.ai.receipt_chain import scan_receipt
from dependencies.auth import get_current_user
import base64

router = APIRouter()

@router.post("/scan-receipt")
async def scan_receipt_endpoint(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    image_bytes = await file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    receipt_data = await scan_receipt(image_base64)
    return {"receipt": receipt_data}
```

**Why LangChain?** The chain is now composable — you can add retry logic, output validation, fallback models, and streaming with zero Express middleware boilerplate.

---

## 10. Conversion 7 — AI Monthly Report (Nodemailer + Gemini → LangGraph Report Agent)

### Old: Procedural Report Generation

The old codebase presumably calls Gemini to summarize transactions, then sends the result via Nodemailer in a cron job callback.

```typescript
// backend/src/services/report.service.ts (inferred)
export async function generateMonthlyReport(userId: string) {
  const transactions = await Transaction.find({ userId, /* last month */ });
  const summary = await gemini.generate(`Summarize these transactions: ${JSON.stringify(transactions)}`);
  await emailService.send(user.email, "Your Monthly Report", summary);
}
```

### New: LangGraph Report Agent

LangGraph models this as a stateful multi-step agent graph with explicit nodes, making the flow auditable and extensible.

```python
# api/services/ai/report_agent.py
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, List
from models.transaction import Transaction
from services.email import send_email

class ReportState(TypedDict):
    user_id: str
    user_email: str
    transactions: List[dict]
    summary: str
    insights: str
    recommendations: str
    email_sent: bool

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

async def fetch_transactions_node(state: ReportState) -> ReportState:
    """Node 1: Fetch last month's transactions from MongoDB."""
    from datetime import datetime, timedelta
    last_month = datetime.utcnow() - timedelta(days=30)
    txns = await Transaction.find(
        Transaction.user_id == state["user_id"],
        Transaction.date >= last_month
    ).to_list()
    state["transactions"] = [t.model_dump() for t in txns]
    return state

async def generate_summary_node(state: ReportState) -> ReportState:
    """Node 2: Generate financial summary."""
    txns_text = "\n".join([f"{t['type']}: {t['amount']} - {t['category']}" for t in state["transactions"]])
    response = await llm.ainvoke(f"Summarize these transactions in 3 sentences:\n{txns_text}")
    state["summary"] = response.content
    return state

async def generate_insights_node(state: ReportState) -> ReportState:
    """Node 3: Generate spending insights."""
    response = await llm.ainvoke(
        f"Based on this summary, give 3 key financial insights:\n{state['summary']}"
    )
    state["insights"] = response.content
    return state

async def generate_recommendations_node(state: ReportState) -> ReportState:
    """Node 4: Generate action recommendations."""
    response = await llm.ainvoke(
        f"Given these insights, give 3 actionable recommendations:\n{state['insights']}"
    )
    state["recommendations"] = response.content
    return state

async def send_email_node(state: ReportState) -> ReportState:
    """Node 5: Send report email."""
    body = f"""
    Monthly Financial Report
    
    Summary: {state['summary']}
    
    Key Insights:
    {state['insights']}
    
    Recommendations:
    {state['recommendations']}
    """
    await send_email(state["user_email"], "Your Monthly Finora Report", body)
    state["email_sent"] = True
    return state

# Build the graph
graph = StateGraph(ReportState)
graph.add_node("fetch_transactions", fetch_transactions_node)
graph.add_node("generate_summary", generate_summary_node)
graph.add_node("generate_insights", generate_insights_node)
graph.add_node("generate_recommendations", generate_recommendations_node)
graph.add_node("send_email", send_email_node)

graph.set_entry_point("fetch_transactions")
graph.add_edge("fetch_transactions", "generate_summary")
graph.add_edge("generate_summary", "generate_insights")
graph.add_edge("generate_insights", "generate_recommendations")
graph.add_edge("generate_recommendations", "send_email")
graph.add_edge("send_email", END)

report_agent = graph.compile()

async def run_report_for_user(user_id: str, user_email: str):
    return await report_agent.ainvoke({"user_id": user_id, "user_email": user_email})
```

---

## 11. Conversion 8 — RAG Layer (New — Financial Knowledge Base)

This is a **net-new capability** not present in the original MERN project. It adds a `/api/rag/chat` endpoint where users can ask questions about their finances and get AI answers grounded in their actual transaction data.

### Architecture

```
User Question → Retriever (Chroma/Atlas Vector) → Context Docs → LangChain QA Chain → Answer
                     ↑
          MongoDB Transactions (embedded as vectors at insert time)
```

### Ingestion Pipeline

```python
# api/rag/ingest.py
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from models.transaction import Transaction

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

async def ingest_user_transactions(user_id: str):
    """Convert transactions to vector embeddings and store in Chroma."""
    transactions = await Transaction.find(Transaction.user_id == user_id).to_list()
    
    docs = [
        LCDocument(
            page_content=f"{t.type} of ${t.amount} for {t.category} on {t.date.strftime('%Y-%m-%d')}: {t.description or ''}",
            metadata={"user_id": user_id, "transaction_id": str(t.id), "type": t.type, "amount": t.amount}
        )
        for t in transactions
    ]
    
    vectorstore = Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=embeddings,
        persist_directory=f"./chroma_db/{user_id}"
    )
    vectorstore.add_documents(docs)
    vectorstore.persist()
```

### RAG QA Chain

```python
# api/rag/chains/finance_qa.py
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

FINANCE_PROMPT = PromptTemplate.from_template("""
You are Finora, an AI financial advisor. Answer the user's question using ONLY their transaction data below.
Be specific with numbers. If you don't know, say so.

Context (user's transactions):
{context}

Question: {question}
Answer:
""")

def get_rag_chain(user_id: str):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=embeddings,
        persist_directory=f"./chroma_db/{user_id}"
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
    
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": FINANCE_PROMPT},
        return_source_documents=True
    )
```

### RAG Router

```python
# api/routers/rag.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from rag.chains.finance_qa import get_rag_chain
from dependencies.auth import get_current_user

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
async def rag_chat(request: ChatRequest, current_user=Depends(get_current_user)):
    chain = get_rag_chain(str(current_user.id))
    result = await chain.ainvoke({"query": request.question})
    return {
        "answer": result["result"],
        "sources": [doc.metadata for doc in result.get("source_documents", [])]
    }
```

### Frontend RAG Chat Component

```tsx
// web/components/rag/finance-chat.tsx
"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

export function FinanceChat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);

  async function askQuestion() {
    const res = await fetch("/api/proxy/rag/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      credentials: "include",
    });
    const data = await res.json();
    setMessages(prev => [
      ...prev,
      { role: "user", content: question },
      { role: "assistant", content: data.answer },
    ]);
    setQuestion("");
  }

  return (
    <div className="flex flex-col gap-4 p-4 border rounded-xl">
      <h3 className="font-semibold">Ask Finora AI</h3>
      <div className="flex flex-col gap-2 min-h-40">
        {messages.map((m, i) => (
          <div key={i} className={`p-2 rounded ${m.role === "user" ? "bg-blue-50 self-end" : "bg-gray-50"}`}>
            {m.content}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="How much did I spend on food last month?"
          className="flex-1 border rounded px-3 py-2"
        />
        <button onClick={askQuestion} className="bg-blue-600 text-white px-4 py-2 rounded">
          Ask
        </button>
      </div>
    </div>
  );
}
```

---

## 12. Conversion 9 — Analytics Pipeline (MongoDB Aggregate → FastAPI + Pandas + LangChain)

### Old: Mongoose Aggregate Pipelines

```typescript
// backend/src/controllers/analytics.controller.ts (inferred)
export const getExpensesBreakdown = async (req, res) => {
  const data = await Transaction.aggregate([
    { $match: { userId: new ObjectId(req.user._id), type: "expense", date: { $gte: startDate } } },
    { $group: { _id: "$category", total: { $sum: "$amount" } } },
    { $sort: { total: -1 } }
  ]);
  res.json(data);
};
```

### New: FastAPI + Motor Aggregation (kept similar for performance)

```python
# api/routers/analytics.py
from fastapi import APIRouter, Depends, Query
from core.database import get_db
from dependencies.auth import get_current_user
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter()

@router.get("/expenses-breakdown")
async def expenses_breakdown(
    days: int = Query(30),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    start_date = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {
            "user_id": str(current_user.id),
            "type": "expense",
            "date": {"$gte": start_date}
        }},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1}}
    ]
    collection = db["transactions"]
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=100)
    return [{"category": r["_id"], "total": r["total"]} for r in results]
```

**Note:** MongoDB aggregation pipelines are kept as-is since they are highly performant and not LLM-dependent. The LangChain layer is added on top for the AI chat (RAG) feature.

---

## 13. Conversion 10 — Cron Jobs (node-cron → APScheduler / Celery Beat)

### Old: node-cron

```typescript
// backend/src/services/cron.service.ts (inferred)
import cron from "node-cron";

cron.schedule("0 0 * * *", async () => {
  const recurringTxns = await Transaction.find({ isRecurring: true });
  for (const txn of recurringTxns) {
    // check if due and create new transaction
  }
});

// Monthly report — 1st of every month at 8am
cron.schedule("0 8 1 * *", async () => {
  const users = await User.find({});
  for (const user of users) {
    await reportService.generateMonthlyReport(user._id);
  }
});
```

### New: APScheduler (in-process, simpler)

```python
# api/services/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

async def process_recurring_transactions():
    from models.transaction import Transaction
    from datetime import datetime
    recurring = await Transaction.find(Transaction.is_recurring == True).to_list()
    for txn in recurring:
        # Check interval and create new transaction if due
        pass

async def send_monthly_reports():
    from models.user import User
    from services.ai.report_agent import run_report_for_user
    users = await User.find_all().to_list()
    for user in users:
        await run_report_for_user(str(user.id), user.email)

scheduler.add_job(process_recurring_transactions, CronTrigger(hour=0, minute=0))
scheduler.add_job(send_monthly_reports, CronTrigger(day=1, hour=8, minute=0))

def start_scheduler():
    scheduler.start()
```

```python
# Add to api/main.py lifespan:
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    from services.scheduler import start_scheduler
    start_scheduler()
    yield
```

---

## 14. Conversion 11 — CSV Import (multer + papaparse → FastAPI UploadFile + pandas)

### Old: Express + papaparse

```typescript
// backend/src/controllers/transaction.controller.ts (inferred)
export const importCSV = async (req, res) => {
  const file = req.file; // multer
  const csvText = file.buffer.toString("utf-8");
  const { data } = Papa.parse(csvText, { header: true, skipEmptyLines: true });
  const transactions = data.map(row => ({
    userId: req.user._id,
    type: row.type,
    amount: parseFloat(row.amount),
    category: row.category,
    date: new Date(row.date),
    description: row.description,
  }));
  await Transaction.insertMany(transactions);
  res.json({ imported: transactions.length });
};
```

### New: FastAPI + pandas

```python
# api/routers/transactions.py (CSV import endpoint)
from fastapi import UploadFile, File, Depends
import pandas as pd
import io

@router.post("/import-csv")
async def import_csv(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    
    # Normalize columns
    df.columns = df.columns.str.lower().str.strip()
    required = {"type", "amount", "category", "date"}
    if not required.issubset(df.columns):
        raise HTTPException(400, f"CSV must contain columns: {required}")
    
    transactions = [
        Transaction(
            user_id=str(current_user.id),
            type=row["type"],
            amount=float(row["amount"]),
            category=row["category"],
            date=pd.to_datetime(row["date"]).to_pydatetime(),
            description=row.get("description", ""),
        )
        for _, row in df.iterrows()
    ]
    
    await Transaction.insert_many(transactions)
    
    # Re-ingest into RAG vector store after import
    from rag.ingest import ingest_user_transactions
    await ingest_user_transactions(str(current_user.id))
    
    return {"imported": len(transactions)}
```

---

## 15. Conversion 12 — File & Profile Photo Upload (Cloudinary SDK → Cloudinary Python SDK)

### Old: Cloudinary Node SDK + multer

```typescript
import cloudinary from "cloudinary";
cloudinary.v2.config({ cloud_name: process.env.CLOUDINARY_NAME, ... });

export const uploadToCloudinary = async (buffer: Buffer): Promise<string> => {
  return new Promise((resolve, reject) => {
    const stream = cloudinary.v2.uploader.upload_stream({ folder: "finora" }, (err, result) => {
      if (err) reject(err);
      else resolve(result!.secure_url);
    });
    stream.end(buffer);
  });
};
```

### New: Cloudinary Python SDK

```python
# api/services/cloudinary_service.py
import cloudinary
import cloudinary.uploader
from core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

async def upload_image(file_bytes: bytes, folder: str = "finora") -> str:
    import asyncio
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: cloudinary.uploader.upload(file_bytes, folder=folder)
    )
    return result["secure_url"]
```

```python
# Usage in router
@router.patch("/profile/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    contents = await file.read()
    url = await upload_image(contents, folder="finora/profiles")
    current_user.profile_photo = url
    await current_user.save()
    return {"photo_url": url}
```

---

## 16. Conversion 13 — Email Service (Nodemailer → FastAPI-Mail / SendGrid)

### Old: Nodemailer

```typescript
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: 587,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
});

export async function sendEmail(to: string, subject: string, html: string) {
  await transporter.sendMail({ from: '"Finora" <no-reply@finora.app>', to, subject, html });
}
```

### New: FastAPI-Mail

```python
# api/services/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASS,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

mail = FastMail(conf)

async def send_email(to: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=body,
        subtype="html"
    )
    await mail.send_message(message)
```

---

## 17. Conversion 14 — Environment & Config (dotenv/Node → pydantic-settings)

### Old: `dotenv` + `process.env`

```typescript
// backend/src/index.ts
import dotenv from "dotenv";
dotenv.config();

const MONGO_URI = process.env.MONGO_URI!;
const JWT_SECRET = process.env.JWT_SECRET!;
```

### New: pydantic-settings (type-safe, validated at startup)

```python
# api/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    MONGODB_URI: str
    DB_NAME: str = "finora"
    
    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    # AI
    GOOGLE_API_KEY: str
    
    # Cloudinary
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # Email
    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str = "no-reply@finora.app"
    
    # App
    CLIENT_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

If any required variable is missing, FastAPI crashes at startup with a clear validation error — much safer than silent `undefined` in Node.js.

---

## 18. Conversion 15 — Routing & Middleware (Express Router → FastAPI APIRouter)

### Old: Express Router Pattern

```typescript
// backend/src/routes/transaction.route.ts
import { Router } from "express";
import { protect } from "../middlewares/auth.middleware";
import { getTransactions, createTransaction, deleteTransaction } from "../controllers/transaction.controller";

const router = Router();
router.use(protect);  // apply auth to all routes
router.get("/", getTransactions);
router.post("/", createTransaction);
router.delete("/:id", deleteTransaction);
export default router;
```

### New: FastAPI APIRouter with Dependencies

```python
# api/routers/transactions.py
from fastapi import APIRouter, Depends, Query, Path
from dependencies.auth import get_current_user
from models.transaction import Transaction
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from typing import Optional
from datetime import datetime

router = APIRouter(dependencies=[Depends(get_current_user)])  # auth on all routes

@router.get("/", response_model=list[TransactionResponse])
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user=Depends(get_current_user)
):
    filters = {"user_id": str(current_user.id)}
    if type: filters["type"] = type
    if category: filters["category"] = category
    if start_date or end_date:
        filters["date"] = {}
        if start_date: filters["date"]["$gte"] = start_date
        if end_date: filters["date"]["$lte"] = end_date
    
    skip = (page - 1) * limit
    txns = await Transaction.find(filters).skip(skip).limit(limit).to_list()
    return txns

@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(data: TransactionCreate, current_user=Depends(get_current_user)):
    txn = Transaction(**data.model_dump(), user_id=str(current_user.id))
    await txn.insert()
    # Trigger async RAG re-ingestion
    from rag.ingest import ingest_user_transactions
    await ingest_user_transactions(str(current_user.id))
    return txn

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str = Path(...), current_user=Depends(get_current_user)):
    txn = await Transaction.get(transaction_id)
    if not txn or txn.user_id != str(current_user.id):
        raise HTTPException(404, "Transaction not found")
    await txn.delete()
    return {"deleted": True}
```

---

## 19. Conversion 16 — TypeScript Types → Python Pydantic Models

### Old: TypeScript Interfaces / Types

```typescript
// backend/src/@types/analytics.type.ts
export interface ExpenseBreakdown {
  category: string;
  total: number;
  percentage: number;
}

export interface IncomeExpenseChart {
  month: string;
  income: number;
  expenses: number;
}
```

### New: Pydantic Schemas

```python
# api/schemas/analytics.py
from pydantic import BaseModel

class ExpenseBreakdown(BaseModel):
    category: str
    total: float
    percentage: float

class IncomeExpensePoint(BaseModel):
    month: str
    income: float
    expenses: float

class AnalyticsSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    expense_breakdown: list[ExpenseBreakdown]
    income_expense_chart: list[IncomeExpensePoint]
```

```python
# api/schemas/transaction.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TransactionCreate(BaseModel):
    type: Literal["income", "expense"]
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    is_recurring: bool = False
    recurring_interval: Optional[Literal["daily", "weekly", "monthly"]] = None

class TransactionUpdate(BaseModel):
    type: Optional[Literal["income", "expense"]] = None
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

class TransactionResponse(TransactionCreate):
    id: str
    user_id: str
    created_at: datetime
    receipt_url: Optional[str] = None
```

---

## 20. Conversion 17 — State Management (React Query + Zustand → TanStack Query + Zustand in Next.js)

The state management tools themselves **don't change** — TanStack Query (formerly React Query) and Zustand both work in Next.js. What changes is the initialization pattern.

### Old: Vite React Setup

```tsx
// client/src/main.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
const queryClient = new QueryClient();
ReactDOM.createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}><App /></QueryClientProvider>
);
```

### New: Next.js Providers Component

```tsx
// web/components/providers.tsx
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 60 * 1000 } }
  }));
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

The key difference: this must be a Client Component (`"use client"`) because QueryClientProvider uses React context. Server Components don't have access to context.

---

## 21. New LangGraph Agent Workflows

Three LangGraph agents power the new AI capabilities:

### Agent 1: Receipt Scanner Agent (already shown in Conversion 6)
Single-turn, chain-based. No graph needed for simple synchronous extraction.

### Agent 2: Monthly Report Agent (shown in Conversion 7)
5-node sequential graph: fetch → summarize → insights → recommendations → email.

### Agent 3: Financial Advisor Agent (new, extends RAG)

A conversational agent that can use tools to query the user's data:

```python
# api/services/ai/advisor_agent.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from typing import TypedDict, Annotated, List
import operator

@tool
async def get_spending_by_category(user_id: str, category: str, days: int = 30) -> str:
    """Get total spending in a category over the last N days."""
    from models.transaction import Transaction
    from datetime import datetime, timedelta
    start = datetime.utcnow() - timedelta(days=days)
    txns = await Transaction.find(
        Transaction.user_id == user_id,
        Transaction.category == category,
        Transaction.date >= start
    ).to_list()
    total = sum(t.amount for t in txns)
    return f"Spent ${total:.2f} on {category} in the last {days} days."

tools = [get_spending_by_category]
llm_with_tools = ChatGoogleGenerativeAI(model="gemini-1.5-flash").bind_tools(tools)

class AdvisorState(TypedDict):
    messages: Annotated[List, operator.add]
    user_id: str

def advisor_node(state: AdvisorState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AdvisorState):
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

graph = StateGraph(AdvisorState)
graph.add_node("advisor", advisor_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("advisor")
graph.add_conditional_edges("advisor", should_continue)
graph.add_edge("tools", "advisor")
advisor_agent = graph.compile()
```

---

## 22. Dependency Mapping — Complete Before/After

### Backend: `package.json` → `requirements.txt`

| Node Package | Python Equivalent | Purpose |
|---|---|---|
| `express` | `fastapi` | Web framework |
| `typescript` | (built-in types) | Type safety |
| `ts-node` | `uvicorn` | Dev server runner |
| `mongoose` | `beanie` + `motor` | MongoDB ODM |
| `passport` + `passport-local` | `python-jose` + `passlib` | Auth |
| `jsonwebtoken` | `python-jose[cryptography]` | JWT signing/verification |
| `bcryptjs` | `passlib[bcrypt]` | Password hashing |
| `dotenv` | `pydantic-settings` | Env variable management |
| `cors` | `fastapi[cors]` (built-in) | CORS middleware |
| `cookie-parser` | (built-in in FastAPI) | Cookie parsing |
| `multer` | `python-multipart` | File upload parsing |
| `papaparse` | `pandas` | CSV parsing |
| `nodemailer` | `fastapi-mail` | Email sending |
| `cloudinary` | `cloudinary` (Python SDK) | Image hosting |
| `node-cron` | `apscheduler` | Task scheduling |
| `@google/generative-ai` | `langchain-google-genai` | Gemini AI |
| — | `langchain` | LLM chains/tools |
| — | `langgraph` | Stateful AI agents |
| — | `langchain-community` | Community integrations |
| — | `chromadb` | Vector store for RAG |
| `zod` | `pydantic` (built-in to FastAPI) | Schema validation |

### Full `requirements.txt`

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
motor==3.6.0
beanie==1.27.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
pydantic-settings==2.6.0
fastapi-mail==1.4.1
cloudinary==1.41.0
apscheduler==3.10.4
pandas==2.2.3
langchain==0.3.0
langchain-google-genai==2.0.0
langchain-community==0.3.0
langgraph==0.2.0
chromadb==0.5.0
python-dotenv==1.0.1
httpx==0.27.0
```

### Frontend: Old `package.json` (Vite) → New `package.json` (Next.js)

| Old Package | New Package | Change |
|---|---|---|
| `react` + `react-dom` | `react` + `react-dom` | Same version (18+) |
| `vite` | `next` | **Replace** |
| `@vitejs/plugin-react` | — | Remove |
| `react-router-dom` | — | Remove (App Router handles routing) |
| `axios` | `ky` or native `fetch` | **Replace** (or keep axios) |
| `@tanstack/react-query` | `@tanstack/react-query` | Same |
| `zustand` | `zustand` | Same |
| `tailwindcss` | `tailwindcss` | Same |
| `shadcn/ui` components | `shadcn/ui` components | Same |
| `recharts` | `recharts` | Same |
| `typescript` | `typescript` | Same |
| — | `server-only` | New (for server-only modules) |

---

## 23. Environment Variables — Complete Before/After

### Old `.env` (backend)

```env
PORT=5000
MONGO_URI=mongodb+srv://...
JWT_SECRET=your_jwt_secret
CLIENT_URL=http://localhost:5173

GEMINI_API_KEY=your_gemini_key

CLOUDINARY_CLOUD_NAME=your_cloud
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret

SMTP_HOST=smtp.gmail.com
SMTP_USER=your@email.com
SMTP_PASS=your_app_password
```

### Old `.env` (client/Vite)

```env
VITE_API_URL=http://localhost:5000
```

### New `.env` (FastAPI — `api/.env`)

```env
# Database
MONGODB_URI=mongodb+srv://...
DB_NAME=finora

# Auth
JWT_SECRET=your_jwt_secret_here

# AI / LangChain
GOOGLE_API_KEY=your_gemini_key

# Cloudinary
CLOUDINARY_NAME=your_cloud
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_USER=your@email.com
SMTP_PASS=your_app_password
SMTP_FROM=no-reply@finora.app

# App
CLIENT_URL=http://localhost:3000

# RAG
CHROMA_PERSIST_DIR=./chroma_db
```

### New `.env.local` (Next.js — `web/.env.local`)

```env
FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Finora
```

Note: `FASTAPI_URL` is a server-side variable (no `NEXT_PUBLIC_` prefix) — the browser never talks to FastAPI directly; it goes through Next.js route handlers.

---

## 24. Migration Execution Checklist

Execute these steps in order. Each step is independently testable.

### Phase 1 — Scaffold New Project Structure

- [ ] Create `api/` directory (FastAPI app)
- [ ] Create `web/` directory (`npx create-next-app@latest web --typescript --tailwind --app`)
- [ ] Set up Python virtual environment (`python -m venv .venv`)
- [ ] Install all Python dependencies (`pip install -r requirements.txt`)
- [ ] Create `api/main.py` with lifespan and CORS
- [ ] Create `api/core/config.py` with pydantic-settings
- [ ] Create `api/core/database.py` with Motor + Beanie init

### Phase 2 — Data Models

- [ ] Create `api/models/user.py` (Beanie Document)
- [ ] Create `api/models/transaction.py` (Beanie Document)
- [ ] Create all Pydantic schemas in `api/schemas/`
- [ ] Run `uvicorn api.main:app --reload` and verify `/docs` loads

### Phase 3 — Authentication

- [ ] Create `api/core/security.py` (hashing + JWT)
- [ ] Create `api/dependencies/auth.py` (`get_current_user`)
- [ ] Create `api/routers/auth.py` (register + login + logout)
- [ ] Test auth flow end-to-end with curl / Postman

### Phase 4 — Core CRUD Routes

- [ ] Create `api/routers/transactions.py` (all CRUD + search + pagination + bulk delete + duplicate)
- [ ] Create `api/routers/analytics.py` (expense breakdown + income/expense chart)
- [ ] Migrate all MongoDB aggregate pipelines from TypeScript to Python Motor
- [ ] Create `api/services/cloudinary_service.py`
- [ ] Test all routes in `/docs`

### Phase 5 — Supporting Services

- [ ] Create `api/services/email.py` (FastAPI-Mail)
- [ ] Create `api/services/scheduler.py` (APScheduler recurring + monthly report)
- [ ] Create `api/routers/transactions.py` CSV import endpoint

### Phase 6 — AI Layer (LangChain)

- [ ] Create `api/services/ai/receipt_chain.py`
- [ ] Create `api/routers/ai.py` (scan-receipt endpoint)
- [ ] Test receipt scanning with a real receipt image

### Phase 7 — AI Agent Layer (LangGraph)

- [ ] Create `api/services/ai/report_agent.py` (5-node graph)
- [ ] Create `api/routers/reports.py`
- [ ] Wire report agent into APScheduler monthly cron

### Phase 8 — RAG Layer

- [ ] Create `api/rag/ingest.py` (transaction → vector embedding)
- [ ] Create `api/rag/chains/finance_qa.py` (retrieval QA chain)
- [ ] Create `api/routers/rag.py` (/chat endpoint)
- [ ] Trigger re-ingestion on every transaction create/import
- [ ] Test RAG chat with sample questions

### Phase 9 — Frontend Migration (Next.js)

- [ ] Set up App Router directory structure
- [ ] Install shadcn/ui: `npx shadcn@latest init`
- [ ] Create `web/middleware.ts` (auth protection)
- [ ] Create `web/components/providers.tsx` (TanStack Query + Zustand)
- [ ] Migrate `signin-form.tsx` and `signup-form.tsx` to Server Action pattern
- [ ] Create `web/app/api/proxy/[...path]/route.ts` (FastAPI proxy)
- [ ] Migrate Dashboard page (Server Component)
- [ ] Migrate Transactions page (Server Component + Client list)
- [ ] Migrate Analytics page (charts remain Client Components)
- [ ] Add `FinanceChat` RAG component to Dashboard
- [ ] Migrate all Zustand stores (no changes needed)
- [ ] Replace `vite.config.ts` with `next.config.ts`

### Phase 10 — Cleanup & Deploy Prep

- [ ] Remove `backend/` and `client/` directories
- [ ] Write `docker-compose.yml` (FastAPI + Next.js + MongoDB + Chroma)
- [ ] Configure production `.env` files
- [ ] Deploy FastAPI to Railway/Render/EC2
- [ ] Deploy Next.js to Vercel

---

## 25. Risk & Gotchas

### 1. Async Context in LangGraph
LangGraph's `ainvoke` must be called from an async FastAPI endpoint. Never call from sync code or APScheduler without using `asyncio.run()` in a thread.

### 2. Chroma Persistence vs. Concurrent Writes
Chroma's file-based persistence does not support concurrent writes. For production, switch to MongoDB Atlas Vector Search or a hosted Chroma instance. Set `CHROMA_PERSIST_DIR` per-user to avoid collisions.

### 3. Next.js Server Components Can't Use React Hooks
Any component using `useState`, `useEffect`, TanStack Query hooks, or Zustand must have `"use client"` at the top. Charts (Recharts) must be Client Components.

### 4. Cookie Forwarding in Proxy
The Next.js route handler proxy must forward the `Cookie` header verbatim to FastAPI, and must also forward `Set-Cookie` headers back from FastAPI to the browser — otherwise auth won't persist.

### 5. RAG Re-ingestion Cost
Every transaction insert triggers a full user re-ingestion. This is expensive at scale. Replace with incremental ingestion: add new documents only (keep a `last_ingested_at` timestamp per user).

### 6. Beanie vs. Raw Motor Aggregations
Beanie ODM does not support all MongoDB aggregation pipeline stages via its query builder. For complex analytics (group + sort + project), fall back to `await collection.aggregate(pipeline).to_list()` using Motor directly.

### 7. APScheduler in Multi-Process Deployments
APScheduler runs in-process. If FastAPI is deployed with multiple workers (`uvicorn --workers 4`), each worker runs its own scheduler and jobs execute N times. Use a Redis-backed lock or switch to Celery Beat for production.

### 8. TypeScript → Python Type Translation
MongoDB `ObjectId` becomes `str` in Beanie (converted automatically). Mongoose's `{ timestamps: true }` option is replaced by manually declaring `created_at` and `updated_at` fields with `default_factory`.

### 9. Environment Variable Prefix Change
Vite uses `VITE_` prefix for client-exposed variables. Next.js uses `NEXT_PUBLIC_`. Update all frontend environment variable references.

### 10. shadcn/ui Components Are Compatible
All shadcn/ui components from the original React client work identically in Next.js — just add `"use client"` to any component file that uses them with interactive state.

---

*End of Migration Report. Total conversions: 17 explicit + 3 new capabilities (LangGraph agents, RAG layer, Financial Advisor chat).*
