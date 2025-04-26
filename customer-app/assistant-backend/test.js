import { AgentForceClient } from './agentforce.js';

const client = new AgentForceClient();

// Example usage
async function testAgentForce() {
    try {
        const agentId = '0XxKB000000c6KN0AY'; // Replace with your actual agent ID
        
        // Create a session
        const session = await client.createSession(agentId);
        console.log('Session created:', session);
        
        // Send a message and handle the stream response
        const sessionId = session.sessionId;
        const response = await client.sendMessage(sessionId, "Show me my leads.");
        console.log('Full response:', response);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

testAgentForce(); 