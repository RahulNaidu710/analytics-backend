from typing import List, Optional, Union

from fastapi import APIRouter, Depends

from domain.platform_users.models import PlatformUser
from domain.platform_users.service import PlatformUserService
from domain.apps.service import AppService
from rest.dtos.platform_users import (
    AppWiseUserDto,
    PlatformUserWithPrivateFields,
    PrivateUserResponse,
)
from rest.middlewares import get_user, get_user_id, validate_jwt

router = APIRouter(
    tags=["platform-users"],
    dependencies=[Depends(validate_jwt)],
    responses={401: {}},
)


@router.get("/platform-users/me", response_model=PlatformUserWithPrivateFields)
async def get_current_user(
    user_id: str = Depends(get_user_id),
    user_service: PlatformUserService = Depends(),
):
    user = await user_service.get_user(user_id)
    return PlatformUserWithPrivateFields(
        id=user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        picture=user.picture,
        slack_channel=user.slack_channel,
        has_visited_sheets=user.has_visted_sheets,
        api_key=user.api_key,
        sheet_token=user.sheet_token,
    )


@router.put("/platform-users")
async def remove_slack_credentials(
    delete_slack_credentials: Optional[bool] = None,
    has_visited_sheets: Optional[bool] = None,
    user_id: str = Depends(get_user_id),
    user_service: PlatformUserService = Depends(),
):
    if delete_slack_credentials:
        return await user_service.remove_slack_credentials(user_id)

    if has_visited_sheets:
        return await user_service.update_visited_sheets_status(user_id=user_id)


async def get_users_for_app(app_id, app_service, user_service):
    user_ids = await app_service.get_users_for_app(app_id=app_id)
    return [await user_service.get_user(id=user_id) for user_id in user_ids]


@router.get("/platform-users", response_model=List[PrivateUserResponse])
async def get_platform_users(
    app_id: Union[str, None] = None,
    user_service: PlatformUserService = Depends(),
    app_service: AppService = Depends(),
):
    if app_id:
        return await get_users_for_app(
            app_id=app_id, app_service=app_service, user_service=user_service
        )
    else:
        return await user_service.get_all_platform_users()


@router.get("/platform-users/apps/all", response_model=List[AppWiseUserDto])
async def get_platform_users(
    user: PlatformUser = Depends(get_user),
    user_service: PlatformUserService = Depends(),
    app_service: AppService = Depends(),
):
    all_apps = await app_service.get_apps(user)
    response = []
    for app in all_apps:
        data = AppWiseUserDto(
            app=app.id,
            users=await get_users_for_app(
                app_id=app.id, app_service=app_service, user_service=user_service
            ),
        )

        response.append(data)
    return response
