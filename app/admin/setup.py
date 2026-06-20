from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import authentication_backend
from app.admin.views import CategoryAdmin, ItemAdmin, UserAdmin
from app.database import engine


def setup_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app,
        engine,
        authentication_backend=authentication_backend,
        title="TLW Admin",
        base_url="/admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(ItemAdmin)

    return admin
