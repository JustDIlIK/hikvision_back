from fastapi import FastAPI
from sqladmin import Admin

from app.api.responses.admin import (
    UserAdmin,
    AreasAdmin,
    DevicesAdmin,
    TgUsersAdmin,
    GroupsAdmin,
)
from app.api.endpoints.persons import router as router_person
from app.api.endpoints.groups import router as router_group
from app.api.endpoints.access import router as router_access
from app.api.endpoints.users import router as router_user
from app.api.endpoints.tg_users import router as router_tg_users

from app.db.connection import engine
from app.api.services.adminAuth import authentication_backend

app = FastAPI(
    title="Работа с Hikvision",
    version="0.0.1",
    terms_of_service="https://ai-softdev.com",
    contact={
        "name": "AI DEVELOPMENT GENERATION",
        "url": "https://ai-softdev.com",
        "email": "info@ai-softdev.com",
    },
    redoc_url=None,
    root_path="/api/v1",
)

app.include_router(router_person)
app.include_router(router_group)
app.include_router(router_access)
app.include_router(router_user)
app.include_router(router_tg_users)

admin = Admin(
    app, engine, authentication_backend=authentication_backend, base_url="/admin/"
)

admin.add_view(UserAdmin)
admin.add_view(AreasAdmin)
admin.add_view(DevicesAdmin)
admin.add_view(TgUsersAdmin)
admin.add_view(GroupsAdmin)
