public class ConvertLeadApex {

    @InvocableMethod(label='Convert Lead' description='Converts a lead into an account, a contact, and optionally an opportunity.')
    public static List<LeadConversionResult> convertLead(List<LeadConversionRequest> requests) {
        List<LeadConversionResult> results = new List<LeadConversionResult>();

        for (LeadConversionRequest request : requests) {
            LeadConversionResult result = new LeadConversionResult();
            try {
                // Set the default handling for booleans.
                if (request.overWriteLeadSource == null) request.overWriteLeadSource = false;
                if (request.createOpportunity == null) request.createOpportunity = true;
                if (request.sendEmailToOwner == null) request.sendEmailToOwner = false;

                // Convert the lead by passing it to a helper method.
                Map<String,String> conversionResult = convertLead(request.leadID, request.contactID, request.accountID, 
                    request.convertedStatus, request.overWriteLeadSource, request.createOpportunity, 
                    request.opportunityName, request.sendEmailToOwner);

                result.accountID = conversionResult.get('AccountID');
                result.contactID = conversionResult.get('ContactID');
                result.opportunityID = conversionResult.get('OpportunityID');
            } catch (Exception e) {
                result.errorMessage = e.getMessage();
            }
            results.add(result);
        }
        return results;
    }

    public static Map<String,String> convertLead (
        String leadID,
        String contactID,
        String accountID,
        String convertedStatus,
        Boolean overWriteLeadSource,
        Boolean createOpportunity,
        String opportunityName,
        Boolean sendEmailToOwner
    ) {
        Map<String,String> result = new Map<String,String>();

        if (leadId == null) throw new ConvertLeadPluginException('Lead Id cannot be null');

        // Check for multiple leads with the same ID
        Lead[] leads = [Select Id, FirstName, LastName, Company From Lead where Id = :leadID];
        if (leads.size() > 0) {
            Lead l = leads[0];
            // CheckAccount = true, checkContact = false
            if (accountID == null && l.Company != null) {
                Account[] accounts = [Select Id, Name FROM Account where Name = :l.Company LIMIT 1];
                if (accounts.size() > 0) {
                    accountId = accounts[0].id;
                }
            }

            // Perform the lead conversion.
            Database.LeadConvert lc = new Database.LeadConvert();
            lc.setLeadId(leadID);
            lc.setOverwriteLeadSource(overWriteLeadSource);
            lc.setDoNotCreateOpportunity(!createOpportunity);
            lc.setConvertedStatus(convertedStatus);
            if (sendEmailToOwner != null) lc.setSendNotificationEmail(sendEmailToOwner);
            if (accountId != null && accountId.length() > 0) lc.setAccountId(accountId);
            if (contactId != null && contactId.length() > 0) lc.setContactId(contactId);
            if (createOpportunity) {
                lc.setOpportunityName(opportunityName);
            }

            Database.LeadConvertResult lcr = Database.convertLead(lc, true);
            if (lcr.isSuccess()) {
                result.put('AccountID', lcr.getAccountId());
                result.put('ContactID', lcr.getContactId());
                if (createOpportunity) {
                    result.put('OpportunityID', lcr.getOpportunityId());
                }
            } else {
                String error = lcr.getErrors()[0].getMessage();
                throw new ConvertLeadPluginException(error);
            }
        } else { 
            throw new ConvertLeadPluginException('No leads found with Id : "' + leadId + '"');
        }
        return result;
    }

    public class LeadConversionRequest {
        @InvocableVariable(required=true)
        public String leadID;
        @InvocableVariable
        public String contactID;
        @InvocableVariable
        public String accountID;
        @InvocableVariable(required=true)
        public String convertedStatus;
        @InvocableVariable
        public Boolean overWriteLeadSource;
        @InvocableVariable
        public Boolean createOpportunity;
        @InvocableVariable
        public String opportunityName;
        @InvocableVariable
        public Boolean sendEmailToOwner;
    }

    public class LeadConversionResult {
        @InvocableVariable
        public String accountID;
        @InvocableVariable
        public String contactID;
        @InvocableVariable
        public String opportunityID;
        @InvocableVariable
        public String errorMessage;
    }

    // Utility exception class
    public class ConvertLeadPluginException extends Exception {}
}