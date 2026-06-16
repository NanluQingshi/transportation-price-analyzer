from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.routes import RouteCreate, RouteResponse, RoutesListResponse
from src.services import routes_service

router = APIRouter()


@router.get("/routes", response_model=RoutesListResponse)
async def list_routes(db: AsyncSession = Depends(get_db)) -> RoutesListResponse:
    routes = await routes_service.list_routes(db)
    return RoutesListResponse(routes=routes)


@router.post("/routes", response_model=RouteResponse, status_code=201)
async def create_route(
    body: RouteCreate,
    db: AsyncSession = Depends(get_db),
) -> RouteResponse:
    return await routes_service.create_route(db, body.origin, body.destination)


@router.delete("/routes/{route_id}", status_code=204)
async def delete_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await routes_service.delete_route(db, route_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Route not found")
