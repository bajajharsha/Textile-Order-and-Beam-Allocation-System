"""
Dependency injection setup for the application
"""

from config.database import get_supabase_client
from controllers.master_controller import MasterController
from controllers.order_controller import OrderController
from controllers.party_controller import PartyController
from fastapi import Depends
from repositories.color_repository import ColorRepository
from repositories.cut_repository import CutRepository
from repositories.order_repository import OrderRepository
from repositories.party_repository import PartyRepository
from repositories.quality_repository import QualityRepository
from supabase import Client
from usecases.master_usecase import MasterUseCase
from usecases.order_usecase import OrderUseCase
from usecases.party_usecase import PartyUseCase


async def get_db_client() -> Client:
    """Dependency to get database client"""
    return await get_supabase_client()


# Party dependencies
def get_party_repository(db_client: Client = Depends(get_db_client)) -> PartyRepository:
    """Dependency to get party repository"""
    return PartyRepository(db_client)


def get_party_usecase(
    repository: PartyRepository = Depends(get_party_repository),
) -> PartyUseCase:
    """Dependency to get party use case"""
    return PartyUseCase(repository)


def get_party_controller(
    use_case: PartyUseCase = Depends(get_party_usecase),
) -> PartyController:
    """Dependency to get party controller"""
    return PartyController(use_case)


# Master data dependencies
def get_color_repository(db_client: Client = Depends(get_db_client)) -> ColorRepository:
    """Dependency to get color repository"""
    return ColorRepository(db_client)


def get_quality_repository(
    db_client: Client = Depends(get_db_client),
) -> QualityRepository:
    """Dependency to get quality repository"""
    return QualityRepository(db_client)


def get_cut_repository(db_client: Client = Depends(get_db_client)) -> CutRepository:
    """Dependency to get cut repository"""
    return CutRepository(db_client)


def get_master_usecase(
    color_repository: ColorRepository = Depends(get_color_repository),
    quality_repository: QualityRepository = Depends(get_quality_repository),
    cut_repository: CutRepository = Depends(get_cut_repository),
) -> MasterUseCase:
    """Dependency to get master use case"""
    return MasterUseCase(color_repository, quality_repository, cut_repository)


def get_master_controller(
    use_case: MasterUseCase = Depends(get_master_usecase),
) -> MasterController:
    """Dependency to get master controller"""
    return MasterController(use_case)


# Order dependencies
def get_order_repository(db_client: Client = Depends(get_db_client)) -> OrderRepository:
    """Dependency to get order repository"""
    return OrderRepository(db_client)


def get_order_usecase(
    order_repository: OrderRepository = Depends(get_order_repository),
    color_repository: ColorRepository = Depends(get_color_repository),
) -> OrderUseCase:
    """Dependency to get order use case"""
    return OrderUseCase(order_repository, color_repository)


def get_order_controller(
    use_case: OrderUseCase = Depends(get_order_usecase),
) -> OrderController:
    """Dependency to get order controller"""
    return OrderController(use_case)
