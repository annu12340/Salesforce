import logging
import re

logger = logging.getLogger(__name__)

class CaseParser:
    def __init__(self):
        pass
    
    def parse_case_text(self, text):
        """
        Parse case text with the following format:
        
        Case number: 12312
        Summary: user a is having issues
        Team: IAM team
        Confidence: 80%
        
        Returns a dictionary with the parsed information or None if parsing fails.
        """
        try:
            case_data = {}
            
            # Extract case number
            case_number_match = re.search(r'Case number:\s*(.*?)(?:\n|$)', text)
            if case_number_match:
                case_data['case_number'] = case_number_match.group(1).strip()
            
            # Extract summary
            summary_match = re.search(r'Summary:\s*(.*?)(?:\n|$)', text)
            if summary_match:
                case_data['summary'] = summary_match.group(1).strip()
            
            # Extract team
            team_match = re.search(r'Team:\s*(.*?)(?:\n|$)', text)
            if team_match:
                case_data['team'] = team_match.group(1).strip().lower()
            
            # Extract confidence
            confidence_match = re.search(r'Confidence:\s*(\d+)%', text)
            if confidence_match:
                confidence = int(confidence_match.group(1))
                case_data['confidence'] = confidence
            
            # Check if all required fields are present
            required_fields = ['case_number', 'summary', 'team', 'confidence']
            if all(field in case_data for field in required_fields):
                logger.info(f"Successfully parsed case: {case_data['case_number']} with confidence {case_data['confidence']}%")
                return case_data
            else:
                missing = [field for field in required_fields if field not in case_data]
                logger.warning(f"Case parsing failed, missing fields: {missing}")
                return None
                
        except Exception as e:
            logger.exception(f"Error parsing case text: {e}")
            return None 