# ParkMate

A peer-to-peer parking marketplace that connects property owners with unused parking spaces to drivers seeking reliable, on-demand parking — by the hour, day, or month.

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-black)](https://nodejs.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-black.svg)](CONTRIBUTING.md)
[![Status](https://img.shields.io/badge/status-active%20development-black)]()

---

## Overview

Urban parking is a structural mismatch problem. In dense cities, thousands of private parking spaces sit idle during working hours while drivers circle blocks for 20–40 minutes per trip. ParkMate resolves this by turning idle private space into a liquid, bookable asset — similar to what Airbnb did for rooms.

The platform operates as a two-sided marketplace with two user roles: **Hosts** (spot owners) and **Guests** (drivers), with the platform facilitating trust, payments, and dispute resolution between them.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Client Layer                      │
│         Web (Next.js)     Mobile (React Native)      │
└──────────────────────┬───────────────────────────────┘
                       │ REST / WebSocket
┌──────────────────────▼───────────────────────────────┐
│                    API Layer                         │
│                   Node.js + Express                  │
│   Auth │ Listings │ Bookings │ Payments │ KYC │ Chat │
└──┬──────────┬──────────┬──────────┬──────────┬───────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
PostgreSQL  Redis    Razorpay  Google Maps  Digilocker
(primary)  (cache,  (payments)   (geo)       (KYC)
           sessions)
```

---

## Features

### Host (Spot Owner)
- Create listings with photos, geolocation, vehicle size constraints, and access instructions
- Set granular availability — recurring weekly schedules or one-off date ranges
- Configure hourly, daily, or monthly pricing
- Earnings dashboard with bank withdrawal via IMPS/NEFT

### Guest (Driver)
- Map-based spot discovery with real-time availability
- Filters: vehicle type, time range, price, amenities (covered, CCTV, EV charging)
- Advance booking with secure payments via Razorpay
- Turn-by-turn navigation to spot with entry instructions

### Platform-wide
- Mutual review and rating system
- Real-time in-app messaging
- KYC verification (Aadhaar, PAN, Driving License) via Digilocker API
- Automated overstay detection and penalty billing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Mobile | React Native (Expo) |
| Backend | Node.js, Express |
| Database | PostgreSQL (primary), Redis (cache + sessions) |
| ORM | Prisma |
| Maps | Google Maps Platform (Maps, Places, Directions APIs) |
| Payments | Razorpay (marketplace split payments) |
| Auth / OTP | Twilio / MSG91 |
| KYC | Digilocker API |
| File Storage | AWS S3 |
| Deployment | Docker, AWS ECS |

---

## Getting Started

### Prerequisites

- Node.js v18+
- PostgreSQL 15+
- Redis 7+
- API keys: Google Maps, Razorpay, Twilio, Digilocker

### Installation

```bash
git clone https://github.com/your-username/parkmate.git
cd parkmate
npm install
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/parkmate"
REDIS_URL="redis://localhost:6379"

# Google Maps
GOOGLE_MAPS_API_KEY=

# Payments
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

# Auth
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# KYC
DIGILOCKER_CLIENT_ID=
DIGILOCKER_CLIENT_SECRET=

# Storage
AWS_BUCKET_NAME=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=

# App
JWT_SECRET=
NODE_ENV=development
PORT=3000
```

### Running Locally

```bash
# Run database migrations
npx prisma migrate dev

# Seed development data
npx prisma db seed

# Start development server (API + Web)
npm run dev

# Start mobile app
cd mobile && npx expo start
```

### Running with Docker

```bash
docker-compose up --build
```

---

## Project Structure

```
parkmate/
├── apps/
│   ├── web/                  # Next.js web app
│   └── mobile/               # React Native app (Expo)
├── packages/
│   ├── api/                  # Express REST API
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── middleware/
│   │   └── services/
│   │       ├── listings/
│   │       ├── bookings/
│   │       ├── payments/
│   │       ├── kyc/
│   │       └── notifications/
│   ├── db/                   # Prisma schema + migrations
│   └── shared/               # Shared types and utilities
├── docker-compose.yml
└── package.json
```

---

## API Reference

A full OpenAPI spec is available at `/api/docs` when running locally.

Key endpoints:

```
POST   /api/auth/send-otp
POST   /api/auth/verify-otp

GET    /api/listings?lat=&lng=&radius=&from=&to=
POST   /api/listings
GET    /api/listings/:id
PATCH  /api/listings/:id

POST   /api/bookings
GET    /api/bookings/:id
POST   /api/bookings/:id/cancel

POST   /api/payments/initiate
POST   /api/payments/webhook

POST   /api/kyc/initiate
GET    /api/kyc/status
```

---

## Business Logic

**Payments split**
The platform charges a 10% commission from the Host and a 5% convenience fee from the Guest on every transaction. Razorpay's marketplace (Route) product handles the automatic split at settlement.

**Overstay handling**
If a Guest has not vacated by the booking end time, the system bills an overstay rate of 3× the hourly price for every additional hour. Hosts can initiate a dispute through the support channel if the Guest is unreachable.

**KYC requirements**
Both Hosts and Guests are required to complete KYC before their first transaction. Aadhaar verification is mandatory. PAN and Driving License verification are strongly recommended and unlock higher transaction limits.

---

## Deployment

```bash
# Build Docker images
docker build -t parkmate-api ./packages/api
docker build -t parkmate-web ./apps/web

# Push to ECR and deploy via ECS task definitions
# (see .github/workflows/deploy.yml for the full CI/CD pipeline)
```

---

## Roadmap

**v0.1 — MVP**
- [x] Listing creation and search
- [x] Google Maps integration
- [x] Razorpay payment flow
- [ ] OTP authentication
- [ ] Booking management

**v0.2 — Trust & Safety**
- [ ] Digilocker KYC integration
- [ ] Review and rating system
- [ ] Overstay detection and penalty billing
- [ ] In-app chat

**v0.3 — Growth**
- [ ] React Native mobile app
- [ ] Event parking partnerships
- [ ] Monthly pass system
- [ ] Host analytics dashboard

---

## Contributing

1. Fork the repository
2. Create a feature branch — `git checkout -b feat/your-feature`
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`, `fix:`, `chore:`, etc.
4. Open a pull request against `main` with a clear description of the change

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR. All contributions require passing CI and at least one approving review.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
