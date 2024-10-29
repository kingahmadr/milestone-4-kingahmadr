# from src.config.settings import create_app
from src.config.settings import create_app

# Main driver function
app = create_app()

if __name__ == '__main__':
    import hypercorn.asyncio
    import asyncio

    asyncio.run(hypercorn.asyncio.serve(app, hypercorn.Config()))
