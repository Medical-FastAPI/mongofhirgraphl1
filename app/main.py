from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from contextlib import asynccontextmanager
from app.graphql.schema import schema
from app.config.database import get_database, close_database
from app.db.indexes import create_indexes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # Test database connection
        db = await get_database()
        await db.client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes(db)
        print("Indexes created successfully")
        
        yield
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise e
    finally:
        # Cleanup
        print("Shutting down...")
        await close_database()

app = FastAPI(
    title="FHIR GraphQL Server",
    description="A FHIR-compliant GraphQL server for healthcare data",
    version="1.0.0",
    lifespan=lifespan
)

# Create GraphQL route
graphql_router = GraphQLRouter(schema)

# Add routes
app.include_router(graphql_router, prefix="/graphql")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)