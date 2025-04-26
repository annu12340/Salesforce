const AgentForceClient = require('./agentforce');

const client = new AgentForceClient({
    domainUrl: 'your-domain.my.salesforce.com',
    consumerKey: 'your-consumer-key',
    consumerSecret: 'your-consumer-secret'
});

const agentId = 'your-agent-id';
const session = await client.createSession(agentId);
console.log('Session created:', session);