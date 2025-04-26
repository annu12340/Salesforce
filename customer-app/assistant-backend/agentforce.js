import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';

dotenv.config();

export class AgentForceClient {
    constructor() {
        this.domainUrl = process.env.SALESFORCE_DOMAIN_URL;
        this.consumerKey = process.env.SALESFORCE_CONSUMER_KEY;
        this.consumerSecret = process.env.SALESFORCE_CONSUMER_SECRET;
        this.accessToken = null;
        this.sequenceId = 0;

        // Validate required environment variables
        if (!this.domainUrl || !this.consumerKey || !this.consumerSecret) {
            throw new Error('Missing required environment variables. Please check your .env file.');
        }
    }

    async getAccessToken() {
        console.log("Getting access token");
        try {
            const response = await axios.post(
                `https://${this.domainUrl}/services/oauth2/token`,
                new URLSearchParams({
                    grant_type: 'client_credentials',
                    client_id: this.consumerKey,
                    client_secret: this.consumerSecret
                }),
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            );

            this.accessToken = response.data.access_token;
            return this.accessToken;
        } catch (error) {
            console.error('Error getting access token:', error.response?.data || error.message);
            throw error;
        }
    }

    async createSession(agentId) {
        console.log("Creating session for agent:", agentId);
        if (!this.accessToken) {
            await this.getAccessToken();
        }

        const sessionKey = uuidv4();
        
        try {
            const response = await axios.post(
                `https://api.salesforce.com/einstein/ai-agent/v1/agents/${agentId}/sessions`,
                {
                    externalSessionKey: sessionKey,
                    instanceConfig: {
                        endpoint: `https://${this.domainUrl}`
                    },
                    streamingCapabilities: {
                        chunkTypes: ["Text"]
                    },
                    bypassUser: true
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error creating session:', error.response?.data || error.message);
            throw error;
        }
    }

    async sendMessage(sessionId, messageText) {
        console.log("Sending message to session:", sessionId);
        if (!this.accessToken) {
            await this.getAccessToken();
        }

        this.sequenceId += 1;
        
        try {
            const response = await axios.post(
                `https://api.salesforce.com/einstein/ai-agent/v1/sessions/${sessionId}/messages`,
                {
                    message: {
                        sequenceId: this.sequenceId,
                        type: "Text",
                        text: messageText
                    }
                },
                {
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error sending message:', error.response?.data || error.message);
            throw error;
        }
    }
} 