@isTest
public class ConvertLeadApexTest {
    
    @isTest
    static void testConvertLead() {
        // Create a test lead
        Lead testLead = new Lead(
            LastName = 'TestLastName',
            Company = 'TestCompany',
            Status = 'Open - Not Contacted'
        );
        insert testLead;

        // Create a test account
        Account testAccount = new Account(
            Name = 'TestCompany'
        );
        insert testAccount;

        // Set up the request parameters
        ConvertLeadApex.LeadConversionRequest request = new ConvertLeadApex.LeadConversionRequest();
        request.leadID = testLead.Id;
        request.accountID = testAccount.Id;
        request.convertedStatus = 'Closed - Converted';
        request.overWriteLeadSource = true;
        request.createOpportunity = true;
        request.opportunityName = 'Test Opportunity';
        request.sendEmailToOwner = false;

        // Add the request to a list
        List<ConvertLeadApex.LeadConversionRequest> requests = new List<ConvertLeadApex.LeadConversionRequest>{ request };

        // Invoke the method
        Test.startTest();
        List<ConvertLeadApex.LeadConversionResult> results = ConvertLeadApex.convertLead(requests);
        Test.stopTest();

        // Verify the results
        System.assertEquals(1, results.size());
        ConvertLeadApex.LeadConversionResult result = results[0];
        System.assertNotEquals(null, result.accountID);
        System.assertNotEquals(null, result.contactID);
        System.assertNotEquals(null, result.opportunityID);
        System.assertEquals(null, result.errorMessage);

        // Verify that the lead was converted
        Lead convertedLead = [SELECT Id, IsConverted, ConvertedAccountId, ConvertedContactId, ConvertedOpportunityId FROM Lead WHERE Id = :testLead.Id];
        System.assert(convertedLead.IsConverted);
        System.assertEquals(testAccount.Id, convertedLead.ConvertedAccountId);
        System.assertNotEquals(null, convertedLead.ConvertedContactId);
        System.assertNotEquals(null, convertedLead.ConvertedOpportunityId);

        // Verify that the contact was created
        Contact newContact = [SELECT Id, LastName, AccountId FROM Contact WHERE Id = :convertedLead.ConvertedContactId];
        System.assertEquals(testLead.LastName, newContact.LastName);
        System.assertEquals(testAccount.Id, newContact.AccountId);

        // Verify that the opportunity was created
        Opportunity newOpportunity = [SELECT Id, Name, AccountId FROM Opportunity WHERE Id = :convertedLead.ConvertedOpportunityId];
        System.assertEquals(request.opportunityName, newOpportunity.Name);
        System.assertEquals(testAccount.Id, newOpportunity.AccountId);
    }

    @isTest
    static void testConvertLeadWithoutOpportunity() {
        // Create a test lead
        Lead testLead = new Lead(
            LastName = 'TestLastName',
            Company = 'TestCompany',
            Status = 'Open - Not Contacted'
        );
        insert testLead;

        // Set up the request parameters
        ConvertLeadApex.LeadConversionRequest request = new ConvertLeadApex.LeadConversionRequest();
        request.leadID = testLead.Id;
        request.convertedStatus = 'Closed - Converted';
        request.overWriteLeadSource = false;
        request.createOpportunity = false;
        request.sendEmailToOwner = false;

        // Add the request to a list
        List<ConvertLeadApex.LeadConversionRequest> requests = new List<ConvertLeadApex.LeadConversionRequest>{ request };

        // Invoke the method
        Test.startTest();
        List<ConvertLeadApex.LeadConversionResult> results = ConvertLeadApex.convertLead(requests);
        Test.stopTest();

        // Verify the results
        System.assertEquals(1, results.size());
        ConvertLeadApex.LeadConversionResult result = results[0];
        System.assertNotEquals(null, result.accountID);
        System.assertNotEquals(null, result.contactID);
        System.assertEquals(null, result.opportunityID);
        System.assertEquals(null, result.errorMessage);

        // Verify that the lead was converted
        Lead convertedLead = [SELECT Id, IsConverted, ConvertedAccountId, ConvertedContactId, ConvertedOpportunityId FROM Lead WHERE Id = :testLead.Id];
        System.assert(convertedLead.IsConverted);
        System.assertNotEquals(null, convertedLead.ConvertedAccountId);
        System.assertNotEquals(null, convertedLead.ConvertedContactId);
        System.assertEquals(null, convertedLead.ConvertedOpportunityId);
    }

    @isTest
    static void testConvertLeadWithErrors() {
        // Set up the request parameters
        ConvertLeadApex.LeadConversionRequest request = new ConvertLeadApex.LeadConversionRequest();
        request.leadID = null; // Invalid Lead ID
        request.convertedStatus = 'Closed - Converted';

        // Add the request to a list
        List<ConvertLeadApex.LeadConversionRequest> requests = new List<ConvertLeadApex.LeadConversionRequest>{ request };

        // Invoke the method
        Test.startTest();
        List<ConvertLeadApex.LeadConversionResult> results = ConvertLeadApex.convertLead(requests);
        Test.stopTest();

        // Verify the results
        System.assertEquals(1, results.size());
        ConvertLeadApex.LeadConversionResult result = results[0];
        System.assertEquals(null, result.accountID);
        System.assertEquals(null, result.contactID);
        System.assertEquals(null, result.opportunityID);
        System.assertNotEquals(null, result.errorMessage);
    }
}