# app/db/versioning.py
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Dict, Any

class VersionManager:
    @staticmethod
    async def create_versioned_resource(
        db: AsyncIOMotorDatabase,
        resource_type: str,
        data: Dict[str, Any],
        id: str = None
    ) -> Dict[str, Any]:
        """Create a new versioned resource"""
        # If no ID provided, generate one
        if not id:
            id = str(ObjectId())
            
        # Get the collection names
        resource_collection = db[resource_type.lower()]
        history_collection = db[f"{resource_type.lower()}_history"]
        
        # Set version 1.0.0 for new resources
        version = "1.0.0"
        
        # Update metadata
        data.update({
            "_id": ObjectId(id),
            "id": id,
            "meta": {
                "versionId": version,
                "lastUpdated": datetime.utcnow().isoformat(),
                "profile": data.get("meta", {}).get("profile", [])
            }
        })
        
        # Store in both collections
        await resource_collection.insert_one(data)
        await history_collection.insert_one({
            **data,
            "_id": ObjectId(),  # New _id for history
            "version": version
        })
        
        return data

    @staticmethod
    async def update_versioned_resource(
        db: AsyncIOMotorDatabase,
        resource_type: str,
        id: str,
        data: Dict[str, Any],
        is_major_update: bool = False
    ) -> Dict[str, Any]:
        """Update a versioned resource with semantic versioning"""
        # Get collection names using lowercase
        resource_collection = db[resource_type.lower()]
        history_collection = db[f"{resource_type.lower()}_history"]
        
        # Get current resource
        current = await resource_collection.find_one({"id": id})
        if not current:
            raise ValueError(f"Resource {id} not found")
            
        # Parse current version
        current_version = current["meta"]["versionId"]
        major, minor, patch = map(int, current_version.split("."))
        
        # Determine new version based on update type
        if is_major_update:
            new_version = f"{major + 1}.0.0"
        else:
            new_version = f"{major}.{minor + 1}.0"

        # Store current version in history
        history_doc = {
            **current,
            "_id": ObjectId(),  # New _id for history
            "version": current_version
        }
        await history_collection.insert_one(history_doc)
        
        # Update metadata for the new version
        new_meta = {
            "versionId": new_version,
            "lastUpdated": datetime.utcnow().isoformat(),
            "profile": data.get("meta", {}).get("profile", current["meta"].get("profile", []))
        }
        
        # Prepare the updated document
        updated_doc = {
            **data,
            "_id": current["_id"],
            "id": id,
            "meta": new_meta
        }
        
        # Update the current resource
        await resource_collection.replace_one(
            {"_id": current["_id"]}, 
            updated_doc
        )
        
        return updated_doc

    @staticmethod
    async def get_resource_history(
        db: AsyncIOMotorDatabase,
        resource_type: str,
        id: str
    ) -> list:
        """Get version history of a resource"""
        history_collection = db[f"{resource_type.lower()}_history"]
        cursor = history_collection.find({"id": id}).sort("meta.versionId", -1)
        history_docs = await cursor.to_list(length=None)
        
        # Get current version too
        current = await db[resource_type.lower()].find_one({"id": id})
        if current:
            # Convert current document to history format
            current["version"] = current["meta"]["versionId"]
            history_docs.insert(0, current)
            
        return history_docs

    @staticmethod
    async def get_version(
        db: AsyncIOMotorDatabase,
        resource_type: str,
        id: str,
        version: str
    ) -> Dict[str, Any]:
        """Get a specific version of a resource"""
        # If it's the current version
        if version == "current":
            return await db[resource_type.lower()].find_one({"id": id})
            
        # Check history collection
        history_doc = await db[f"{resource_type.lower()}_history"].find_one({
            "id": id,
            "version": version
        })
        
        return history_doc