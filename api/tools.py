import os
import boto3
from strands import tool

#@tool
#def search_vector_db(query: str, customer_id: str) -> str:    
#    """    
#    Handle document-based, narrative, and conceptual queries using the unstructured knowledge base.    
#    Args:        
#        query: A question about business strategies, policies, company information,or requiring document comprehension and qualitative analysis        
#        customer_id: Customer identifier    
#    Returns:        
#    Formatted string response from the knowledge base    
#    """
#    
#    region = os.environ.get("AWS_DEFAULT_REGION", "us-west-2")    
#    kb_id = os.environ.get("KNOWLEDGE_BASE_ID")    
#    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=region)    
#    try:        
#        retrieve_response = bedrock_agent_runtime.retrieve(            knowledgeBaseId=kb_id,            
#            retrievalQuery={"text": query},            
#            retrievalConfiguration={                
#                "vectorSearchConfiguration": {                    "numberOfResults": 5,                    
#                "filter": {"equals": {"key": "customer_id", "value": customer_id}}}
#                }
#        )
        
        # Format the response for better readability        
#        results = []        
#        for result in retrieve_response.get('retrievalResults', []):    
#            content = result.get('content', {}).get('text', '')  
            
#        if content:                
#            results.append(content) 
        
#        return "\n\n".join(results) if results else "No relevant information found."    
#    except Exception as e:        
#        return f"Error in unstructured data assistant: {str(e)}"