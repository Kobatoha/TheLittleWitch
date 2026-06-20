from sqladmin import ModelView

from app.models import Category, Item, User


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.username, User.email, User.is_active, User.created_at]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.created_at]
    form_columns = [User.username, User.email, User.is_active]


class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-folder"

    column_list = [Category.id, Category.name, Category.description]
    column_searchable_list = [Category.name]
    form_columns = [Category.name, Category.description]


class ItemAdmin(ModelView, model=Item):
    name = "Товар"
    name_plural = "Товары"
    icon = "fa-solid fa-box"

    column_list = [
        Item.id,
        Item.name,
        Item.price,
        Item.category,
        Item.is_active,
    ]
    column_searchable_list = [Item.name]
    column_sortable_list = [Item.id, Item.name, Item.price]
    form_columns = [Item.name, Item.description, Item.price, Item.category, Item.is_active]
