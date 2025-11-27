from fastapi import APIRouter, Depends, HTTPException, status
from app.api.endpoints.auth import get_current_user
from app.models.user import ChatRequest, ChatMessage
from app.services.gemini_service import generate_medical_response
from app.db.mongodb import get_database
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
MAX_MESSAGE_LENGTH = 5000

@router.post("/message", response_model=ChatMessage)
async def send_message(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    # Input validation
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    if len(request.message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message too long. Maximum length is {MAX_MESSAGE_LENGTH} characters"
        )
    
    user_email = current_user["email"]
    logger.info(f"Processing chat message from user: {user_email}")
    
    try:
        db = await get_database()
        
        # Fetch history
        history_doc = await db.chat_history.find_one({"user_email": user_email})
        history = history_doc["messages"] if history_doc else []
        
        # Generate AI response
        ai_response_text = await generate_medical_response(history, request.message)
        
        # Create message objects
        user_msg = ChatMessage(role="user", content=request.message)
        ai_msg = ChatMessage(role="model", content=ai_response_text)
        
        # Update history in database
        new_messages = [user_msg.dict(), ai_msg.dict()]
        if history_doc:
            await db.chat_history.update_one(
                {"user_email": user_email},
                {"$push": {"messages": {"$each": new_messages}}}
            )
        else:
            await db.chat_history.insert_one({
                "user_email": user_email,
                "messages": new_messages
            })
        
        logger.info(f"Successfully processed message for user: {user_email}")
        return ai_msg
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error processing chat message for {user_email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your message. Please try again."
        )

@router.get("/history", response_model=List[ChatMessage])
async def get_history(current_user: dict = Depends(get_current_user)):
    try:
        db = await get_database()
        history_doc = await db.chat_history.find_one({"user_email": current_user["email"]})
        return history_doc["messages"] if history_doc else []
    except Exception as e:
        logger.error(f"Error fetching chat history for {current_user['email']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat history. Please try again."
        )

@router.delete("/messages/{message_index}")
async def delete_message(message_index: int, current_user: dict = Depends(get_current_user)):
    try:
        db = await get_database()
        user_email = current_user["email"]
        
        history_doc = await db.chat_history.find_one({"user_email": user_email})
        if not history_doc or not history_doc.get("messages"):
            raise HTTPException(status_code=404, detail="Message not found")
            
        messages = history_doc["messages"]
        if message_index < 0 or message_index >= len(messages):
            raise HTTPException(status_code=404, detail="Message not found")
            
        # Determine which messages to delete (Context-Aware Deletion)
        # If user message (usually even index), delete it and the next AI response
        # If AI message (usually odd index), delete it and the previous user message
        
        indices_to_delete = set()
        indices_to_delete.add(message_index)
        
        msg_role = messages[message_index]["role"]
        
        if msg_role == "user":
            # Look for the next message if it exists and is from model
            if message_index + 1 < len(messages) and messages[message_index + 1]["role"] == "model":
                indices_to_delete.add(message_index + 1)
        elif msg_role == "model":
            # Look for the previous message if it exists and is from user
            if message_index - 1 >= 0 and messages[message_index - 1]["role"] == "user":
                indices_to_delete.add(message_index - 1)
                
        # Filter out the messages
        new_messages = [msg for i, msg in enumerate(messages) if i not in indices_to_delete]
        
        # Update database
        await db.chat_history.update_one(
            {"user_email": user_email},
            {"$set": {"messages": new_messages}}
        )
        
        return {"message": "Messages deleted successfully", "deleted_indices": list(indices_to_delete)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message for {user_email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message."
        )
