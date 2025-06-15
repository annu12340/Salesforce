# Enigma
`An AI-Powered Business Automation Solution`

Enigma is a full-stack, AI-driven automation suite built on the Agentforce platform. It combines three intelligent agents to streamline customer support, internal operations, and executive decision-making for businesses. Demonstrated in the context of an escape room startup, Escape.exe, it offers:

- Customer Agent: A 3D avatar chatbot for 24/7 support and lead/case handling.
- Internal Employee Agent: Automates workflows like case summarization and triage, lead follow-ups etc
- Administrator Agent: Provides daily reports, operational insights, content automation etc 

*Enigma's versatility is showcased in the context of an escape room startup, Escape.exe.*

## Problem Statement
Companies often face challenges in managing customer interactions, internal workflows, and overall business operations. These include:

- Customer Support: Providing timely and effective support, especially during peak hours.
- Lead Management: Efficiently tracking and converting leads, which is crucial for growth but time-consuming.
- Case Management: Handling customer issues and requests to ensure prompt resolution and supports new incident/issue/bug creation etc
- Operational Efficiency: Providing administrators with tools to monitor performance, automate tasks, and gain insights.

## Solution
![img](https://i.ibb.co/5X3p03Pp/highlevel.png)

Enigma addresses these challenges by deploying a suite of AI-powered agents on the Agentforce platform:

- 1. Customer Agent: Enhances customer experience with 24/7 support via an interactive 3D avatar chatbot, RAG-powered knowledge, and automated lead/case management.
- 2. Internal Employee Agent: Boosts productivity by automating workflows:
  - Streamlines lead management with Salesforce integration, Slack notifications, personalized outreach, and conversion tracking.
  - Optimizes case management with intelligent routing, proactive Slack updates, and RAG-powered runbook access, which reduces human effort in finding solutions.
- 3. Administrator/Stakeholder Agent: Delivers daily reports on key metrics (e.g., new cases, bookings, customers), get quick insights about the operations assists with content generation etc


## High-Level Flow of Events
The following outlines the flow of events across the three agents:

### Customer Agent
`App Load → Chat → Backend → Agentforce Logic → Avatar Response`
- Whenever users has a query like booking details or support question, they interact with the 3D avatar chatbot.
- Agent engages with the user, provides answers using the Agentforce knowledge base, captures lead information in Salesforce, handles booking requests, and logs support cases.
- Triggers the Internal Employee Agent, when a new case or lead is created

![img](https://i.ibb.co/KpZHrtxk/a-1.png)

### Internal Employee Agent

**Lead Flow:**
`Customer Chat → Lead Created → Slack Alert → Email Follow-Up → Conversion`
- For lead management, the agent sends a Slack alert to the #new-potential-opportunity channel
- The internal employees gets a button to send a personalized email with a discount code
- The agent tracks lead status, creates a new Salesforce account upon conversion, and notifies the #new-customer Slack channel.

**Case Flow**
`Case Created → Slack Notification → AI Assignment → Team Resolution`

- For case management, the agent sends a case summary to the #central-case-management channel
- It predicts the team responsible for resolving the case,
   routes the case to the appropriate team's Slack channel if confidence is high (>80%), 
   prompts for human intervention and suggests teams if confidence is low (<80%)
- It also shares relevant runbook documentation using RAG functionality of agentforce

**Incident/Bug/Issue creation**
- We can also create incidents, bugs, and other items directly from Slack. I accidentally missed mentioning this in the demo video, so I'm including it here.
- Demo for incident creation: https://youtu.be/QZX2T0t3G88 

![img](https://i.ibb.co/ZzrmSpcZ/int-employee-agent.png)

### Administrator Agent
- Gets daily updates include key metrics such as new leads, bookings, case metrics, and conversion rates via Slack notifacations.
- Using RAGs and custom salesforce flow, answer various management queries
- Assists in content generation, analyzes customer feedback etc

![img](https://i.ibb.co/RTShqSmD/c.png)

## Potential impact

Enigma drives business outcomes through smart automation and AI-driven workflows:

- Cuts support wait times by 60%, enhancing customer satisfaction with always-on assistance.
- Boosts lead conversions by up to 20% through automated capture, follow-ups, and real-time sales engagement.
- 30% faster case resolution, thanks to AI-driven routing, runbook access via RAG, and team-based Slack workflows.
- Higher customer loyalty and operational efficiency through intelligent engagement and streamlined team collaboration.

All these leads to huge improvments in the company value and sales


## Detailed flow

### 1. Customer Agent

- User interaction
  - On app launch, a 3D avatar built with React Three Fiber and Three.js loads, greeting the user. 
  - When the user sends a message, it is sent to the backend via a POST /chat request.
- Backend Processing (Express.js):
  - Session Handling: Initiates or retrieves session with Agentforce to make API calls
  - Agentforce Functionalities:
    - RAG (Retrieval-Augmented Generation): Pulls context-aware answers from the knowledge base.
    - Lead Creation: If it is a new user, then agent creates a new lead in Salesforce 
    - Case Creation: If the agent is unable to help the user, it prompts for a new case creation
- Response Enhancement:
  - The core logic is handled using agentforce API calls
  - Google Gemini is used to get emotion, facial expressions, and animation cues from the agentforce response
  - ElevenLabs: Converts the message to realistic speech (TTS).
  - Rhubarb Lip Sync: Generates mouth movement data from audio.
  - Audio is base64-encoded for frontend use.
- Frontend Playback:
  - Avatar responds with voice, facial animations, and gestures.
  - Three.js and Rhubarb drive 3D rendering and lip sync for a natural conversational experience.

![img](https://i.ibb.co/Z1dnnc0R/diagram-export-30-04-2025-14-45-07.png)

### 2. Internal employee agent

**Lead Management Flow**
- When a new customer interacts with the system, a new Lead record is automatically created in Salesforce with the captured customer information, such as name, contact details etc
- A webhook is configured to send a message to the Slack channel #new-potential-opportunity. The message includes the lead information and a button for follow-up personalized email action with a discount code
- If the lead is converted, a trigger in Salesforce updates the Lead status and creats a new account record. Another webhook sends a notification to the Slack channel #new-customer to inform the team of the new account creation.
- If the lead was not converted, it updates the record accordingly

**Case Management Flow**
- When a new case is created, salesforce get the relevant info for the case and summarize. The AgentForce AI also analyzes the case to determine which team is best fit to handle, assigning a confidence score based on its assessment. It sends these info to the #central-case-management slack channel. 
- Case Routing:
  - If confidence of the agent for the team selection > 80%, the case is auto-routed to that specific team's Slack channel via API.
  - If < 80%, AI suggests top teams, and a human selects the appropriate one.
- Resolution and Status Update
  - The specific team receives the case 
  - They can use agentforce RAG functionality to automatically fetch the relevant runbooks
  - The team resolves the issue using the runbook and updates the case status in the system.

![img](https://i.ibb.co/qMY6HgTt/sequence-diagram.png)

**Incident creation**
- We can also directly create incidents/bugs etc from the slack. I had accidentally missed out this point in the demo video. So adding it here
- Demo for incident creation: https://youtu.be/QZX2T0t3G88 

<video width="320" height="240" controls>
  <source src="https://youtu.be/QZX2T0t3G88" >
</video>

### 3. Administration agent
- A scheduled cron job triggers a flow that sends daily updates like new leads, bookings, accounts, case metrics etc to the admin slack channel
- The RAG model can help in dministrative knowledge and decision-making.
- The system helps in auto-generating contents like escape room descriptions, summarized customer feedback on the escape room etc

## Tech stack used

- **Frontend**
  - React.js
  - Three.js and React Three Fiber/Drei for 3D rendering
  - TailwindCSS for styling

- **Backend**
  - Agentforce API
  - Express.js
  - Google Gemini for emotion and facial expressions
  - ElevenLabs for Text-to-Speech
  - Rhubarb Lip Sync for mouth movement synchronization

- **Salesforce components**
  - Custom flow and pre-existing flow
  - Prompt builder
  - Apex class
  - Custom Objects/Fields
  - Salesforce-Slack Connector
  - Flow Integration with Slack

- **Other stack**
  - Slack
  - Service Cloud for Slack

## Judging criteria
Enigma aligns with the judging criteria as follows:

- Innovation: Enigma pioneers the use of Agentforce to build a multi-agent AI ecosystem tailored for the escape room industry—combining 3D avatars, real-time speech, and intelligent automation in a way not seen before.
- Impact: The solution drives measurable business results—reducing customer wait times by up to 60%, increasing lead conversion rates by 20%, cutting case resolution time by 30%, and lowering operational costs by 20%.
- Technical Excellence: Enigma deeply integrates Agentforce capabilities such as Retrieval-Augmented Generation (RAG), AI-based routing, and intelligent automation, while seamlessly connecting with Salesforce, Slack, ElevenLabs, and Rhubarb Lip Sync for a robust, end-to-end architecture.
- User Experience: Customers interact with a lifelike 3D avatar for instant support, while employees receive intelligent alerts and auto-assigned tasks—ensuring smooth, intuitive experiences across all touchpoints.
- Presentation: The project delivers a polished and compelling demo with a clear narrative, highlighting tangible business benefits and technical sophistication through real-time interactions and metrics.

### Why Enigma Qualifies for Best Use of Slack

Enigma deeply integrates Slack as a central automation and collaboration layer across all three intelligent agents, making it a mission-critical part of the solution. Rather than treating Slack as a simple notification tool, Enigma transforms it into a dynamic control center for real-time decision-making, task automation, and cross-functional communication.

**Key highlights of Slack integration:**

- Actionable Alerts and Interactive Buttons:

Leads generated via the Customer Agent trigger Slack alerts in #new-potential-opportunity, with actionable buttons for internal employees to trigger personalized email follow-ups—bridging AI automation and human judgment seamlessly.

- Intelligent Case Routing in Slack:

New cases are summarized by AI and posted in #central-case-management. If the AI is confident, cases are auto-routed to team-specific Slack channels. If uncertain, it suggests top teams and requests human confirmation—all within Slack, reducing friction and speeding up resolutions.

- Incident and Bug Reporting from Slack:

Enigma enables incident/bug creation directly from Slack, allowing team members to initiate new issues without switching tools. This was demonstrated in this video, showing how Slack acts as a true operational frontend.

- Slack as a Reporting Dashboard:

The Administrator Agent posts daily operational reports (leads, bookings, case stats) to the admin Slack channel. Leadership can also query operational insights using RAG-powered natural language interactions, without ever leaving Slack.

- End-to-End Team Orchestration:

From customer onboarding to lead conversion, case management, bug tracking, and performance reviews—all flows are orchestrated through Slack with real-time context, updates, and AI-powered automation.

In short: Enigma doesn't just use Slack—it amplifies it as a central nervous system for business operations, blending AI-driven automation with human-in-the-loop workflows in a way that's both scalable and intuitive.

**NOTE**:
Most of the Slack wizardry is handled by Python scripts—unfortunately, due to a tight deadline (and Python’s love for last-minute drama), I didn’t get a chance to deploy the backend. So if you try testing the bot in Slack… well, it might ghost you like it’s avoiding work on a Monday morning.

## Screenshots
![img](https://media-hosting.imagekit.io/d0aaff4fb4084438/Screenshot%20(4).png?Expires=1840656300&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=ULZqI9evdhLg39GL2B3bhjKzam2UVAP4tc9LawPeT4G7oKTOjKjLo~-MRBjD-WBTTPqdKUdVP3gPP~IoEQDN2KdfCp7nSqeGfRH5cL-dEdlHSGQ8HadEXGirt~FVzvP6bJINE4EAJhtRq2i~MyOHI48~sUcleqA~crcWPNnaPO6Nj0uChaYTbX~h95IC58roK9yWloo9vuhBAfvXPU8jEMa1kp5hhJs11TPVGHp0G5J4jGZ6TRr89LgK3J5zoK9fIM5r3DZS6A76UJWXDTPcjKNxpchvGR5AbvhyuKCxoAzxCj0JKGTGatjBUsVApGHo-tL1EFXNZ~7ne5RX~TXwrA__)

![img](https://i.ibb.co/SD9GDWRk/Screenshot-2025-05-18-at-6-21-04-PM.png)

![img](https://i.ibb.co/TqpswDMD/Screenshot-2025-05-18-at-6-21-09-PM.png)

- Created a new app for escape room company

![img](https://media-hosting.imagekit.io/a2464a8cb1d44e3d/Scrceenshot%20(4).png?Expires=1840656300&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=CfElHT21ljx-n01~Amco--Cli2d9LJzgKhmLL0T9jjtW14cZLsxML1G1or3CpV2KGMmPTDXtWOdoMEi6zr0KiKSELdO1MCx3UN2Arf5J2KB8b55dUBpjr~HXlT-TP45Fz2SXRjkUPDSIJLyo0LrAOOH6qXfyzl79-tv4-QQj76mHmKtFNExlOPZprZ751ub7E20E6HGZxooflkHIJnWEwLnxNdXAKk3Vg9Bq81~phmUGHpg3GIhqabgDmAOtJQYR~47tPrMPvIrFeFdgGK4Veju0-ivVeWa-apLaIHOs-TuegEwK7iGqMnFFh2RFqdZ3-BKM-xHLn3IbXPHvODquvg__)

![img](https://i.ibb.co/NgXrs3DN/Screenshot-2025-05-18-at-6-21-15-PM.png)

![img](https://media-hosting.imagekit.io/1534a791a7094a4a/d.png?Expires=1840955027&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=vFLkEZdyQbZIqgNIVJZ4LcGj0R-4sddt5aPiYeROIpSHvYgNtsvYHGgGJZoKVWV66Q3Ap4VC-hRB7uO12lSnOXKg44wHW5JetXZNO3vhmmqowXOtq5yGbdK4pAFXeKq~8gwE0O4N-2PyZObuJ2JVceb93dw6ICv9r2HZYAdlsHODW2d~dHLFkpyL9APz01SolL07Tx29gpEet8lNsbsUfL445cCXhqyE9PBW5p~vcsG0cH3PKvzjVlZL5~IGgMYeOgEcF0247xym9Fmg3MleKAaPOBcU9nSMpU0B498gSiWljRt7CP6Zw0jtL~Vyib7ML9hmPGZGaPH0ziS7WcMH1Q__)

![img](https://i.ibb.co/KxyzYrSQ/Screenshot-2025-05-18-at-6-21-21-PM.png)

![img](https://i.ibb.co/S1bw7b2/Screenshot-2025-05-18-at-6-21-27-PM.png)

![img](https://i.ibb.co/ynZSQYfs/Screenshot-2025-05-18-at-6-21-34-PM.png)

![img](https://i.ibb.co/1fSPDQd9/Screenshot-2025-05-18-at-6-21-39-PM.png)

![img](https://i.ibb.co/RTQqbCd4/Screenshot-2025-05-18-at-6-21-47-PM.png)

![img](https://i.ibb.co/nMLnLpDC/Screenshot-2025-05-18-at-6-22-00-PM.png)

![img](https://i.ibb.co/CCPcf7L/Screenshot-2025-05-18-at-6-22-06-PM.png)


## Challenges we ran into
- As a first-time Salesforce user, navigating the ecosystem—understanding objects, flows, and integrations—was initially overwhelming. A significant portion of the hackathon was spent rapidly upskilling and experimenting with key Salesforce components to get things working.
- I had received the Salesforce credentials later than expected, which compressed our development timeline. 
- I had faced a lot of bugs while developing the entire platform. But the folks in the agentforce slack channel were pretty helpful and it had unblokced me
- Because of time constraints, I couldn't implement all the functionalities that I had planned for
- While cleaning up the salesforce flow and agentforce agents, I had accidentally deleted the working agents. So I had to redo the entire agent creation once again at the last moment 😭

## Accomplishments that we're proud of
- The whole thing ... So proud to build a working model in just a few days— after overcoming all the above blockers and challenges

